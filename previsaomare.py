import streamlit as st
import pandas as pd
import plotly.express as px
from utide import solve, reconstruct
import numpy as np
from scipy.signal import butter, filtfilt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from dateutil.relativedelta import relativedelta
componentes_ordenadas = [
    'M2', 'S2', 'O1', 'N2', 'K1', 'MM', 'L2', 'MU2', 'Q1', 'MSF',
    'M3', 'SK3', '2Q1', 'ETA2', 'EPS2', 'OO1', 'NO1', 'MS4', 'M4',
    'MN4', 'ALP1', 'J1', 'SN4', 'MK3', 'UPS1', 'MO3', 'S4', 'M6',
    '2SK5', '2MS6', '2SM6', '2MK5', '3MK7', '2MN6', 'M8'
]

tipo_de_filtro="Médio"#Fraco


def carregar_e_processar_csv(df, time_col, height_col):
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col, height_col])
    df = df.sort_values(by=time_col)
    return df

def calcular_metricas(verdadeiro, previsto):
    mae = mean_absolute_error(verdadeiro, previsto)
    rmse = np.sqrt(mean_squared_error(verdadeiro, previsto))
    r2 = r2_score(verdadeiro, previsto)
    mape = np.mean(np.abs((verdadeiro - previsto) / verdadeiro)) * 100
    return mae, rmse, r2, mape


def aplicar_filtro(df, height_col, tipo_filtro, sampling_interval):
    Wc_fraco = 0.000224014336917  # Hz
    Wc_medio = 0.0000224014336917  # Hz
    tipo_filtro = tipo_filtro.lower()
    if tipo_filtro == 'fraco':
        cutoff_freq = Wc_fraco
    elif tipo_filtro == 'médio':
        cutoff_freq = Wc_medio
    else:
        raise ValueError("Tipo de filtro inválido. Escolha 'Fraco' ou 'Médio'.")
    nyquist_freq = 1 / (2 * sampling_interval)
    normalized_cutoff = cutoff_freq / nyquist_freq
    if not (0 < normalized_cutoff < 1):
        raise ValueError(
            f"Erro: frequência de corte normalizada ({normalized_cutoff}) "
            f"deve estar entre 0 e 1. Verifique o intervalo de amostragem."
        )
    order = 4
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)   
    
    original = df[height_col].values
    n_total = len(original)
    n_preservar = 15
    if n_total <= n_preservar + 1:
        raise ValueError("Série muito curta para aplicar filtro e preservar os últimos 15 pontos.")

    n_filtrar = n_total - n_preservar
    dados_filtrar = original[:n_filtrar]
    padlen = 4 * max(len(a), len(b))
    padlen = min(padlen, len(dados_filtrar) - 1)
    start_pad = dados_filtrar[1:padlen+1][::-1]
    end_pad = dados_filtrar[-padlen-1:-1][::-1]
    padded = np.concatenate([start_pad, dados_filtrar, end_pad])
    filtered_padded = filtfilt(b, a, padded)
    filtered_data = filtered_padded[padlen:-padlen]
    final_data = np.concatenate([filtered_data, original[-n_preservar:]])

    return final_data

def reindex_time_gaps(df,time_col, avg_delta_t):
    coluna_tempo=time_col
    time_col = pd.to_datetime(df[coluna_tempo], errors='coerce')
    df[coluna_tempo] = time_col 
    df = df.dropna(subset=[coluna_tempo])
    freq = f"{round(avg_delta_t)}S"  # Frequência em segundos
    df = df.set_index(coluna_tempo)
    full_time_range = pd.date_range(
        start=df.index.min(), 
        end=df.index.max()+ relativedelta(days=3), 
        freq=freq
        )
    df = df.reindex(full_time_range)
    df.index.name = coluna_tempo
    return df

