import QC_FLAGS_UMISAN as qc
import json
#from api_hobo_meteo import acesso_API_HOBBO_meteo
from api_hobo_mare import acesso_API_HOBBO_mare
import pandas as pd
#from SIG1000_string_config import processar_correntes, processar_ondas, organizar_dados_adcp
from backend_mare import calibrar_sensores, formatar_dados_temporais, processar_mare_com_redundancia
from API_ODAS import *
alert_window_size = 100  # Tamanho da janela de dados para ativar o sistema de alerta

def processar_sensor(registro_id: int, caminho_config: str):
    # Carregar configuração
    df_config = pd.read_csv(caminho_config)
    df_config = df_config[df_config["RegistroID"] == registro_id]

    # --- Configurações básicas ---
    parametros_direcionais = ['DirTp','DirTp_sea','DirTp_swell','Main_Direction','Main_Direction_sea',
                              'Main_Direction_swell','Direction','Wind Direction(*)','Heading','Pitch','Roll'] + \
                              [f"Direction_Cell#{i}" for i in range(1,15)]

    parameter_columns = [p.strip().strip("'") for p in qc.get_str(df_config, "parametros_sensor").split(",")]
    filtros_ativos = {f.strip().strip('"'): True for f in qc.get_str(df_config, "filtros_ativos_qc_sensor").split(",")}
    parametro_data_sensor = qc.get_str(df_config, "parametro_data_sensor")
    frequencia_sensor = qc.get_int(df_config, "frequencia_sensor",10)
    caminho_dicionarios = qc.get_path(df_config, "caminho_dicionarios")
    caminho_dos_dados = qc.get_path(df_config, "caminho_dos_dados")
    serial_sensor = [str(qc.get_int(df_config, "serial_sensor"))] if pd.notna(df_config["serial_sensor"].iloc[0]) else []
    start_data = qc.get_date(df_config, "start_data")
    nome_projeto = qc.get_str(df_config, "nome_projeto", None)
    declinacao_magnetica = qc.get_float(df_config, "declinacao_magnetica_sensor")
    numero_de_celulas = qc.get_int(df_config, "numero_celulas_sensor", 0)

    # Parâmetros para correntes
    itens_sem_celulas = ['GMT-03:00','Pitch','Roll','Battery','Heading','Temperature(C)','Pressure(dbar)']
    itens_com_celulas = [item for item in parameter_columns if item not in itens_sem_celulas]
    parameter_columns_correntes = itens_sem_celulas + [f"{item}_Cell#{i}" for item in itens_com_celulas for i in range(1, numero_de_celulas+1)]

    # Filtros / Forecast / Maré
    tipo_de_filtro = qc.get_str(df_config, "tipo_de_filtro")
    ativar_previsao_futura = qc.get_bool(df_config, "ativar_previsao_futura")
    ativar_preenchimento_gaps = qc.get_bool(df_config, "ativar_preenchimento_gaps")
    forecast_days = qc.get_int(df_config, "forecast_days", 0)
    fuso_horas = qc.get_int(df_config, "fuso_horas", 0)
    height_col = qc.get_str(df_config, "height_col", "")
    reducao = qc.get_float(df_config, "reducao_sensor", 0.0)
    a = qc.get_float(df_config, "a_sensor", 1.0)
    b = qc.get_float(df_config, "b_sensor", 0.0)
    lat_estacao = qc.get_float(df_config, "lat_estacao", -22.0)
    long_estacao=qc.get_float(df_config, "long_estacao", -44.0)
    # --- Funções auxiliares ---
    def aplicar_filtros_padrao(df,filtros_ativos):
        return qc.aplicar_filtros(df, parameter_columns, dict_offset, limites_range_check, dict_max_min_test,
                                  st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site,
                                  frequencia_sensor, config["time_col"], alert_window_size, dict_spike,
                                  dict_lt_time_and_regressao, filtros_ativos, parametro_para_teste, parametros_direcionais)

    def aplicar_filtros_correntes(df,filtros_ativos):
        return qc.aplicar_filtros(df, parameter_columns, dict_offset, limites_range_check, dict_max_min_test,
                                  st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site,
                                  frequencia_sensor, config["time_col"], alert_window_size, dict_spike,
                                  dict_lt_time_and_regressao, filtros_ativos, parametro_para_teste, parametros_direcionais,
                                  threshold_plato, threshold_mudanca_abrupta)

    def expandir_chaves_para_celulas(dicionario, n=numero_de_celulas):
        chaves_originais = list(dicionario.keys())
        for k in chaves_originais:
            if (("Amplitude_Cell" in k) or ("Speed(m/s)_Cell" in k) or ("Direction_Cell" in k)) and ("#" not in k):
                for i in range(1, n + 1):
                    dicionario[f"{k}#{i}"] = dicionario[k]
                del dicionario[k]

    # --- Configuração do sensor ---
    def gerar_config_sensor(parameter_columns):
        return {
            "parameter_columns": parameter_columns,
            "sampling_frequency": frequencia_sensor,
            "start": start_data,
            "filtros_ativos": filtros_ativos,
            "logger_ids": serial_sensor,
            "time_col": parametro_data_sensor,
            "declinacao_mag": declinacao_magnetica,
            "tipo_de_filtro": tipo_de_filtro,
            "ativar_preenchimento_gaps": ativar_preenchimento_gaps,
            "ativar_previsao_futura": ativar_previsao_futura,
            "forecast_days": forecast_days,
            "nome_projeto": nome_projeto,
            "fuso_horas": fuso_horas,
            "height_col": height_col,
            "reducao": reducao,
            "a": a,
            "b": b,
            "lat_estacao": lat_estacao
        }

    sensores_config = {
        "CORRENTES": gerar_config_sensor(parameter_columns_correntes),
        "ONDAS": gerar_config_sensor(parameter_columns),
        "ONDAS_NAO_DIRECIONAIS": gerar_config_sensor(parameter_columns),
        "METEOROLOGIA": gerar_config_sensor(parameter_columns),
        "MARE": gerar_config_sensor(parameter_columns)
    }

    config_sensor = {df_config["tipo_sensor"].iloc[0]: sensores_config[df_config["tipo_sensor"].iloc[0]]}

    with open(caminho_dicionarios, 'r') as file:
        config_data = json.load(file)

    todos_os_resultados = []

    for parametro_para_teste, config in config_sensor.items():
        parameter_columns = config["parameter_columns"]

        for key in ["limites_range_check","dict_spike","limite_sigma_aceitavel_and_dict_delta_site",
                    "limite_repeticao_dados","dict_lt_time_and_regressao","st_time_series_dict","dict_max_min_test"]:
            expandir_chaves_para_celulas(config_data[parametro_para_teste][key])

        limites_range_check = config_data[parametro_para_teste]["limites_range_check"]
        dict_spike = config_data[parametro_para_teste]["dict_spike"]
        limite_sigma_aceitavel_and_dict_delta_site = config_data[parametro_para_teste]["limite_sigma_aceitavel_and_dict_delta_site"]
        limite_repeticao_dados = config_data[parametro_para_teste]["limite_repeticao_dados"]
        dict_lt_time_and_regressao = config_data[parametro_para_teste]["dict_lt_time_and_regressao"]
        st_time_series_dict = config_data[parametro_para_teste]["st_time_series_dict"]
        dict_max_min_test = config_data[parametro_para_teste]["dict_max_min_test"]
        dict_offset = {"GMT-03:00": {"limite_futuro_segundos":600,"limite_passado_segundos":86400}}

        if parametro_para_teste == 'CORRENTES':
            threshold_plato = config_data[parametro_para_teste]["threshold_plato"]
            threshold_mudanca_abrupta = config_data[parametro_para_teste]["threshold_mudanca_abrupta"]
 
        # --- Processar dados ---
        if parametro_para_teste == 'METEOROLOGIA': 
            df = acesso_API_HOBBO_meteo(parameter_columns, start=start_data, logger_ids=serial_sensor)
            df = df.assign(**{f"Flag_{col}": 0 for col in parameter_columns})
            df, resultados = aplicar_filtros_padrao(df, filtros_ativos)
 
        elif parametro_para_teste == 'MARE':
            if registro_id == 9 or registro_id == 10:
                df=filtrar_por_sensor(get_df_all(), serial_sensor[0])
            else:
                df, parameter_columns_mare = acesso_API_HOBBO_mare(parameter_columns, start=config["start"], logger_ids=config["logger_ids"])

            df = calibrar_sensores(df, config["height_col"], "Pressure_S2", a, b, reducao)
            print(parameter_columns)
            df = df.assign(**{f"Flag_{col}": 0 for col in parameter_columns})
            df, resultados = aplicar_filtros_padrao(df, filtros_ativos) 
            df = formatar_dados_temporais(df, config["time_col"], config["height_col"])
            df = processar_mare_com_redundancia(df, config["time_col"], config["height_col"], config["height_col"],
                                                config["tipo_de_filtro"], config["sampling_frequency"]*60,
                                                config["forecast_days"], config["parameter_columns"],
                                                config["start"], config["logger_ids"], a, b, reducao,
                                                lat_estacao, config["fuso_horas"], ativar_preenchimento_gaps)
        elif parametro_para_teste == 'CORRENTES':
            dfs = organizar_dados_adcp(caminho_dos_dados, parameter_columns_correntes)
            df = processar_correntes(dfs, parameter_columns_correntes)
            df = df.assign(**{f"Flag_{col}": 0 for col in parameter_columns_correntes})
            df, resultados = aplicar_filtros_correntes(df, filtros_ativos)
        elif parametro_para_teste == 'ONDAS':
            dfs = organizar_dados_adcp(caminho_dos_dados, parameter_columns)
            df = processar_ondas(dfs)[parameter_columns]
            df = df.assign(**{f"Flag_{col}": 0 for col in parameter_columns})
            df, resultados = aplicar_filtros_padrao(df, filtros_ativos)
        elif parametro_para_teste == 'ONDAS_NAO_DIRECIONAIS':
            df = pd.read_csv(caminho_dos_dados, header=1, sep=',', names=parameter_columns)
            df = df.assign(**{f"Flag_{col}": 0 for col in parameter_columns})
            df, resultados = aplicar_filtros_padrao(df,filtros_ativos)

        df['GMT-03:00'] = pd.to_datetime(df['GMT-03:00'], errors='coerce')
        resultados["parameter_column"] = parametro_para_teste
        todos_os_resultados.append(resultados)

    todos_os_resultados = pd.concat(todos_os_resultados, ignore_index=True)
    return df, todos_os_resultados,lat_estacao,long_estacao,df_config




