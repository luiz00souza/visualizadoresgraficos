import pandas as pd
from utide import solve, reconstruct
import numpy as np
from scipy.signal import butter, filtfilt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from api_hobo_mare import acesso_API_HOBBO_mare
from datetime import timedelta
import json

def ler_configuracoes(caminho_config):
    with open(caminho_config, "r", encoding="utf-8") as f:
        return json.load(f)

def ler_dados(arquivo):
    df = pd.read_csv(arquivo, sep=r'\s+', header=None, names=["n", "data", "hora", "valor_bruto"], dtype=str)
    df["valor_bruto"] = df["valor_bruto"].astype(float)
    return df

def aplicar_calibracao(df, a, b, redu, height_col):
    df[height_col] = (a * df[height_col] + b - redu).round(3)
    return df

def gerar_timestamps_regulares(df, nome_coluna_tempo):
    df["datetime"] = pd.to_datetime(df[nome_coluna_tempo], format="%Y-%m-%d %H:%M:%S", errors='coerce')    
    intervalo = int((df["datetime"].iloc[1] - df["datetime"].iloc[0]).total_seconds())    
    dt_inicial = df["datetime"].iloc[0]
    df["datetime"] = [dt_inicial + timedelta(seconds=intervalo * i) for i in range(len(df))]
    return df, intervalo

def ajustar_fuso(df, time_col, fuso_horas):
    # df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df["datetime_utc"] = df[time_col] + pd.to_timedelta(fuso_horas, unit='h')
    return df

def suavizacao_matlab_like(df, intervalo):
    if intervalo == 60:
        valores_corrigidos = []
        for i in range(len(df)):
            bloco = df["valor_calibrado"].iloc[max(0, i - 4):i + 1]
            bloco = bloco[bloco >= 0]
            media = bloco.mean() if not bloco.empty else np.nan
            valores_corrigidos.append(media)
        df["valor_corrigido"] = valores_corrigidos
    else:
        df["valor_corrigido"] = df["valor_calibrado"]
    return df

# ========================
# FUNÇÕES AUXILIARES
# ========================

def calcular_metricas(verdadeiro, previsto):
    mae = mean_absolute_error(verdadeiro, previsto)
    rmse = np.sqrt(mean_squared_error(verdadeiro, previsto))
    r2 = r2_score(verdadeiro, previsto)
    mape = np.mean(np.abs((verdadeiro - previsto) / verdadeiro)) * 100
    return mae, rmse, r2, mape

def formatar_dados_temporais(df, time_col, height_col):
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce').round(3)
    # df = df.dropna(subset=[time_col, height_col])
    df = df.sort_values(by=time_col)
    return df

def calcular_intervalo(df, time_col):
    df['delta_t'] = df[time_col].diff().dt.total_seconds()
    avg_delta_t = df['delta_t'].mean()
    df = df.drop(columns=['delta_t'])
    return avg_delta_t