def extrair_componentes(df, latitude, time_col, filtered_col):
    maior_bloco = encontrar_maior_bloco(df, filtered_col)
    maior_bloco[time_col] = pd.to_datetime(maior_bloco[time_col], errors='coerce')
    time_dt = maior_bloco[time_col].dt.to_pydatetime()
    # coef = solve(time_dt, maior_bloco[filtered_col].values, lat=latitude, method='ols')
    coef = solve(time_dt, maior_bloco[filtered_col], lat=latitude, method='ols', constit=componentes_ordenadas)

    return coef
def encontrar_maior_bloco(df, col):
    mask_valid = df[col].notna()
    df['grupo'] = (mask_valid != mask_valid.shift()).cumsum()
    valid_groups = df.loc[mask_valid, 'grupo']
    group_sizes = valid_groups.value_counts()
    maior_grupo = group_sizes.idxmax()
    df_maior_bloco = df[df['grupo'] == maior_grupo].drop(columns='grupo')
    return df_maior_bloco

def ajustar_offset_gaps(df, time_col, height_col, predicted_col):
    mask_nan = df['Filtro Médio'].isna()
    df['grupo'] = (mask_nan != mask_nan.shift()).cumsum()  # Agrupar por regiões contínuas de NaN
    for grupo in df['grupo'].unique():
        bloco = df[df['grupo'] == grupo]
        #TRIAGEM INTELIGENTE, PARA GAPS MAIOR MENORES OU MAIORES DE 4 DADOS
        if len(bloco) < 4:
            df.loc[bloco.index, 'Altura Preenchida Filtro Médio'] = np.nan  # Definir os valores como NaN
            df.loc[bloco.index, 'Altura Preenchida Filtro Médio'] = df['Altura Preenchida Filtro Médio'].interpolate(method='linear', limit_direction='both')
        else:
            if bloco[height_col].isna().all():
                idx_inicio = bloco.index[0]
                idx_fim = bloco.index[0] - pd.Timedelta(seconds=300)
                if idx_inicio in df.index and idx_fim in df.index:
                    altura_fim = df.loc[idx_fim, height_col]
                    previsao_inicio = df.loc[idx_inicio, predicted_col]    
                    offset = altura_fim - previsao_inicio
                    # offset=0
                    df.loc[bloco.index, predicted_col] += offset
    return df
def gerar_previsao(df, coef, avg_delta_t, time_col,tipo_de_filtro):
    df[time_col] = df.index.to_pydatetime()
    forecast_days = 365
    time_forecast = pd.date_range(
        start=df[time_col].max(),
        periods=int(forecast_days * 24 * 3600 / avg_delta_t),
        freq=f"{int(avg_delta_t)}S"
    )
    reconstruction_forecast = reconstruct(time_forecast.to_pydatetime(), coef)
    return pd.DataFrame({
        "Tempo": time_forecast,
        f"Altura Prevista Filtro {tipo_de_filtro}": reconstruction_forecast['h']
    })

def reconstruir_mare(df, time_col, coef,tipo_de_filtro):
    time_dt = df.index.to_pydatetime()
    reconstruction_obs = reconstruct(time_dt, coef)
    df[f"Altura Prevista Filtro Médio"] = reconstruction_obs['h']
    return df

#%%FUNCOES VISUAIS STREAMLIT
def grafico_original(df, time_col, height_col):
    fig = px.line(
        df, 
        x=time_col, 
        y=height_col, 
        labels={time_col: "Tempo", height_col: "Altura da Maré"},
        title="Altura da Maré Original",
)
    st.plotly_chart(fig)
