import pandas as pd
import numpy as np

from suprememare import (
    ler_configuracoes,
    acesso_API_HOBBO_mare,
    formatar_dados_temporais,
    aplicar_calibracao,
    aplicar_filtro,
    reindex_time_gaps,
    encontrar_maior_bloco,
    extrair_componentes,
    reconstruir_mare,
    calcular_residuos,
    preencher_gaps_com_interpolacao,
    preencher_gaps_com_previsao,
    gerar_previsao,
    suavizar_transicao,
    ajustar_fuso
)


def preencher_gaps_com_redundancia(df, sensor_principal, sensor_redundante, coluna_saida="Altura Preenchida"):
    """
    Preenche gaps usando sensor redundante, se ele existir.
    """
    if sensor_redundante and sensor_redundante in df.columns:
        df[coluna_saida] = df[sensor_principal].combine_first(df[sensor_redundante]).round(3)
    else:
        # Se não houver redundância, apenas copia o sensor principal
        df[coluna_saida] = df[sensor_principal].round(3)
    return df

def calibrar_sensores(df, height_col_principal, height_col_redundancia, a, b, reducao):
    if height_col_principal in df.columns:
        df = aplicar_calibracao(df, a, b, reducao, height_col_principal)
    else:
        print(f"[ERRO] Coluna do sensor principal '{height_col_principal}' não encontrada no DataFrame!")
    if height_col_redundancia and height_col_redundancia in df.columns:
        df = aplicar_calibracao(df, a, b, reducao, height_col_redundancia)
    else:
        print(f"[AVISO] Nenhum sensor redundante encontrado ou coluna '{height_col_redundancia}' ausente.")
    return df
def aplicar_filtro_final(df, col_principal, tipo_filtro, sampling_interval):
    """
    Aplica o(s) filtro(s) diretamente na coluna 'Altura Final'.
    
    Parâmetros:
        df: DataFrame
        col_principal: coluna de entrada para o filtro
        tipo_filtro: string ou lista de strings com os filtros a aplicar
        sampling_interval: intervalo de amostragem usado no filtro
    
    Retorna:
        df com a coluna 'Altura Final' atualizada
    """
    # Se for string, converte para lista
    if isinstance(tipo_filtro, str):
        tipos_filtro = [tipo_filtro]
    else:
        tipos_filtro = tipo_filtro

    # Começa com os dados originais da coluna principal
    df['Altura Final'] = df[col_principal]

    # Aplica cada filtro sequencialmente
    for filtro in tipos_filtro:
        df['Altura Final'] = aplicar_filtro(df, 'Altura Final', filtro, sampling_interval).round(3)

    print("DADOS FILTRADOS NA COLUNA 'Altura Final'")
    return df

def aplicar_filtros_suavizacao(df, col_principal, col_redundancia, tipos_filtro, sampling_interval):
    for filtro in tipos_filtro:
        # Aplica filtro na coluna principal
        df[f'Filtro {filtro} {col_principal}'] = aplicar_filtro(
            df, col_principal, filtro, sampling_interval
        ).round(3)

        # Aplica filtro na coluna redundante apenas se ela existir
        if col_redundancia and col_redundancia in df.columns:
            df[f'Filtro {filtro} {col_redundancia}'] = aplicar_filtro(
                df, col_redundancia, filtro, sampling_interval
            ).round(3)

    print("DADOS FILTRADOS")
    return df


def processar_mare_com_redundancia(df_tide, time_col, height_col_principal, height_col_redundancia,
                                   tipo_de_filtro, avg_delta_t, forecast_days, parameter_columns_mare,
                                   start, logger_ids, a, b, reducao, latitude, fuso, ativar_preenchimento_gaps=True):
    df = df_tide
    flag_columns = [f"Flag_{col}" for col in parameter_columns_mare]
    df_flag0 = df[(df[flag_columns] != 4).all(axis=1)]
    df_flag4 = df[(df[flag_columns] == 4).any(axis=1)]

    df_suavizado = aplicar_filtros_suavizacao(df_flag0, height_col_principal, height_col_redundancia,
                                              tipos_filtro=['Fraco', 'Medio'], sampling_interval=avg_delta_t)
    df_reindex = reindex_time_gaps(df_suavizado, time_col, avg_delta_t)
    if ativar_preenchimento_gaps:
        df_reindex["Altura Preenchida"] = df_reindex[f"{tipo_de_filtro} {height_col_principal}"]
        df_reindex = preencher_gaps_com_interpolacao(df_reindex, time_col, "Altura Preenchida")
        if height_col_redundancia and height_col_redundancia in df_reindex.columns:
            df_reindex = preencher_gaps_com_redundancia(df_reindex, "Altura Preenchida",
                                                        f"{tipo_de_filtro} {height_col_redundancia}")
        maior_bloco = encontrar_maior_bloco(df_reindex, "Altura Preenchida")
        if len(maior_bloco) >= 806:
            coef = extrair_componentes(df_reindex, latitude, time_col, f"{tipo_de_filtro} {height_col_principal}", maior_bloco)
            df_ajustado = reconstruir_mare(df_reindex, time_col, coef)
            if forecast_days > 0:
                forecast_df = gerar_previsao(df_ajustado, coef, avg_delta_t, time_col, forecast_days)
                df_ajustado_extended = df_ajustado.set_index(time_col).combine_first(forecast_df.set_index(time_col)).reset_index()
            df_ajustado_extended = preencher_gaps_com_previsao(df_ajustado_extended, time_col,
                                                               f"{tipo_de_filtro} {height_col_principal}",
                                                               col_prevista="Altura Prevista")
            df_ajustado_extended = calcular_residuos(df_ajustado_extended, f"{tipo_de_filtro} {height_col_principal}")
        else:
            df_ajustado_extended = df_reindex
    else:
        df_ajustado_extended["Altura Preenchida"] = df_ajustado_extended[f"{tipo_de_filtro} {height_col_principal}"].round(3)

    df_ajustado_extended["Tipo_de_Filtro"] = f"{tipo_de_filtro} {height_col_principal}"
    df_ajustado_extended["Flag_origem"] = np.where(df_ajustado_extended["Altura Preenchida"] == df_ajustado_extended[height_col_principal],"Dado medido", "Dado previsto/redundância")
    df_ajustado_extended['Altura Final'] = suavizar_transicao(df_ajustado_extended,col_preenchida='Altura Preenchida',flag_origem="Flag_origem",window=3)
    df_ajustado_extended['Altura Final'] = aplicar_filtro(df_ajustado_extended,'Altura Preenchida','Filtro Fraco',avg_delta_t).round(3)
    df_ajustado_extended = ajustar_fuso(df_ajustado_extended, time_col, fuso)

    df_flag4_subset = df_flag4[[time_col] + flag_columns]
    df_ajustado_extended = df_ajustado_extended.merge(df_flag4_subset, on=time_col, how='left', suffixes=('', '_flag'))
    for col in flag_columns:
        df_ajustado_extended[col] = df_ajustado_extended[f"{col}_flag"].combine_first(df_ajustado_extended[col])
        df_ajustado_extended = df_ajustado_extended.drop(columns=f"{col}_flag")
        
        
    return df_ajustado_extended