def aplicar_filtro(df, height_col, tipo_filtro, sampling_interval):
    print(f"\n[DEBUG] -> Iniciando aplicar_filtro() para '{height_col}' com tipo '{tipo_filtro}' e sampling_interval={sampling_interval}")

    # --- Verificações básicas ---
    if height_col not in df.columns:
        print(f"[ERRO] Coluna '{height_col}' não encontrada no DataFrame.")
        return pd.Series([np.nan] * len(df), index=df.index)

    dados = df[height_col].values
    n_valid = np.sum(~np.isnan(dados))
    print(f"[DEBUG] Total de amostras: {len(dados)} | Válidas: {n_valid}")

    if n_valid == 0:
        print(f"[AVISO] Todos os valores de '{height_col}' são NaN.")
        return pd.Series([np.nan] * len(df), index=df.index)

    # --- Definição das frequências de corte ---
    Wc_fraco = 0.000224014336917
    Wc_medio = 0.0000224014336917
    tipo_filtro_original = tipo_filtro
    tipo_filtro = tipo_filtro.lower()

    if 'fraco' in tipo_filtro.lower():
        cutoff_freq = Wc_fraco
    elif 'medio' in tipo_filtro.lower() or 'médio' in tipo_filtro.lower():
        cutoff_freq = Wc_medio
    else:
        print(f"[ERRO] Tipo de filtro '{tipo_filtro_original}' inválido. Use 'Fraco' ou 'Médio'.")
        return pd.Series([np.nan] * len(df), index=df.index)

    nyquist_freq = 1 / (2 * sampling_interval)
    normalized_cutoff = cutoff_freq / nyquist_freq

    print(f"[DEBUG] Cutoff freq: {cutoff_freq}")
    print(f"[DEBUG] Nyquist freq: {nyquist_freq}")
    print(f"[DEBUG] Normalized cutoff: {normalized_cutoff}")

    if normalized_cutoff >= 1 or normalized_cutoff <= 0:
        print(f"[ERRO] Normalized cutoff fora do intervalo válido (0–1): {normalized_cutoff}")
        return pd.Series([np.nan] * len(df), index=df.index)

    # --- Construção do filtro ---
    order = 4
    try:
        b, a = butter(order, normalized_cutoff, btype='low', analog=False)
        print(f"[DEBUG] Coeficientes do filtro Butterworth obtidos com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao calcular coeficientes do filtro: {e}")
        return pd.Series([np.nan] * len(df), index=df.index)

    # --- Aplicação do filtro ---
    try:
        # Remove NaN antes de filtrar
        valid_idx = ~np.isnan(dados)
        if np.sum(valid_idx) < 10:
            print(f"[AVISO] Menos de 10 valores válidos. Filtro não aplicado.")
            return pd.Series([np.nan] * len(df), index=df.index)

        dados_validos = dados[valid_idx]

        print(f"[DEBUG] Aplicando filtfilt em {len(dados_validos)} amostras válidas...")
        filtered_valid = filtfilt(b, a, dados_validos)

        # Reconstituir série com NaN nas posições originais
        filtered_data = np.full_like(dados, np.nan, dtype=float)
        filtered_data[valid_idx] = filtered_valid

        print(f"[DEBUG] Filtro aplicado com sucesso. {np.sum(~np.isnan(filtered_data))} valores válidos após filtragem.")

        if np.sum(~np.isnan(filtered_data)) == 0:
            print("[AVISO] Resultado final contém apenas NaN!")

        return pd.Series(filtered_data, index=df.index)

    except Exception as e:
        print(f"[ERRO] Falha ao aplicar o filtro '{tipo_filtro}' em '{height_col}': {e}")
        return pd.Series([np.nan] * len(df), index=df.index)


def encontrar_maior_bloco(df, col, manter_grupo=False):
    if col not in df.columns:
        print(f"[ERRO] Coluna '{col}' não encontrada.")
        return pd.DataFrame(), df
    mask_valid = pd.to_numeric(df[col], errors='coerce').notna()
    if mask_valid.sum() == 0:
        print(f"[AVISO] Nenhum valor numérico válido encontrado na coluna '{col}'.")
        return pd.DataFrame(columns=df.columns), df    
    df = df.copy()
    if 'grupo' in df.columns:
        df = df.drop(columns='grupo')
    df['grupo'] = (mask_valid != mask_valid.shift()).cumsum()
    valid_groups = df.loc[mask_valid, 'grupo']
    if valid_groups.empty:
        print("[AVISO] Nenhum grupo válido identificado.")
        return pd.DataFrame(columns=df.columns), df
    group_sizes_valid = valid_groups.value_counts()
    maior_grupo = group_sizes_valid.idxmax()
    print(f"[INFO] Maior bloco contínuo válido: Grupo {maior_grupo} com {group_sizes_valid.max()} pontos.")
    df_maior_bloco = df[df['grupo'] == maior_grupo].reset_index(drop=True)
    if not manter_grupo:
        df_maior_bloco = df_maior_bloco.drop(columns='grupo')
    return df_maior_bloco