def grafico_comparativo(df, time_col, height_col, filtered_data_weak, filtered_data_medium,tipo_de_filtro):
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')

    fig_filtered = px.line(
        df, 
        x=time_col, 
        y=[height_col, 'Filtro Fraco', 'Filtro Médio'],
        labels={time_col: "Tempo", "value": "Altura da Maré"},
        title="Comparação: Dados Reais vs Filtros (Fraco e Médio)"
    )
    st.plotly_chart(fig_filtered)
    # fig_comparison = px.line(
    #     df, 
    #     x=time_col, 
    #     y=[height_col, f"Altura Prevista Filtro {tipo_de_filtro}",f"Altura Preenchida Filtro {tipo_de_filtro}"],
    #     labels={time_col: "Tempo", "value": "Altura da Maré"},
    #     title="Maré Observada vs Prevista"
    # )
    # st.plotly_chart(fig_comparison)
    st.subheader("📋 Tabela de Tamanhos das Colunas")
    col_sizes = pd.DataFrame({
        "Coluna": df.columns,
        "Valores Válidos": [df[col].notna().sum() for col in df.columns],
        "Total": len(df)
    })
    st.dataframe(col_sizes)
    col2 = f"Altura Prevista Filtro {tipo_de_filtro}"
    col3 = f"Altura Preenchida Filtro {tipo_de_filtro}"
    
    # Garante que a coluna de tempo está no formato datetime
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col])
    
    # Verifica quais colunas estão presentes
    colunas_existentes = [col for col in [height_col, col2, col3] if col in df.columns]
    
    if len(colunas_existentes) < 2:
        st.warning("⚠️ Não há colunas suficientes para plotar.")
        return
    
    # Constrói DataFrame no formato longo (long format)
    df_plot = df[[time_col] + colunas_existentes].copy()
    df_melt = df_plot.melt(id_vars=[time_col], 
                           value_vars=colunas_existentes,
                           var_name="Série", 
                           value_name="Altura")
    
    # Agora mesmo com tamanhos diferentes ou NaNs, o plotly vai funcionar
    fig = px.line(df_melt, x=time_col, y="Altura", color="Série",
                  title="Maré Observada, Prevista e Preenchida",
                  labels={time_col: "Tempo", "Altura": "Altura da Maré"})
    
    st.plotly_chart(fig, use_container_width=True)


def grafico_residuos(df, time_col):
    fig_residuals = px.line(
        df, 
        x=time_col, 
        y="Resíduo",
        labels={time_col: "Tempo", "Resíduo": "Altura Residual"},
        title="Resíduos da Maré"
    )
    st.plotly_chart(fig_residuals)
def exibir_componentes(coef,tipo_de_filtro):
    st.write(f"Componentes Harmônicas Extraídas:({tipo_de_filtro})")
    st.dataframe(pd.DataFrame({
        "Constituente": coef['name'],
        "Amplitude (m)": coef['A'],
        "Fase (°)": coef['g']
    }))
def grafico_previsao(forecast_df,tipo_de_filtro):
    fig_forecast = px.line(
        forecast_df, 
        x="Tempo", 
        y=f"Altura Prevista Filtro {tipo_de_filtro}",
        title="Previsão de Maré para 1 Ano",
        labels={"Tempo": "Tempo", "Altura Prevista Filtro Médio": "Altura da Maré"}
    )
    st.plotly_chart(fig_forecast)

def download_dados(df, forecast_df):
    st.download_button(
        label="Baixar Dados (CSV com previsão e resíduos)",
        data=df.to_csv(index=False),
        file_name="dados_mare_com_residuos.csv",
        mime="text/csv"
    )
    st.download_button(
        label="Baixar Previsão (1 Ano, CSV)",
        data=forecast_df.to_csv(index=False),
        file_name="previsao_mare_1_ano.csv",
        mime="text/csv"
    )