def reindex_time_gaps(df, time_col, avg_delta_t):
    df = df.dropna(subset=[time_col])
    df[time_col] = pd.to_datetime(df[time_col])
    
    full_time_range = pd.date_range(
        start=df[time_col].min(),
        end=df[time_col].max(),
        freq=f"{round(avg_delta_t)}S"
    )
    
    df = df.set_index(time_col).reindex(full_time_range).rename_axis(time_col).reset_index()
    return df
def extrair_componentes(df, latitude, time_col, filtered_col,maior_bloco):
    maior_bloco[time_col] = pd.to_datetime(maior_bloco[time_col], errors='coerce')
    time_dt = np.array(maior_bloco[time_col].dt.to_pydatetime())
    coef = solve(time_dt, maior_bloco[filtered_col].values, lat=latitude, method='ols')
    return coef

def reconstruir_mare(df,time_col, coef):
    df["Altura Prevista"] = reconstruct(pd.to_datetime(df[time_col]), coef)["h"].round(3)
    return df

def preencher_gaps_com_interpolacao_ou_previsao(df, time_col, col_altura):
    col_preenchida = 'Altura Preenchida'
    col_prevista = 'Altura Prevista'

    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')

    # Cria coluna de preenchimento se não existir
    if col_preenchida not in df.columns:
        df[col_preenchida] = df[col_altura].copy()
        print(f"[INFO] Coluna '{col_preenchida}' criada a partir de '{col_altura}'.")

    if col_altura not in df.columns:
        print(f"[ERRO] Coluna '{col_altura}' não encontrada. Nenhum preenchimento será feito.")
        return df

    if col_prevista not in df.columns:
        print(f"[AVISO] Coluna '{col_prevista}' não encontrada. Gaps longos não poderão ser preenchidos com previsão.")

    total_gaps = df[col_altura].isna().sum()
    if total_gaps == 0:
        print(f"[INFO] Nenhum gap encontrado na coluna '{col_altura}'.")
        return df
    else:
        print(f"[INFO] Foram encontrados {total_gaps} gaps na coluna '{col_altura}'.")

    # Identifica blocos contínuos de NaN
    mask_nan = df[col_altura].isna()
    df['grupo'] = (mask_nan != mask_nan.shift()).cumsum()

    for grupo in df['grupo'].unique():
        bloco = df[df['grupo'] == grupo]

        if len(bloco) < 4:
            # Gaps curtos → interpolação usando a coluna de altura original
            df.loc[bloco.index, col_preenchida] = df[col_altura].interpolate(
                method='linear', limit_direction='both'
            ).loc[bloco.index]
            
            media_preenchida = df.loc[bloco.index, col_preenchida].mean()
            print(f"[DEPURAÇÃO] Gap curto interpolado no grupo {grupo} ({len(bloco)} pontos). "
                  f"Média preenchida: {media_preenchida:.3f}. Coluna usada: '{col_altura}'")
        else:
            # Gaps longos → preencher com Altura Prevista + offset
            if bloco[col_altura].isna().all():
                if col_prevista not in df.columns or df[col_prevista].isna().all():
                    print(f"[AVISO] Gap longo no grupo {grupo} ({len(bloco)} pontos) não pôde ser preenchido. "
                          f"'{col_prevista}' não tem valores.")
                    continue

                idx_inicio = bloco.index[0]
                # último valor conhecido antes do bloco
                idx_anterior = idx_inicio - 1
                while idx_anterior not in df.index and idx_anterior > 0:
                    idx_anterior -= 1

                if idx_anterior in df.index and not pd.isna(df.loc[idx_anterior, col_preenchida]):
                    valor_anterior = df.loc[idx_anterior, col_preenchida]
                    valor_previsto_inicio = df.loc[idx_inicio, col_prevista]
                    offset = valor_anterior - valor_previsto_inicio
                    df.loc[bloco.index, col_preenchida] = df.loc[bloco.index, col_prevista] + offset
                    media_preenchida = df.loc[bloco.index, col_preenchida].mean()
                    print(f"[DEPURAÇÃO] Gap longo preenchido no grupo {grupo} ({len(bloco)} pontos) "
                          f"com offset {offset:.3f}. Média preenchida: {media_preenchida:.3f}. Coluna usada: '{col_prevista}'")
                else:
                    # Sem valor anterior conhecido, preenche direto com previsto
                    df.loc[bloco.index, col_preenchida] = df.loc[bloco.index, col_prevista]
                    media_preenchida = df.loc[bloco.index, col_preenchida].mean()
                    print(f"[DEPURAÇÃO] Gap longo preenchido no grupo {grupo} ({len(bloco)} pontos) sem offset "
                          f"(sem valor anterior). Média preenchida: {media_preenchida:.3f}. Coluna usada: '{col_prevista}'")

    df.drop(columns=['grupo'], inplace=True, errors='ignore')
    print(f"[OK] Preenchimento concluído para '{col_preenchida}'.")
    return df
def suavizar_transicao(df, col_preenchida, flag_origem, window=3):
    """
    Retorna a coluna suavizada com transições leves entre medido e previsto.
    """
    df_copy = df.copy()
    alt_final = df_copy[col_preenchida].copy()
    
    transicoes = df_copy.index[df_copy[flag_origem] != df_copy[flag_origem].shift()]
    
    for idx in transicoes:
        start = max(0, idx - window//2)
        end = min(len(df_copy), idx + window//2 + 1)
        alt_final[start:end] = alt_final[start:end].rolling(
            window=min(window, end-start), center=True, min_periods=1
        ).mean()
    
    return alt_final

def preencher_gaps_com_previsao(df, time_col, col_altura, col_prevista):
    """
    Preenche grandes gaps (blocos longos de NaN) usando dados previstos,
    aplicando offset entre o último valor conhecido e o início do gap.
    """
    col_preenchida = 'Altura Preenchida'
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')

    if col_altura not in df.columns:
        print(f"[ERRO] Coluna '{col_altura}' não encontrada.")
        return df

    if col_prevista not in df.columns:
        print(f"[AVISO] Coluna '{col_prevista}' não encontrada. Nenhum preenchimento será feito.")
        return df

    if col_preenchida not in df.columns:
        df[col_preenchida] = df[col_altura].copy()
        print(f"[INFO] Coluna '{col_preenchida}' criada a partir de '{col_altura}'.")

    mask_nan = df[col_altura].isna()
    df['grupo'] = (mask_nan != mask_nan.shift()).cumsum()

    total_previstos = 0
    for grupo in df['grupo'].unique():
        bloco = df[df['grupo'] == grupo]

        # Só atua sobre gaps longos
        if len(bloco) >= 4 and bloco[col_altura].isna().all():
            idx_inicio = bloco.index[0]
            idx_anterior = idx_inicio - 1
            while idx_anterior not in df.index and idx_anterior > 0:
                idx_anterior -= 1

            if idx_anterior in df.index and not pd.isna(df.loc[idx_anterior, col_preenchida]):
                valor_anterior = df.loc[idx_anterior, col_preenchida]
                valor_previsto_inicio = df.loc[idx_inicio, col_prevista]
                offset = valor_anterior - valor_previsto_inicio
                df.loc[bloco.index, col_preenchida] = df.loc[bloco.index, col_prevista] + offset
                media_preenchida = df.loc[bloco.index, col_preenchida].mean()
                print(f"[DEPURAÇÃO] Gap longo ({len(bloco)} pts) preenchido com offset {offset:.3f}. "
                      f"Média: {media_preenchida:.3f}")
            else:
                df.loc[bloco.index, col_preenchida] = df.loc[bloco.index, col_prevista]
                media_preenchida = df.loc[bloco.index, col_preenchida].mean()
                print(f"[DEPURAÇÃO] Gap longo ({len(bloco)} pts) preenchido sem offset. "
                      f"Média: {media_preenchida:.3f}")

            total_previstos += len(bloco)

    df.drop(columns=['grupo'], inplace=True, errors='ignore')
    print(f"[OK] {total_previstos} pontos preenchidos com previsão.")
    return df

def preencher_gaps_com_interpolacao(df, time_col, col_altura):
    """
    Preenche pequenos gaps (blocos curtos de NaN) usando interpolação linear.
    """
    col_preenchida = 'Altura Preenchida'
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')

    if col_altura not in df.columns:
        print(f"[ERRO] Coluna '{col_altura}' não encontrada.")
        return df

    if col_preenchida not in df.columns:
        df[col_preenchida] = df[col_altura].copy()
        print(f"[INFO] Coluna '{col_preenchida}' criada a partir de '{col_altura}'.")

    mask_nan = df[col_altura].isna()
    df['grupo'] = (mask_nan != mask_nan.shift()).cumsum()

    total_interpolados = 0
    for grupo in df['grupo'].unique():
        bloco = df[df['grupo'] == grupo]
        if len(bloco) < 4 and bloco[col_altura].isna().any():  # apenas gaps curtos
            df.loc[bloco.index, col_preenchida] = df[col_altura].interpolate(
                method='linear', limit_direction='both'
            ).loc[bloco.index]
            total_interpolados += len(bloco)
            media_preenchida = df.loc[bloco.index, col_preenchida].mean()
            print(f"[DEPURAÇÃO] Gap curto interpolado no grupo {grupo} ({len(bloco)} pts). "
                  f"Média: {media_preenchida:.3f}")

    # df.drop(columns=['grupo'], inplace=True, errors='ignore')
    print(f"[OK] {total_interpolados} pontos preenchidos por interpolação.")
    return df




def calcular_residuos(df, height_col):
    if height_col not in df.columns:
        df["Resíduo"] = 0
        return df
    if df[height_col].isna().all():
        df["Resíduo"] = 0
        return df
    df["Resíduo"] = df[height_col] - df["Altura Prevista"]
    df["Resíduo"] = df["Resíduo"].fillna(0)
    return df

def gerar_previsao(df, coef, avg_delta_t, time_col,forecast_days):
    time_forecast = pd.date_range(
        start=df[time_col].max(),
        periods=int(forecast_days * 24 * 3600 / avg_delta_t),
        freq=f"{int(avg_delta_t)}S"
    )
    reconstruction_forecast = reconstruct(time_forecast.to_pydatetime(), coef)
    return pd.DataFrame({
        time_col: time_forecast,
        "Altura Prevista": reconstruction_forecast['h'].round(3)
    })

# coloque isto no fim do arquivo, substituindo a seção de "CONFIGURAÇÕES INICIAIS" e "EXECUÇÃO"

def run_pipeline(caminho_config_path=None, forecast_days=4, max_now_override=None):
    """
    Executa o pipeline de maré. 
    Se caminho_config_path for None, usa o path embutido (ou levante erro).
    max_now_override: opcional -- usar uma datetime para 'now' (útil pra testes).
    Retorna df_ajustado_extended, forecast_df (ou o que você quiser).
    """
    # Config
    if caminho_config_path is None:
        caminho_config_path = r"C:\Users\campo\Desktop\tide_forecast_realtime_v003\config_mare_cosipa.json"
    config = ler_configuracoes(caminho_config_path)
    arquivo = config.get("arquivo")
    a = config.get("a")
    b = config.get("b")
    redu = config.get("reducao")
    fuso = config.get("fuso", "").lower()
    filtro = config.get("filtro", "").lower()
    local = config.get("local", "").replace(" ", "_")
    projeto = config.get("projeto", "").replace(" ", "_")
    saida = config.get("saida")
    parameter_columns_mare = config.get("parameter_columns_mare")
    start_time = config.get("start_time")
    logger_ids = config.get("logger_ids")

    time_col = config.get("time_col")
    height_col = config.get("height_col")
    latitude = config.get("latitude")
    tipo_de_filtro = config.get("tipo_de_filtro")
    avg_delta_t = config.get("avg_delta_t")
    fuso_horas = config.get("fuso_horas")

    # 1 - obter dados (cuidado: chamada externa)
    print("1️⃣ INÍCIO: Obtendo dados da API HOBO...")
    df_tide, parameter_info = acesso_API_HOBBO_mare(
        parameter_columns_mare=parameter_columns_mare,
        start=start_time,
        logger_ids=logger_ids
    )
    print(f"✅ Dados carregados: {df_tide.shape[0]} linhas\n")

    # 2 - pré-processamento
    print("2️⃣ Pré-processamento dos dados...")
    df_tide = formatar_dados_temporais(df_tide.copy(), time_col, height_col)
    df_tide = aplicar_calibracao(df_tide, a, b, redu, height_col)
    print("✅ Pré-processamento concluído\n")

    # 3 - filtros
    print("3️⃣ Aplicando filtros...")
    df_tide['Filtro Fraco'] = aplicar_filtro(df_tide, height_col, 'Fraco', sampling_interval=avg_delta_t)
    df_tide['Filtro Médio'] = aplicar_filtro(df_tide, height_col, 'Médio', sampling_interval=avg_delta_t)
    print("✅ Filtros aplicados\n")

    # remover data específica (se necessário)
    df_tide = df_tide[~((df_tide[time_col].dt.year == 2025) &
                        (df_tide[time_col].dt.month == 5) &
                        (df_tide[time_col].dt.day == 6))]
    print("✅ Dados do dia 2025-05-06 removidos!")

    # 4 - extrair componentes
    print("4️⃣ Extraindo componentes harmônicas...")
    df_ajustado = reindex_time_gaps(df_tide, time_col, avg_delta_t)
    maior_bloco = encontrar_maior_bloco(df_ajustado.reset_index(), tipo_de_filtro)
    coef = extrair_componentes(df_ajustado.reset_index(), latitude, time_col, tipo_de_filtro, maior_bloco)
    print("✅ Componentes extraídas\n")

    # 5 - reconstrução e resíduos
    print("5️⃣ Reconstruindo gaps e calculando resíduos...")
    df_ajustado = reconstruir_mare(df_ajustado, time_col, coef)
    df_ajustado = calcular_residuos(df_ajustado, height_col)
    df_ajustado["Altura Preenchida"] = df_ajustado[tipo_de_filtro].combine_first(df_ajustado["Altura Prevista"])
    df_ajustado = preencher_gaps_com_interpolacao_ou_previsao(df_ajustado, time_col, height_col)
    print("✅ Reconstrução e preenchimento concluídos\n")

    # 7 - extensão em tempo real / previsão
    print("7️⃣ Extensão em tempo real...")
    min_index = df_ajustado[time_col].min()
    max_index = pd.to_datetime("now") if max_now_override is None else pd.to_datetime(max_now_override)
    forecast_df = gerar_previsao(df_ajustado, coef, avg_delta_t, time_col, forecast_days)
    forecast_df[time_col] = pd.to_datetime(forecast_df[time_col])
    forecast_df = forecast_df[forecast_df[time_col] <= max_index]
    timestamps_5min = pd.date_range(start=min_index, end=max_index, freq='5T')
    df_ajustado_extended = df_ajustado.set_index(time_col).reindex(timestamps_5min)
    forecast_df_reindexed = forecast_df.set_index(time_col).reindex(df_ajustado_extended.index)
    df_ajustado_extended["Altura Final"] = df_ajustado_extended["Altura Preenchida"].combine_first(forecast_df_reindexed["Altura Prevista"])
    print("✅ Extensão em tempo real concluída\n")

    # classificações finais e retorno
    df_ajustado_extended = df_ajustado_extended.reset_index().rename(columns={"index": time_col})
    df_ajustado_extended["Tipo_de_Filtro"] = f"{tipo_de_filtro}_{height_col}"
    df_ajustado_extended["Flag_origem"] = np.where(
        df_ajustado_extended["Altura Preenchida"] == df_ajustado_extended[height_col],
        "Dado medido", "Dado previsto"
    )
    df_ajustado_extended = ajustar_fuso(df_ajustado_extended, time_col, fuso_horas)
    print("✅ Pipeline finalizado")

    return df_ajustado_extended, forecast_df

if __name__ == "__main__":
    # quando executado diretamente, roda com o config embutido
    run_pipeline()


# #%%
# import streamlit as st
# import plotly.express as px

# st.subheader("Maré Original vs Filtros")
# fig1 = px.line(
#     df_ajustado_extended,
#     x=time_col,
#     y=[height_col, "Filtro Fraco", "Filtro Médio"],
#     labels={time_col: "Tempo", "value": "Altura da Maré"},
#     title="Dados Reais e Filtrados"
# )
# st.plotly_chart(fig1)
# st.subheader("Maré Observada vs Preenchida e Prevista")
# fig2 = px.line(
#     df_ajustado_extended,
#     x=time_col,
#     y=[height_col, "Altura Preenchida", "Altura Final"],
#     labels={time_col: "Tempo", "value": "Altura da Maré"},
#     title="Maré Observada x Preenchida x Prevista"
# )
# st.plotly_chart(fig2)
# st.subheader("Resíduos da Maré")
# residuos_para_grafico = df_ajustado_extended["Resíduo"].fillna(0)
# fig3 = px.line(
#     df_ajustado_extended,
#     x=time_col,
#     y=residuos_para_grafico,
#     labels={time_col: "Tempo", "y": "Altura Residual"},  # 'y' é usado pois passamos a série diretamente
#     title="Resíduos Observado - Previsto"
# )

# st.plotly_chart(fig3)
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from scipy.signal import find_peaks

# # Série de previsão
# mare = forecast_df["Altura Prevista"]

# # Encontrar picos (maré cheia) e vales (maré vazante)
# picos, _ = find_peaks(mare)
# vales, _ = find_peaks(-mare)

# # Criar DataFrame unificado
# df_picos_vales = pd.DataFrame({
#     "Horário": pd.concat([forecast_df.iloc[picos][time_col], forecast_df.iloc[vales][time_col]]),
#     "Tipo": ["Cheia"]*len(picos) + ["Vazante"]*len(vales)
# }).sort_values("Horário").reset_index(drop=True)

# # Criar coluna só com a data
# df_picos_vales["Data"] = df_picos_vales["Horário"].dt.date

# # Gráfico da previsão
# st.subheader("Previsão de Maré")
# fig = px.line(
#     forecast_df,
#     x=time_col,
#     y="Altura Prevista",
#     labels={time_col: "Tempo", "Altura Prevista": "Altura da Maré"},
#     title="Previsão de Maré"
# )
# st.plotly_chart(fig)

# # Cards agrupados por dia
# st.subheader("Horários Previsto de Picos de Maré")
# for data, group in df_picos_vales.groupby("Data"):
#     st.markdown(f"### 📅 {data}")  # Título com a data
#     for _, row in group.iterrows():
#         seta = "🟢🔺" if row["Tipo"] == "Cheia" else "🔴🔻"
#         st.write(f"{row['Horário'].strftime('%H:%M')} {seta}")