def streamlituploadautomatico(df_tide,time_col ,height_col, latitude,tipo_de_filtro,avg_delta_t):
    st.title("Processamento e Análise de Séries Temporais")
    # 1. Carregamento e pré-processamento
    df = df_tide
    df = carregar_e_processar_csv(df, time_col, height_col)

    # 2. Filtros nos dados brutos (opcional, para comparação)
    filtered_data_medium = aplicar_filtro(df, height_col, 'Médio', sampling_interval=600)
    filtered_data_weak = aplicar_filtro(df, height_col, 'Fraco', sampling_interval=600)

    df['Filtro Fraco'] = filtered_data_weak
    df['Filtro Médio'] = filtered_data_medium
    
    # 3. Bloco contínuo para extração harmônica
    maior_bloco = encontrar_maior_bloco(df, tipo_de_filtro)
    df = reindex_time_gaps(df, time_col,avg_delta_t)
    coef = extrair_componentes(maior_bloco, latitude, time_col=time_col, filtered_col=tipo_de_filtro)
    df = reconstruir_mare(df, time_col, coef,tipo_de_filtro)

    # 4. Cálculo do resíduo (opcional, para avaliação)
    df["Resíduo"] = df[height_col] - df["Altura Prevista Filtro Médio"]
    df["Resíduo Médio"] = df[height_col] - df["Altura Prevista Filtro Médio"]
    # df["Resíduo Fraco"] = df[height_col] - df["Altura Prevista Filtro Fraco"]

    # 5. Previsão futura
    forecast_df = gerar_previsao(df, coef, avg_delta_t, time_col,tipo_de_filtro)

    # 6. Combina altura observada com previsão para preencher falhas+3 dias de previsao
    df["Altura Preenchida Filtro Médio"] = df[height_col].combine_first(df["Altura Prevista Filtro Médio"])
    # df["Altura Preenchida Fraco"] = df[height_col].combine_first(df["Altura Prevista Filtro Médio"])

    df_ajustado = ajustar_offset_gaps(df, time_col=time_col,height_col=height_col,predicted_col='Altura Preenchida Filtro Médio')
    
    
    #7 Aplica filtro aos dados preenchidos    
    df["Altura Preenchida Filtro Médio"] = aplicar_filtro(df, "Altura Preenchida Filtro Médio", 'Médio', sampling_interval=600)
    # df["Altura Preenchida Fraco"] = aplicar_filtro(df, "Altura Preenchida Fraco", 'Fraco', sampling_interval=600)

    #EXIBICAO NO STREAMLIT
    st.dataframe(df_ajustado)  # Mostra as primeiras 5 linhas
    grafico_original(df, time_col, height_col)
    grafico_comparativo(df_ajustado, time_col, height_col, filtered_data_weak, filtered_data_medium, tipo_de_filtro)
    exibir_componentes(coef, tipo_de_filtro)
    df_clean = df[[tipo_de_filtro, "Altura Prevista Filtro Médio"]].dropna()
    mae_utide, rmse_utide, r2_utide, mape_utide = calcular_metricas(df_clean[tipo_de_filtro], df_clean["Altura Prevista Filtro Médio"])

    st.write("### Avaliação dos Modelos")
    st.write(f"**UTIDE:** MAE = {mae_utide:.4f}, RMSE = {rmse_utide:.4f}, R² = {r2_utide:.4f}, MAPE = {mape_utide:.2f}%")
    st.title("Tabela de Dados")

    st.dataframe(df_ajustado.head())  # Mostra as primeiras 5 linhas
    grafico_residuos(df_ajustado, time_col)
    grafico_previsao(forecast_df,tipo_de_filtro)
    download_dados(df_ajustado, forecast_df)
    tid_content = df_ajustado.to_csv(index=False, sep="\t")  # Converte para formato tabulado

    st.download_button(
        label="Baixar Arquivo .tid",
        data=tid_content,
        file_name="dados_processados.tid",
        mime="text/plain"
    )
def streamlituploadmanual():
    st.title("Processamento e Análise de Séries Temporais")
    st.write(""" Carregue um arquivo CSV""")
    uploaded_file = st.file_uploader("Carregue o arquivo CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("Selecione as colunas:")
        time_col = st.selectbox("Selecione a coluna do tempo:", df.columns, key="time_col")
        height_col = st.selectbox("Selecione a coluna da altura:", df.columns, key="height_col")
        if time_col and height_col:
            st.success(f"Colunas selecionadas: Tempo = '{time_col}', Altura = '{height_col}'")
            tipo_filtro = st.selectbox(
                "Selecione o tipo de filtro que deseja aplicar:",
                options=[f'{height_col}', "Filtro Fraco", "Filtro Médio"],
                index=0  # Default: "Sem Filtro"
            )
            filtro_selecionado = st.radio(
                "Escolha o tipo de filtro a ser aplicado:",
                (f'{height_col}', "Filtro Fraco", "Filtro Médio"),
            )
            latitude = st.number_input(r"Insira a latitude do local (exemplo: -21 para o Vitória/ES)", 
                               min_value=-90.0, max_value=90.0, value=-21.0, step=0.1)
    
            # Habilitar botão somente após seleção do filtro
            if filtro_selecionado:
                if st.button("Processar Dados"):
                    with st.spinner("Processando os dados..."):
                        df = carregar_e_processar_csv(df, time_col, height_col)
                        tipo_de_filtro='Filtro Médio'
                        tipo_de_filtro=filtro_selecionado
                        avg_delta_t = 300
                        filtered_data_weak = aplicar_filtro(df, height_col, 'Fraco', sampling_interval=600)
                        filtered_data_medium = aplicar_filtro(df, height_col, 'Médio', sampling_interval=600)
                        df['Filtro Fraco'] = filtered_data_weak
                        df['Filtro Médio'] = filtered_data_medium
                        maior_bloco = encontrar_maior_bloco(df, tipo_de_filtro)
                        df = reindex_time_gaps(df, time_col,avg_delta_t)
                        coef = extrair_componentes(maior_bloco, latitude,time_col=time_col, filtered_col=tipo_de_filtro)
                        df = reconstruir_mare(df, time_col, coef,tipo_de_filtro)
                        df["Resíduo"] = df[height_col] - df["Altura Prevista Filtro Fraco"]
                        df["Resíduo"] = df[height_col] - df["Altura Prevista Filtro Médio"]

                        forecast_df = gerar_previsao(df, coef, avg_delta_t, time_col,tipo_de_filtro)
                        df["Altura Preenchida Filtro Fraco"] = df[height_col].combine_first(df["Altura Prevista Filtro Fraco"])
                        df["Altura Preenchida Filtro Médio"] = df[height_col].combine_first(df["Altura Prevista Filtro Médio"])

                        df_ajustado = ajustar_offset_gaps(df, time_col=time_col, 
                                                          height_col=height_col,
                                                          predicted_col='Altura Preenchida Filtro Médio')
                        grafico_original(df, time_col, height_col)
                        grafico_comparativo(df_ajustado, time_col, height_col, filtered_data_weak, filtered_data_medium,tipo_de_filtro)
                        exibir_componentes(coef, tipo_de_filtro)
                        st.title("Tabela de Dados")
                        st.dataframe(df_ajustado.head())  # Mostra as primeiras 5 linhas                        
                        grafico_residuos(df_ajustado, time_col)
                        
                        grafico_previsao(forecast_df,tipo_de_filtro)
                        download_dados(df_ajustado, forecast_df)
                        tid_content = df_ajustado.to_csv(index=False, sep="\t")  # Converte para formato tabulado
                        st.download_button(
                            label="Baixar Arquivo .tid",
                            data=tid_content,
                            file_name="dados_processados.tid",
                            mime="text/plain"
                        )
# streamlituploadautomatico(df_tide,time_col = 'GMT-03:00',height_col = 'Pressure_S1', latitude =-21,tipo_de_filtro='Filtro Fraco',avg_delta_t = 300)# UTILIZAR PARA ARQUIVO PREDEFINIDO COM CONFIGURACOES PREDEFINIDAS
# streamlituploadmanual()# UTILIZAR PARA PREVISOES RAPIDAS, REALIZANDO O UPLOAD DE QUALQUER ARQUIVO CSV