import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import inspect
import re
from io import StringIO
import logging 
import os
def format_datetime(date_str, time_str):
    """Função para formatar a data e hora no formato correto (YYYY-MM-DD HH:MM:SS)."""
    try:
        date_obj = datetime.strptime(date_str, "%m%d%y")
        time_obj = datetime.strptime(time_str, "%H%M%S")
        formatted_date = date_obj.strftime("%Y-%m-%d")  # YYYY-MM-DD
        formatted_time = time_obj.strftime("%H:%M:%S")  # HH:MM:SS
        return f"{formatted_date} {formatted_time}"
    except Exception as e:
        print(f"Erro ao formatar data/hora: {e}")
        # continue
        return None
def aplicar_filtros(
    df,
    parameter_columns,
    dict_offset,
    limites_range_check,
    dict_max_min_test,
    st_time_series_dict,
    limite_repeticao_dados,
    limite_sigma_aceitavel_and_dict_delta_site,
    sampling_frequency,
    coluna_tempo,
    alert_window_size,
    dict_spike,
    dict_lt_time_and_regressao,
    filtros_ativos,
    parametro_para_teste,
    parametros_direcionais, 
    # Parâmetros opcionais
    threshold_plato=None, 
    threshold_mudanca_abrupta=None,

):
    resultados = []

    if filtros_ativos.get("F01_time_offset"):
        df_before = df.copy()
        df, func_name = time_offset(df, dict_offset)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F02_range_check_sensors"):
        df_before = df.copy()
        df, func_name = range_check_sensors(df, limites_range_check, alert_window_size,parameter_columns)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F03_range_check_env"):
        df_before = df.copy()
        df, func_name = range_check_enviroment(df, limites_range_check, alert_window_size,parameter_columns)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F04_gaps"):
        df_before = df.copy()
        df, func_name = identificar_gaps(df, sampling_frequency, parameter_columns, coluna_tempo, alert_window_size)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F05_nulos"):
        df_before = df.copy()
        df, func_name = identificar_dados_nulos(df, parameter_columns, alert_window_size)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F06_spike"):
        df_before = df.copy()
        df, func_name = spike_test(df, dict_spike, alert_window_size, parametros_direcionais)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F07_lt_trend"):
        df_before = df.copy()
        df, func_name = lt_time_series_rate_of_change(df, dict_lt_time_and_regressao, alert_window_size, parametros_direcionais)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F08_tempo_continuidade"):
        df_before = df.copy()
        df, func_name = teste_continuidade_tempo(df, limite_sigma_aceitavel_and_dict_delta_site, alert_window_size, parametros_direcionais)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F09_duplicatas"):
        df_before = df.copy()
        df, func_name = identificar_duplicatas_tempo(df, parameter_columns, alert_window_size)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F10_repetidos"):
        df_before = df.copy()
        df, func_name = verifica_dados_repetidos(df, limite_repeticao_dados, alert_window_size,parameter_columns)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F11_st_segment"):
        df_before = df.copy()
        df, func_name = st_time_series_segment_shift(df, st_time_series_dict, alert_window_size, parametros_direcionais)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if filtros_ativos.get("F12_max_min"):
        df_before = df.copy()
        df, func_name = max_min_test(df, dict_max_min_test, parametros_direcionais)
        print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if parametro_para_teste == "METEOROLOGIA":
        if filtros_ativos.get("F13_temp_vs_dew"):
            df_before = df.copy()
            df, func_name = verificar_temperatura_vs_ponto_de_orvalho(df, alert_window_size)
            print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
        if filtros_ativos.get("F14_vel_vs_rajada"):
            df_before = df.copy()
            df, func_name = verificar_velocidade_vs_rajada(df, alert_window_size)
            print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if parametro_para_teste in ["ONDAS", "ONDAS_NAO_DIRECIONAIS"]:
        if filtros_ativos.get("F15_altura_max_vs_sig"):
            df_before = df.copy()
            hs_col = 'Hm0' if parametro_para_teste == 'ONDAS' else 'HS_256Hz'
            hmax_col = 'Hmax' if parametro_para_teste == 'ONDAS' else 'Hmax_calc_256Hz'
            df, func_name = verificar_altura_max_vs_sig(df, Hs=hs_col, Hmax=hmax_col)
            print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    if parametro_para_teste == "CORRENTES":
        if filtros_ativos.get("F16_grad_sinal"):
            df_before = df.copy()
            df, func_name = gradiente_de_amplitude_do_sinal(df)
            print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
        if filtros_ativos.get("F17_platos"):
            df_before = df.copy()
            df, func_name = detectar_platos(df, threshold_plato, categorias=["amplitude", "speed", "direction"])
            print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
        if filtros_ativos.get("F18_mudanca_vert"):
            df_before = df.copy()
            df, func_name = taxa_de_mudanca_vertical(df, threshold_mudanca_abrupta, categorias=["amplitude", "speed", "direction"])
            print_confiaveis(df_before, df, func_name, parameter_columns, resultados)
    df_resultados = pd.DataFrame(resultados)
    return df, df_resultados
#%%MODULO FUNCOES DEPENDENTES QCS
def import_df_meteo(caminho_arquivo, nomes_colunas):
    '''importa o arquivo csv bruto, e gera as colunas de controle de qualidade(flag), e coluna suspect(ainda nao aplicavel)'''
    datetime_format = '%m/%d/%y %H:%M:%S'
    # df = pd.read_csv(input_file_meteo,delimiter=',',encoding='utf-8',skiprows=49,header=0,names=nomes_colunas)   
    df = pd.read_excel(caminho_arquivo)
    colunas_interesse = [1,2,3,4,5,6,10,12,13]
    df = df.iloc[:, colunas_interesse]
    df.columns = nomes_colunas
    df['GMT-03:00'] = pd.to_datetime(df['GMT-03:00'], format=datetime_format) 
    for coluna in df.columns:
        df[f'Flag_{coluna}'] = 0
    nomes_colunas = df.columns.tolist()
    return df, nomes_colunas

def import_df_mare(caminho_arquivo, nomes_colunas):
    '''importa o arquivo csv bruto, e gera as colunas de controle de qualidade(flag), e coluna suspect(ainda nao aplicavel)'''
    df= pd.read_csv(caminho_arquivo, names=nomes_colunas)    
    df['GMT-03:00'] = pd.to_datetime(df['GMT-03:00'])
    for coluna in nomes_colunas:
        df[f'Flag_{coluna}'] = 0    
    # df['Suspect'] = 0
    return df,nomes_colunas

def import_df_currents (caminho_arquivo,parameter_columns):
    '''importa o arquivo csv bruto, e gera as colunas de controle de qualidade(flag), e coluna suspect(ainda nao aplicavel)'''
    df = pd.read_csv(caminho_arquivo, sep=',', skiprows=1, usecols=range(len(parameter_columns)), header=None, names=parameter_columns)   
    df['GMT-03:00'] = pd.to_datetime(df['GMT-03:00'])
    for coluna in parameter_columns:
        df[f'Flag_{coluna}'] = 0   
    # df['Suspect'] = 0
    return df
def calcular_componentes_uv(df, declinacao_magnetica):
    # a função calcula os componentes U e V da direção do vento (m/s).
    velocidade = df["Wind Speed(m/s)"]
    direcao = df['Wind Direction(*)']
    direcao_rad = np.radians(direcao + declinacao_magnetica)
    df['u']  = velocidade * np.cos(direcao_rad)
    df['v'] = velocidade * np.sin(direcao_rad)
    
def diferenca_angular(angulo_novo, angulo_antigo):
# a função calcula a de diferença angular entre dois angulos
    diff = (angulo_novo - angulo_antigo + 180) % 360 - 180
    return diff

def classificar_porcentagem(percentual_flags):
# a função atribui grau de prioridade ao alerta baseado no percentual de flags. 
    if percentual_flags < 5:
        return 'Não classificado'
    elif percentual_flags < 10:
        return 'Prioridade Baixa'
    elif percentual_flags < 25:
        return 'Prioridade Media'
    elif percentual_flags < 50:
        return 'Prioridade Alta'
    else:
        return 'Prioridade Urgente'
logging.basicConfig(
    filename='alertas.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
def get_str(df, col, default=""):
    val = df.get(col, pd.Series([default])).iloc[0]
    return str(val).strip().strip("'").strip('"') if pd.notna(val) else default

def get_int(df, col, default=0):
    val = pd.to_numeric(df.get(col, pd.Series([default])).iloc[0], errors="coerce")
    return int(val) if pd.notna(val) else default

def get_float(df, col, default=0.0):
    val = pd.to_numeric(df.get(col, pd.Series([default])).iloc[0], errors="coerce")
    return float(val) if pd.notna(val) else default

def get_bool(df, col, default=False):
    val = df.get(col, pd.Series([default])).iloc[0]
    return bool(val) if pd.notna(val) else default

def get_date(df, col, default=None, fmt="%Y-%m-%d %H:%M:%S"):
    val = df.get(col, pd.Series([default])).iloc[0]
    return pd.to_datetime(val).strftime(fmt) if pd.notna(val) else default

def get_path(df, col, default=""):
    val = df.get(col, pd.Series([default])).iloc[0]
    return os.path.normpath(val) if pd.notna(val) else default

def alerta(alert_window_size, parameter_column, func_name, df):
    classe_counts = {'Não classificado': 0, 'Prioridade Baixa': 0, 'Prioridade Media': 0, 'Prioridade Alta': 0, 'Prioridade Urgente': 0}
    for i in range(len(df) - alert_window_size + 1):
        flags_na_janela = df[f'Flag_{parameter_column}'].iloc[i:i+alert_window_size].sum()
        percentual_flags = (flags_na_janela / alert_window_size) * 100
        classe = classificar_porcentagem(percentual_flags)
        classe_counts[classe] += 1       
        if classe == 'Prioridade Urgente':
            urgente = f'Alerta URGENTE. Conferir dados -{parameter_column}- {func_name}.ID:{i}:{i+alert_window_size}'
            with open('alertas.log', 'a') as f:
                f.write(urgente + '\n')
    pass
def print_confiaveis(df_before, df_after, func_name, parameter_columns, resultados):
    for parameter_column in parameter_columns:
        # Flags antes e depois
        flag_before = df_before[f'Flag_{parameter_column}']
        flag_after = df_after[f'Flag_{parameter_column}']
        
        # Novas falhas geradas neste teste: eram 0 e viraram ≠ 0
        novas_falhas = (flag_before == 0) & (flag_after != 0)
        fail = novas_falhas.sum()
        
        total_testado = len(df_before)
        confiaveis = total_testado - fail
        dados_confiaveis = round(100 * confiaveis / total_testado, 2)

        texto = f"{fail} F/{dados_confiaveis}C. {func_name},{parameter_column}.Total: {total_testado} "
        print(texto)
        resultados.append({
            'Teste': func_name,
            'Parametro': parameter_column,
            'Porcentagem Confiáveis': dados_confiaveis,
            'Porcentagem Falhos':100- dados_confiaveis,
            'Total de dados':total_testado,
            'Falhos': fail,
            'Confiáveis': confiaveis
        })
    return resultados

def mean_direction(angles):
    # Calcula a média angular de uma lista de direções (em graus)
    radians = np.radians(angles)  # Converte para radianos
    mean_x = np.mean(np.cos(radians))  # Média do cosseno
    mean_y = np.mean(np.sin(radians))  # Média do seno
    mean_angle = np.degrees(np.arctan2(mean_y, mean_x))  # Calcula o ângulo médio em radianos, depois converte para graus
    
    # Garante que o ângulo esteja entre 0 e 360
    if mean_angle < 0:
        mean_angle += 360
    return mean_angle
def angular_diff(a, b):
    """Retorna a menor diferença angular entre dois ângulos (em graus)."""
    return 180 - abs(abs(a - b) % 360 - 180)

def circular_mean(series):
    """Média circular em graus."""
    radians = np.deg2rad(series.dropna())
    return np.rad2deg(np.arctan2(np.mean(np.sin(radians)), np.mean(np.cos(radians)))) % 360

def circular_std(series):
    """Desvio padrão circular em graus."""
    radians = np.deg2rad(series.dropna())
    R = np.sqrt(np.mean(np.cos(radians))**2 + np.mean(np.sin(radians))**2)
    return np.rad2deg(np.sqrt(-2 * np.log(R))) if R > 0 else np.nan

def calculate_mean_A(df):
    """    Calcula a média das colunas A1, A2, A3 e A4 para cada instante de tempo (DateTime).    """
    columns_to_avg = ['Amplitude', 'A2', 'A3', 'A4']
    df_mean = df.groupby('GMT-03:00')[columns_to_avg].mean().reset_index()
    return df_mean
def to_wide_format(df):
    """ Converte o DataFrame no formato wide, com uma linha por instante de tempo
    e informações de todas as células distribuídas em colunas. """
    value_columns = [ 'Speed(m/s)', 'Direction', 'Amplitude', 'Correlation']
    df['Cell'] = 'Cell#' + df['Cell number'].astype(str)
    wide_df = df.pivot(index='GMT-03:00', values=value_columns, columns='Cell')
    wide_df.columns = [f"{col[0]}_{col[1]}" for col in wide_df.columns]  # Adiciona o número da célula depois do nome do parâmetro
    wide_df.reset_index(inplace=True)
    return wide_df
def process_txt_to_multiple_dfs(input_file_meteo):
    with open(input_file_meteo, 'r') as file:
        lines = file.readlines()

    dataframes = {}
    prev_date_str = None
    prev_time_str = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        fields = line.split(',')
        prefix = fields[0]
        
        if prefix not in dataframes:
            dataframes[prefix] = []

        # Se o prefixo for '$PNORI', pega a data e hora da próxima linha com '$PNORS'
        if prefix == '$PNORI':
            # Verifica se a próxima linha é válida e tem o prefixo '$PNORS'
            if i + 1 < len(lines) and lines[i + 1].startswith('$PNORS'):
                next_line = lines[i + 1].strip()
                next_fields = next_line.split(',')
                prev_date_str = next_fields[1]  # Pega a data da linha seguinte
                prev_time_str = next_fields[2]  # Pega o horário da linha seguinte
            date_str = prev_date_str
            time_str = prev_time_str
        elif prefix == '$PNORF':
            date_str = fields[2]
            time_str = fields[3]
        else:
            date_str = fields[1]
            time_str = fields[2]
        
        # Formatar a data e hora
        formatted_datetime = format_datetime(date_str, time_str)
        formatted_fields = [formatted_datetime] + fields[0:]
        dataframes[prefix].append(formatted_fields)
    
    # Criação dos DataFrames para cada prefixo
    for prefix, rows in dataframes.items():
        df = pd.DataFrame(rows)
        df.columns = ['DateTime'] + [f'Field_{i}' for i in range(2, len(df.columns) + 1)]
        dataframes[prefix] = df
        globals()[f"df_{prefix.strip('$')}"] = df  # Exemplo: cria df_PNORI, df_PNORS, etc.

    # print("Dataframes criados para os seguintes prefixos:")
    # for key in dataframes.keys():
    #     print(f"df_{key.strip('$')}")
    
    return dataframes

def organizar_String_adcp(caminho_arquivo,parameter_columns_PNORC,parameter_columns_PNORI,parameter_columns_PNORS,parameter_columns_PNORB,parameter_columns_PNORW,parameter_columns ):
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        linhas_arquivo = f.readlines()[0:]  # pula as 4 primeiras linhas
        conteudo = ''.join(linhas_arquivo)
    conteudo_io = StringIO(conteudo)
    df = pd.read_csv(conteudo_io, sep=',', header=None,on_bad_lines='skip')
    df_datalogger = df.iloc[:, [0, 2]]
    df_datalogger.columns = ['GMT-03:00', 'Battery']  # novos nomes das colunas

    df = pd.DataFrame(df.iloc[:, 3])
    df_texto = df.to_string(index=False, header=False)
    df_texto = df_texto.replace('\n', '')  # Substitui quebras de linha por espaço
    df_texto = df_texto.replace('PNORI\n', 'PNORI')
    df_texto = df_texto.replace('  ', '\n')
    df_texto=df_texto.strip()
    texto_io = StringIO(df_texto)
    rows = []
    for row in texto_io:
        values = row.strip().split(',')
        rows.append(values)
    max_cols = max(len(r) for r in rows)
    rows_padded = [
        r + [None] * (max_cols - len(r))
        for r in rows]
    df = pd.DataFrame(rows_padded,columns=[f'col_{i+1}' for i in range(max_cols)])
    df_pnori = df[df.iloc[:, 0] == "$PNORI"].dropna(axis=1, how='all')
    df_pnors = df[df.iloc[:, 0] == "$PNORS"].dropna(axis=1, how='all')
    df_pnorc = df[df.iloc[:, 0] == "$PNORC"].dropna(axis=1, how='all')
    df_pnorb = df[df.iloc[:, 0] == "$PNORB"].dropna(axis=1, how='all')
    df_pnorw = df[df.iloc[:, 0] == "$PNORW"].dropna(axis=1, how='all')
    df_pnore = df[df.iloc[:, 0] == "$PNORE"].dropna(axis=1, how='all')
    df_pnorf = df[df.iloc[:, 0] == "$PNORF"].dropna(axis=1, how='all')
    df_pnorwd = df[df.iloc[:, 0] == "$PNORWD"].dropna(axis=1, how='all')
    df_pnorc = df_pnorc[df_pnorc.count(axis=1) == 19].copy()
    df_pnorc = df_pnorc.dropna(axis=1, how='all')
    # df_pnorc = df_pnorc.drop(5099, axis=0)

    df_pnori.columns = parameter_columns_PNORI
    df_pnorc.columns = parameter_columns_PNORC
    df_pnorb.columns = parameter_columns_PNORB
    df_pnorw.columns = parameter_columns_PNORW
    df_pnors.columns = parameter_columns_PNORS  
    df_pnors = adicionar_coluna_DATATIME(df_pnors)
    df_pnorw = adicionar_coluna_DATATIME(df_pnorw)
    df_pnore= adicionar_coluna_DATATIME(df_pnore)
    df_pnorb = adicionar_coluna_DATATIME(df_pnorb)
    df_pnorc = adicionar_coluna_DATATIME(df_pnorc)
    return df_pnori, df_pnors, df_pnorw, df_pnore, df_pnorc, df_pnorwd, df_pnorb, df_pnorf, df_datalogger

#####
def adicionar_coluna_DATATIME(df):
    datetime_format = '%m%d%y %H%M%S'
    if 'Date' in df.columns and 'Time' in df.columns:
        df['GMT-03:00'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format=datetime_format, errors='coerce')
        df['GMT-03:00'] = df['GMT-03:00'].dt.strftime('%m/%d/%y %H:%M:%S')
        cols = ['GMT-03:00'] + [col for col in df.columns if col != 'GMT-03:00']
        df = df[cols]
    return df
def import_and_merge_wave_parameter(df_pnorb,df_pnors,df_pnorw):
    # parameter_columns=parameter_columns_ondas

    df_pnorb['tipo'] = df_pnorb.groupby('GMT-03:00').cumcount().map({0: 'sea', 1: 'swell'})
    df_pnorb_wide = df_pnorb.pivot(index='GMT-03:00', columns='tipo')
    df_pnorb_wide.columns = [f"{col}_{tipo}" for col, tipo in df_pnorb_wide.columns]
    df_ondas = df_pnorw.merge(df_pnorb_wide.reset_index(), on='GMT-03:00', how='left')
    df_ondas['GMT-03:00'] = pd.to_datetime(df_ondas['GMT-03:00'], errors='coerce')
    df_pnors['GMT-03:00'] = pd.to_datetime(df_pnors['GMT-03:00'], errors='coerce')
    df_ondas = df_ondas.sort_values(by='GMT-03:00')
    df_pnors = df_pnors.sort_values(by='GMT-03:00')
    df_ondas = pd.merge_asof(df_ondas, df_pnors, on='GMT-03:00', direction='nearest')
    # df_ondas = df_ondas[parameter_columns_ondas]
    value_cols = [col for col in df_ondas.columns if col not in ['Identifier','Date', 'GMT-03:00','Time', 'Cell_number', 'row_id']]
    df_ondas[value_cols] = df_ondas[value_cols].apply(pd.to_numeric, errors='coerce')

        
    return df_ondas
def import_and_merge_curr_parameter(df_pnors,df_pnorc):
    ultima_coluna = df_pnorc.columns[-1]
    df_pnorc['prioridade'] = df_pnorc[ultima_coluna].notna().astype(int)
    df_pnorc = df_pnorc.sort_values(by=['prioridade'], ascending=False)
    df_pnorc = df_pnorc.drop_duplicates(subset=['Date', 'Time', 'Cell_number'], keep='first')
    df_pnorc = df_pnorc.drop(columns='prioridade')
    df_pnorc['Cell_number'] = df_pnorc['Cell_number'].astype(str)
    df_pnorc['row_id'] = df_pnorc.groupby(['Identifier','Date', 'Time','GMT-03:00']).ngroup()
    
    value_cols = [col for col in df_pnorc.columns if col not in ['Identifier','Date', 'GMT-03:00','Time', 'Cell_number', 'row_id']]
    df_pnorc[value_cols] = df_pnorc[value_cols].apply(pd.to_numeric, errors='coerce')

    df_pnorc_wide = df_pnorc.pivot(index='row_id', columns='Cell_number', values=value_cols)
    df_pnorc_wide.columns = [f"{param}_Cell#{cell}" for param, cell in df_pnorc_wide.columns]
    ids = df_pnorc[['row_id', 'Date', 'Time']].drop_duplicates()
    df_pnorc = ids.merge(df_pnorc_wide.reset_index(), on='row_id').drop(columns='row_id')
    df_pnorc = adicionar_coluna_DATATIME(df_pnorc)
    df_pnorc['GMT-03:00'] = pd.to_datetime(df_pnorc['GMT-03:00'], errors='coerce')
    df_pnors['GMT-03:00'] = pd.to_datetime(df_pnors['GMT-03:00'], errors='coerce')
    df_correntes = df_pnorc.merge(df_pnors.reset_index(), on='GMT-03:00', how='left')
    df_correntes['GMT-03:00'] = pd.to_datetime(df_correntes['GMT-03:00'], errors='coerce')
    df_correntes = df_correntes.sort_values(by='GMT-03:00')
    # df_correntes=df_correntes[parameter_columns_correntes]

    # df_correntes = df_correntes[[col for col in df_correntes.columns if any(param in col for param in parameter_columns_correntes)]]# linha descontinuada pra aumentar a rigorosidade dos filtros
    # for coluna in df_correntes.columns:# linha descontinuada pois esta quebrando o df e causando lentidao quando sao muitas colunas add de uma unica vez
    #     df_correntes[f'Flag_{coluna}'] = 0
        # Cria todas as colunas de flag de uma vez

    
    # Opcional: desfaz a fragmentação acumulada
    df_correntes = df_correntes.copy()

    return df_correntes
def importar_dados_corrente_string_ADCP(df_PNORC,df_PNORI,df_PNORS,parameter_columns_PNORC,parameter_columns_PNORI,parameter_columns_PNORS,parameter_columns):    # Ajustar os nomes das colunas
    df_PNORC.columns = parameter_columns_PNORC
    df_PNORI.columns = parameter_columns_PNORI
    df_PNORS.columns = parameter_columns_PNORS

    df_PNORC = to_wide_format(df_PNORC)

    merged_df = pd.merge(df_PNORI, df_PNORS, on='GMT-03:00', how='outer')
    merged_df = pd.merge(merged_df, df_PNORC, on='GMT-03:00', how='outer')

    additional_columns = [col for col in merged_df.columns if any(term in col for term in ['Speed(m/s)', 'Direction', 'Amplitude'])]
    selected_columns = list(set(parameter_columns + additional_columns))

    df_correntes = merged_df[selected_columns]

    # Ordenar as colunas numericamente com base nos números (se existirem)
    def ordenar_colunas_numericamente(colunas):
        return sorted(
            colunas,
            key=lambda x: int(re.search(r'#(\d+)', x).group(1)) if re.search(r'#(\d+)', x) else float('inf')
        )
    sorted_columns = ordenar_colunas_numericamente(df_correntes.columns)
    df_correntes = df_correntes[sorted_columns]
    for coluna in df_correntes.columns:
        df_correntes[f'Flag_{coluna}'] = 0
    return df_correntes,selected_columns
def process_wave_data(df_pnorw, df_pnorb, df_pnori,df_pnors, param_columns_pnorw, param_columns_pnorb,parameter_columns_PNORI,parameter_columns_PNORS, param_columns_final):
    df_pnorw.columns = param_columns_pnorw
    df_pnorb.columns = param_columns_pnorb
    df_pnori.columns = parameter_columns_PNORI

    df_pnors.columns = parameter_columns_PNORS

    df_pnorb['Classification'] = ['sea' if i % 2 == 0 else 'swell' for i in range(len(df_pnorb))]
    df_pnorw['Classification'] = ['sea' if i % 2 == 0 else 'swell' for i in range(len(df_pnorw))]
    df_ondas = df_pnorb.pivot_table(
        index='GMT-03:00',
        columns='Classification',
        values=df_pnorb.columns.difference(['gmt', 'Classification']),
        aggfunc='first'
    )
    df_ondas.columns = [f'{col[0]}_{col[1]}' for col in df_ondas.columns]
    df_ondas.reset_index(inplace=True)   
    df_ondas = pd.merge(df_pnorw, df_ondas, on='GMT-03:00', how='inner')
    df_ondas['GMT-03:00'] = pd.to_datetime(df_ondas['GMT-03:00'])
    df_pnors['GMT-03:00'] = pd.to_datetime(df_pnors['GMT-03:00'])
    df_pnori['GMT-03:00'] = pd.to_datetime(df_pnori['GMT-03:00'])

    headerADCP_df = pd.merge(df_pnori, df_pnors, on='GMT-03:00', how='outer')

    # Realiza o merge utilizando a correspondência mais próxima, sem interpolação
    df_ondas = pd.merge_asof(df_ondas.sort_values('GMT-03:00'),
                              headerADCP_df.sort_values('GMT-03:00'),
                              on='GMT-03:00',
                              direction='nearest')  # Alinha para a linha mais próxima sem interpolação

    df_ondas.iloc[:, 1:] = df_ondas.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

    df_ondas = df_ondas[param_columns_final]
    
    for coluna in df_ondas.columns:
        df_ondas[f'Flag_{coluna}'] = 0
    return df_ondas


def gerar_grafico_gradiente_vertical(df, linha_escolhida, coluna_escolhida):
    selected_columns = [col for col in df.columns if col.lower().startswith(coluna_escolhida.lower())]
    selected_data = pd.to_numeric(df.loc[linha_escolhida, selected_columns], errors='coerce')
    cell_numbers = [int(col.split('#')[1].split('_')[0]) for col in selected_columns]
    temp_df = pd.DataFrame({'Cell': cell_numbers, coluna_escolhida.capitalize(): selected_data}).sort_values('Cell')
    
    plt.figure(figsize=(10, 6))
    plt.plot(temp_df[coluna_escolhida.capitalize()], temp_df['Cell'], marker='o', linestyle='-', color='purple', label=coluna_escolhida.capitalize())
    plt.title(f'Perfil Vertical de {coluna_escolhida.capitalize()}', fontsize=14)
    plt.ylabel('Profundidade', fontsize=12)
    plt.xlabel(coluna_escolhida.capitalize(), fontsize=12)
    plt.grid(visible=True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)
    # plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
def plot_historical_series(df, parameter_columns):   
    speed_params = [param for param in parameter_columns if param.startswith("v")]
    direction_params = [param for param in parameter_columns if param.startswith("Direction")]
    amplitude_params = [param for param in parameter_columns if param.startswith("A")]

    for param in parameter_columns:
        if param not in amplitude_params:
            if param in speed_params:
                flag_column = f'Flag_{param}'
                if flag_column in df.columns:
                    plt.figure(figsize=(10, 6))
                    df_flag_0 = df[df[flag_column] != 4]
                    df_flag_4 = df[df[flag_column] == 4]
                    df_nan = df[df[param].isna()]  # Filtrando os valores NaN
                    df_flag_4_gmt = df[df['Flag_GMT-03:00'] == 4]  # Identificar as flags na coluna GMT-03:00
                    plt.plot(df['GMT-03:00'], df[param], label=f'Série Completa ({param})', color='black', linestyle='-', linewidth=1)
                    plt.scatter(df_flag_0['GMT-03:00'], df_flag_0[param], color='blue', s=30, label='Flag 0')
                    plt.scatter(df_flag_4['GMT-03:00'], df_flag_4[param], color='red', s=30, label='Flag 4')
                    plt.scatter(df_flag_4_gmt['GMT-03:00'], df_flag_4_gmt[param], s=30, marker='x', color='red', zorder=15)
                    plt.scatter(df_nan['GMT-03:00'], [0] * len(df_nan), s=30, marker='x', color='red', zorder=15)
                    plt.title(f'Série Histórica: {param}')
                    plt.xlabel('Data e Hora')
                    plt.ylabel(param)
                    plt.xticks(rotation=45)
                    plt.legend()
                    plt.grid(True)
                    plt.ylim(0, 20)
                    plt.tight_layout()
                    plt.show()
                continue
            elif param in direction_params:
                flag_column = f'Flag_{param}'
                if flag_column in df.columns:
                    plt.figure(figsize=(10, 6))
                    df_flag_0 = df[df[flag_column] != 4]
                    df_flag_4 = df[df[flag_column] == 4]
                    df_nan = df[df[param].isna()]  # Filtrando os valores NaN
                    df_flag_4_gmt = df[df['Flag_GMT-03:00'] == 4]  # Identificar as flags na coluna GMT-03:00
                    plt.plot(df['GMT-03:00'], df[param], label=f'Série Completa ({param})', color='black', linestyle='-', linewidth=1)
                    plt.scatter(df_flag_0['GMT-03:00'], df_flag_0[param], color='blue', s=30, label='Flag 0')
                    plt.scatter(df_flag_4['GMT-03:00'], df_flag_4[param], color='red', s=30, label='Flag 4')
                    plt.scatter(df_flag_4_gmt['GMT-03:00'], df_flag_4_gmt[param], s=30, marker='x', color='red', zorder=15)
                    plt.scatter(df_nan['GMT-03:00'], [0] * len(df_nan), s=30, marker='x', color='red', zorder=15)
                    plt.title(f'Série Histórica: {param}')
                    plt.xlabel('Data e Hora')
                    plt.ylabel(param)
                    plt.xticks(rotation=45)
                    plt.legend()
                    plt.grid(True)
                    # plt.ylim(0, 360)
                    plt.tight_layout()
                    plt.show()
                continue
            else:
                flag_column = f'Flag_{param}'
                if flag_column in df.columns:
                    plt.figure(figsize=(10, 6))
                    df_flag_0 = df[df[flag_column] != 4]
                    df_flag_4 = df[df[flag_column] == 4]
                    df_nan = df[df[param].isna()]  # Filtrando os valores NaN
                    df_flag_4_gmt = df[df['Flag_GMT-03:00'] == 4]  # Identificar as flags na coluna GMT-03:00
                    plt.plot(df['GMT-03:00'], df[param], label=f'Série Completa ({param})', color='black', linestyle='-', linewidth=1)
                    plt.scatter(df_flag_0['GMT-03:00'], df_flag_0[param], color='blue', s=30, label='Flag 0')
                    plt.scatter(df_flag_4['GMT-03:00'], df_flag_4[param], color='red', s=30, label='Flag 4')
                    plt.scatter(df_flag_4_gmt['GMT-03:00'], df_flag_4_gmt[param], s=30, marker='x', color='red', zorder=15)
                    plt.scatter(df_nan['GMT-03:00'], [0] * len(df_nan), s=30, marker='x', color='red', zorder=15)
                    plt.title(f'Série Histórica: {param}')
                    plt.xlabel('Data e Hora')
                    plt.ylabel(param)
                    plt.xticks(rotation=45)
                    plt.legend()
                    plt.grid(True)
                    plt.tight_layout()
                    plt.show()


#%% MODULO QC ##FIXME
#TESTE 1: Time Offset.
def time_offset(df, dict_offset):
    limite_futuro_segundos = dict_offset["GMT-03:00"]["limite_futuro_segundos"]
    limite_passado_segundos = dict_offset["GMT-03:00"]["limite_passado_segundos"]
    df['GMT-03:00'] = pd.to_datetime(df['GMT-03:00'])
    tempo_atual = pd.Timestamp.now()
    timestamp_inicial = df['GMT-03:00'].iloc[0]
    df["Flag_GMT-03:00"] |= np.where(df['GMT-03:00'] > tempo_atual + pd.to_timedelta(limite_futuro_segundos, unit='s'), 4, 0)
    limite_passado_tempo = timestamp_inicial - pd.to_timedelta(limite_passado_segundos, unit='s')
    df["Flag_GMT-03:00"] |= np.where(df['GMT-03:00'] < limite_passado_tempo, 4, 0)
    func_name = inspect.currentframe().f_code.co_name
    return df, func_name



# #TESTE 2: Range Check Sensors.
def range_check_sensors(df, limites_range_check, alert_window_size,parameter_columns):

    for parameter_column, valores in limites_range_check.items():
        if parameter_column not in parameter_columns:
            continue
        limite_inferior_sensor = valores.get("sensores_min")
        limite_superior_sensor = valores.get("sensores_max")
        
        df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')
        condition_fail_sensor = (df[parameter_column] > limite_superior_sensor) | (df[parameter_column] < limite_inferior_sensor)
        df[f'Flag_{parameter_column}'] |= np.where(condition_fail_sensor, 4, 0)
        alerta(alert_window_size, parameter_column, range_check_sensors.__name__, df)
    return df, inspect.currentframe().f_code.co_name

#TESTE 3: Range Check Enviroment.
def range_check_enviroment (df, limites_range_check,alert_window_size,parameter_columns):
    for parameter_column, valores in limites_range_check.items():
        if parameter_column not in parameter_columns:
            continue
        limite_inferior_ambiental = valores.get("ambiental_min")
        limite_superior_ambiental = valores.get("ambiental_max")
        df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')
        condition_fail_sensor = (df[parameter_column] > limite_superior_ambiental) | (df[parameter_column] < limite_inferior_ambiental)
        df[f'Flag_{parameter_column}'] |= np.where(condition_fail_sensor, 4, 0)
        alerta(alert_window_size, parameter_column, range_check_enviroment.__name__, df)
    return df, inspect.currentframe().f_code.co_name


#TESTE 4: Identificar Gaps.
# def identificar_gaps(df, sampling_frequency, parameter_columns, coluna_tempo, alert_window_size, limite_segurança=59):
#     """    Identifica e preenche gaps no DataFrame, mantendo a frequência esperada e marcando flags apropriadas."""
#     novo_indice = pd.date_range(start=df[coluna_tempo].min(), 
#                                 end=df[coluna_tempo].max(), 
#                                 freq=f'{sampling_frequency}min')
#     df = df.set_index(coluna_tempo).reindex(novo_indice).rename_axis(coluna_tempo).reset_index()
#     for parameter_column in parameter_columns:
#         df[f'Flag_{parameter_column}'] = df[f'Flag_{parameter_column}'].fillna(0).astype(int)
#         gaps = df[parameter_column].isna()
#         df['Flag_GMT-03:00'] |= np.where(gaps, 4, 0)
#         alerta(alert_window_size, parameter_column, identificar_gaps.__name__, df)       
#     return df, inspect.currentframe().f_code.co_name

def identificar_gaps(df, sampling_frequency, parameter_columns, coluna_tempo, alert_window_size):
    
    """
    Identifica e preenche gaps no DataFrame com tolerância ao atraso.
    Marca flags apenas quando há ausência real de dados (gap > limite_segurança).
    """
    limite_segurança=sampling_frequency/3
    df[coluna_tempo] = pd.to_datetime(df[coluna_tempo])

    # Arredonda os timestamps para a grade mais próxima do intervalo desejado
    df[coluna_tempo] = df[coluna_tempo].dt.round(f'{sampling_frequency}min')

    # Cria novo índice baseado na grade esperada
    inicio = df[coluna_tempo].min().floor(f'{sampling_frequency}min')
    fim = df[coluna_tempo].max().ceil(f'{sampling_frequency}min')
    novo_indice = pd.date_range(start=inicio, end=fim, freq=f'{sampling_frequency}min')

    # Junta o DataFrame aos tempos esperados
    df = df.drop_duplicates(subset=coluna_tempo)

    df = df.set_index(coluna_tempo).reindex(novo_indice).rename_axis(coluna_tempo).reset_index()

    # Marca flag de gap se a diferença entre pontos for maior que o limite de segurança
    for parameter_column in parameter_columns:
        df[f'Flag_{parameter_column}'] = df.get(f'Flag_{parameter_column}', 0).fillna(0).astype(int)
        gaps = df[parameter_column].isna()
        
        # Apenas marca flag se o gap é real
        time_diffs = df[coluna_tempo].diff().dt.total_seconds().div(60).fillna(sampling_frequency)
        flag_real_gap = (gaps) & (time_diffs > limite_segurança)
        df[f'Flag_{parameter_column}'] |= np.where(flag_real_gap, 4, 0)

        alerta(alert_window_size, parameter_column, identificar_gaps.__name__, df)

    return df, inspect.currentframe().f_code.co_name


#TESTE 5: Identificar dados nulos.
def identificar_dados_nulos(df,parameter_columns,alert_window_size):
    # a função verifica se o valor observado é nulo (missing value, -9999, etc)
    for parameter_column in parameter_columns:
        df[f'Flag_{parameter_column}']|= np.where(df[parameter_column].isnull(), 4,0)
        alerta(alert_window_size, parameter_column, identificar_dados_nulos.__name__, df) 
    return df, inspect.currentframe().f_code.co_name

#Teste 6: Spike Test.
# def spike_test(df, dict_spike,alert_window_size):#versao descontinuada por nao servir para dados direcionais
#     for parameter_column, params in dict_spike.items():
#         window = params['window']  # Tamanho da janela móvel
#         threshold_factor = params["threshold_factor"]  # Fator do desvio padrão
#         df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')
#         rolling_mean = df[parameter_column].rolling(window=window, min_periods=1).mean()
#         rolling_std = df[parameter_column].rolling(window=window, min_periods=1).std()
#         limiar = threshold_factor * rolling_std
#         condition_spike = (df[parameter_column] > rolling_mean + limiar) | \
#                           (df[parameter_column] < rolling_mean - limiar)
#         df[f'Flag_{parameter_column}'] |= np.where(condition_spike, 4, 0)
#         alerta(alert_window_size, parameter_column, spike_test.__name__, df)
#     return df, inspect.currentframe().f_code.co_name

def spike_test(df, dict_spike, alert_window_size, parametros_direcionais):
    
    
    for parameter_column, params in dict_spike.items():
        if parameter_column not in df.columns:
            continue  # pula se a coluna não existe no DataFrame
        window = params['window']
        threshold_factor = params['threshold_factor']
        df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')
        is_directional = parameter_column in parametros_direcionais
        if is_directional:
            rolling_mean = df[parameter_column].rolling(window=window, min_periods=1).apply(circular_mean, raw=False)
            rolling_std = df[parameter_column].rolling(window=window, min_periods=1).apply(circular_std, raw=False)
            diffs = angular_diff(df[parameter_column], rolling_mean)
        else:
            rolling_mean = df[parameter_column].rolling(window=window, min_periods=1).mean()
            rolling_std = df[parameter_column].rolling(window=window, min_periods=1).std()
            diffs = (df[parameter_column] - rolling_mean).abs()
        limiar = threshold_factor * rolling_std
        condition_spike = diffs > limiar
        df[f'Flag_{parameter_column}'] |= np.where(condition_spike, 4, 0)
        alerta(alert_window_size, parameter_column, spike_test.__name__, df)
    return df, inspect.currentframe().f_code.co_name


#Teste 7: LT Time series rate of change.#versao descontinuada por nao servir para dados direcionais
# def lt_time_series_rate_of_change(df, dict_lt_time_and_regressao, alert_window_size):
#     # A função verifica se as observações consecutivas apresentam uma diferença dentro de um limite especificado.
#     for parameter_column, params in dict_lt_time_and_regressao.items():
#         delta_thresh = params["delta_lt_time"]
#         df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')
#         condicao = df[parameter_column].diff().abs() >= delta_thresh
#         df[f'Flag_{parameter_column}'] |= np.where(condicao, 4, 0)
#         alerta(alert_window_size, parameter_column, lt_time_series_rate_of_change.__name__, df)
#     return df, inspect.currentframe().f_code.co_name


def lt_time_series_rate_of_change(df, dict_lt_time_and_regressao, alert_window_size, parametros_direcionais):
    for parameter_column, params in dict_lt_time_and_regressao.items():
        if parameter_column not in df.columns:
            continue
        delta_thresh = params["delta_lt_time"]
        df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')
        if parameter_column in parametros_direcionais:
            diff_fw = angular_diff(df[parameter_column], df[parameter_column].shift(1))
            diff_bw = angular_diff(df[parameter_column], df[parameter_column].shift(-1))
        else:
            diff_fw = df[parameter_column].diff().abs()
            diff_bw = df[parameter_column].shift(-1).subtract(df[parameter_column]).abs()
        condicao_fw = diff_fw >= delta_thresh
        condicao_bw = diff_bw >= delta_thresh
        condicao_final = condicao_fw & condicao_bw  # sinal mais forte: pico isolado
        condicao_leve = condicao_fw | condicao_bw   # marca também os dois lados, se quiser
        df[f'Flag_{parameter_column}'] = df.get(f'Flag_{parameter_column}', 0)
        df[f'Flag_{parameter_column}'] |= np.where(condicao_final, 4, 0)
        alerta(alert_window_size, parameter_column, lt_time_series_rate_of_change.__name__, df)
    return df, inspect.currentframe().f_code.co_name


#Teste 8: Continuidade tempo.
# def teste_continuidade_tempo (df, limite_sigma_aceitavel_and_dict_delta_site, alert_window_size):
#     for parameter_column, config in limite_sigma_aceitavel_and_dict_delta_site.items():
#         window = config["window"]
#         n_desvpad_fail = config["delta"]
#         df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')
#         rolling_stats = df[parameter_column].rolling(window).agg(['mean', 'std'])
#         upper_limit_fail = rolling_stats['mean'] + n_desvpad_fail * rolling_stats['std']
#         lower_limit_fail = rolling_stats['mean'] - n_desvpad_fail * rolling_stats['std']
#         condition_fail = (df[parameter_column] < lower_limit_fail) | (df[parameter_column] > upper_limit_fail)
#         df[f'Flag_{parameter_column}'] |= np.where(condition_fail, 4, 0)
#         alerta(alert_window_size, parameter_column, teste_continuidade_tempo.__name__, df) 
#     return df, inspect.currentframe().f_code.co_name

def teste_continuidade_tempo(df, limite_sigma_aceitavel_and_dict_delta_site, alert_window_size, parametros_direcionais):
    
    for parameter_column, config in limite_sigma_aceitavel_and_dict_delta_site.items():
        if parameter_column not in df.columns:
            continue  # ignora colunas ausentes

        window = config["window"]
        n_desvpad_fail = config["delta"]
        df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')

        flag_col = f'Flag_{parameter_column}'
        if flag_col not in df.columns:
            df[flag_col] = 0

        if parameter_column in parametros_direcionais:
            rolling_mean = df[parameter_column].rolling(window=window, min_periods=1).apply(circular_mean, raw=False)
            rolling_std = df[parameter_column].rolling(window=window, min_periods=1).apply(circular_std, raw=False)

            diffs = angular_diff(df[parameter_column], rolling_mean)
            limiar = n_desvpad_fail * rolling_std
            condition_fail = diffs > limiar
        else:
            rolling_mean = df[parameter_column].rolling(window=window, min_periods=1).mean()
            rolling_std = df[parameter_column].rolling(window=window, min_periods=1).std()
            upper_limit = rolling_mean + n_desvpad_fail * rolling_std
            lower_limit = rolling_mean - n_desvpad_fail * rolling_std
            condition_fail = (df[parameter_column] > upper_limit) | (df[parameter_column] < lower_limit)

        df[flag_col] |= np.where(condition_fail, 4, 0)
        alerta(alert_window_size, parameter_column, teste_continuidade_tempo.__name__, df)

    return df, inspect.currentframe().f_code.co_name




#Teste 9: Identificar duplicatas.
def identificar_duplicatas_tempo(df,parameter_columns,alert_window_size):
    # a função verifica se os valores de tempo não estão duplicados
    for parameter_column in parameter_columns:      
        duplicatas = df.index.duplicated()    
        df[f'Flag_{parameter_column}'] |= np.where(duplicatas, 4, 0)
        alerta(alert_window_size, parameter_column, identificar_duplicatas_tempo.__name__, df) 
    return df, inspect.currentframe().f_code.co_name


#Teste 10: Verificar dados repetidos.
def verifica_dados_repetidos(df, limite_repeticao_dados, alert_window_size,parameter_columns):
    for parameter_column in limite_repeticao_dados:
        if parameter_column not in parameter_columns:
            continue
        if parameter_column not in ["Tp_sea", "Tp_swell"]:

            fail = limite_repeticao_dados[parameter_column]["fail"]
            rolling_fail = df[parameter_column].rolling(window=fail)
            condition_fail = rolling_fail.apply(lambda x: len(set(x)) == 1, raw=True).dropna()
            df[f'Flag_{parameter_column}'] |= np.where(condition_fail.reindex(df.index, fill_value=False), 4, 0)
        alerta(alert_window_size, parameter_column, verifica_dados_repetidos.__name__, df)
    return df, inspect.currentframe().f_code.co_name

# Teste 11: ST Time series segment.
def st_time_series_segment_shift(df, st_time_series_dict, alert_window_size, parametros_direcionais): 
    for parameter_column, params in st_time_series_dict.items():

        if parameter_column not in df.columns:
            continue  # Ignora colunas que não existem no df

        # Cria coluna de flag se não existir
        flag_col = f'Flag_{parameter_column}'
        if flag_col not in df.columns:
            df[flag_col] = 0
        else:
            df[flag_col] = df[flag_col].fillna(0).astype(int)

        m_points = params['m_points']
        P = params['mean_shift_threshold']

        # Cria uma série temporária para trabalhar, convertendo para numérico
        temp_series = pd.to_numeric(df[parameter_column], errors='coerce')

        n_segments = len(temp_series) // m_points
        if n_segments < 2:
            continue  # não há segmentos suficientes para comparar

        segments = [temp_series.iloc[i * m_points : (i + 1) * m_points] for i in range(n_segments)]

        # Cálculo da média por segmento
        if parameter_column in parametros_direcionais or 'dir' in parameter_column.lower():
            # Direcionais: usa média angular
            segment_means = [mean_direction(segment.dropna()) for segment in segments]
        else:
            # Não direcionais: média normal
            segment_means = [segment.dropna().mean() for segment in segments]

        # Aplica o critério de mudança abrupta entre segmentos
        for i in range(1, len(segment_means)):
            diff_value = abs(segment_means[i] - segment_means[i - 1])

            if diff_value >= P:
                start_idx = i * m_points
                end_idx = (i + 1) * m_points

                # Garante que os índices não ultrapassem o DataFrame
                end_idx = min(end_idx, len(df))

                # Marca a flag com operação bitwise segura
                df.iloc[start_idx:end_idx, df.columns.get_loc(flag_col)] = (
                    df.iloc[start_idx:end_idx, df.columns.get_loc(flag_col)].astype(int) | 4
                )

        # Chama a função de alerta (suponho que ela já exista no seu código)
        alerta(alert_window_size, parameter_column, st_time_series_segment_shift.__name__, df)

    return df, inspect.currentframe().f_code.co_name


# Teste 12: Max Min.
def max_min_test(df, dict_max_min_test,parametros_direcionais): 
    for parameter_column, params in dict_max_min_test.items():
        if parameter_column not in df.columns:
            continue  # ignora colunas ausentes
        if parameter_column in parametros_direcionais:
            continue  # ignora dados direcionais
        delta = params["delta"]
        m_points = params["m_points"]
        #window_size = params["window_size"]
        window_size = len (df)
        df[parameter_column] = pd.to_numeric(df[parameter_column], errors='coerce')
        invalid_positions = df[parameter_column].isna()
        if invalid_positions.any():
            print(f"Valores não numéricos encontrados na coluna '{parameter_column}' nos índices: {df[invalid_positions].index.tolist()}")
        n_segments = window_size // m_points
        segments = [df.iloc[i * m_points: (i + 1) * m_points] for i in range(n_segments)]
        flag_col = f'Flag_{parameter_column}'
        if flag_col not in df.columns:
            df[flag_col] = 0
        for i, segment in enumerate(segments):
            segment_values = segment[parameter_column].values
            if 'dir' in parameter_column.lower():
                diffs = diferenca_angular(segment_values, np.roll(segment_values, -1))
                diffs[-1] = 0  # Manter o último valor em 0
                ampli_values = np.abs(diffs)
                df.loc[segment.index, flag_col] |= np.where(ampli_values >= delta, 4, 0)
            else:
                ampli_value = abs(segment[parameter_column].max() - segment[parameter_column].min())
                df.loc[segment.index, flag_col] |= np.where(ampli_value >= delta, 3, 0)
        alerta(window_size, parameter_column, max_min_test.__name__, df)
    return df, inspect.currentframe().f_code.co_name


#TESTE 13: Temperatura vs Ponto de orvalho
def verificar_temperatura_vs_ponto_de_orvalho(df,alert_window_size):
# a função verifica se o valor de velocidade do vento é maior que a rajada de vento.
    parameter_column='Dew Point'
    df['Flag_Dew Point'] |= np.where(df['Dew Point'] >= df['Temperature(*C)'], 4, 0)
    func_name = inspect.currentframe().f_code.co_name
    alerta(alert_window_size, parameter_column, func_name, df)
    return df, func_name   

#TESTE 14: Velocidade vs rajada
def verificar_velocidade_vs_rajada(df,alert_window_size):
# a função verifica se o valor de velocidade do vento é maior que a rajada de vento.
    parameter_column='Gust Speed(m/s)'
    df['Flag_Wind Speed(m/s)'] |= np.where(df['Wind Speed(m/s)'] > df['Gust Speed(m/s)'], 4, 0)
    func_name = inspect.currentframe().f_code.co_name
    alerta(alert_window_size, parameter_column, func_name, df)
    return df, func_name   

#TESTE 15: Verificar altura max vs sig
def verificar_altura_max_vs_sig(df,Hs,Hmax):
    
    
    df[f'Flag_{Hmax}'] |= np.where((df[Hs] > df[Hmax]), 4, 0)
    func_name = inspect.currentframe().f_code.co_name
    return df, func_name   

#TESTE 16: SIGNAL ADCP GRADIENT
import re
import inspect
import pandas as pd

def gradiente_de_amplitude_do_sinal(df):
    amplitude_columns = ['Amplitude']
    speed_columns = ['Speed']
    direction_columns = ['Direction']

    # Função para extrair número da célula da coluna
    def extrair_numero_celula(nome_coluna):
        match = re.search(r'Cell#(\d+)', nome_coluna)
        return int(match.group(1)) if match else -1

    # Função para criar dicionário {num_celula: nome_coluna}
    def criar_mapa_colunas(prefixos):
        colunas = [col for col in df.columns if any(col.startswith(p) for p in prefixos)]
        mapa = {extrair_numero_celula(col): col for col in colunas if extrair_numero_celula(col) != -1}
        return dict(sorted(mapa.items()))

    mapa_amplitude = criar_mapa_colunas(amplitude_columns)
    mapa_speed = criar_mapa_colunas(speed_columns)
    mapa_direction = criar_mapa_colunas(direction_columns)
    for col in set(mapa_amplitude.values()) | set(mapa_speed.values()) | set(mapa_direction.values()):
        df[col] = pd.to_numeric(df[col], errors='coerce')
    numeros_celulas = sorted(mapa_amplitude.keys())
    for i in range(1, len(numeros_celulas)):
        prev_num = numeros_celulas[i - 1]
        curr_num = numeros_celulas[i]
        prev_col = mapa_amplitude[prev_num]
        curr_col = mapa_amplitude[curr_num]
        condition_fail = df[curr_col] > df[prev_col]
        for idx in range(i, len(numeros_celulas)):
            num = numeros_celulas[idx]
            amp_col = mapa_amplitude[num]
            flag_amp = f"Flag_{amp_col}"
            if flag_amp not in df.columns:
                df[flag_amp] = 0
            df.loc[condition_fail & (df[flag_amp] == 0), flag_amp] = 4
            speed_col = mapa_speed.get(num)
            if speed_col:
                flag_speed = f"Flag_{speed_col}"
                if flag_speed not in df.columns:
                    df[flag_speed] = 0
                df.loc[condition_fail & (df[flag_speed] == 0), flag_speed] = 4
            direction_col = mapa_direction.get(num)
            if direction_col:
                flag_dir = f"Flag_{direction_col}"
                if flag_dir not in df.columns:
                    df[flag_dir] = 0
                df.loc[condition_fail & (df[flag_dir] == 0), flag_dir] = 4
    func_name = inspect.currentframe().f_code.co_name
    return df, func_name

#TESTE 17: Detectar platos verticais
# def detectar_platos(df, threshold_plato, categorias=["Amplitude", "Speed", "Direction"]):
#     for categoria in categorias:
#         threshold = threshold_plato[categoria]["threshold"]
#         window = threshold_plato[categoria]["window"]
#         categoria_columns = [col for col in df.columns if col.lower().startswith(categoria.lower())]
#         cell_numbers = [int(col.split('#')[1].split('_')[0]) for col in categoria_columns]
#         categoria_order = pd.DataFrame({'Cell': cell_numbers, 'Column': categoria_columns}).sort_values('Cell')
#         sorted_columns = categoria_order['Column'].tolist()
#         df[sorted_columns] = df[sorted_columns].apply(pd.to_numeric, errors='coerce')
#         for i in range(len(sorted_columns) - window + 1):
#             window_columns = sorted_columns[i:i + window]
#             for j in range(1, len(window_columns)):
#                 previous_col = window_columns[j - 1]
#                 current_col = window_columns[j]
#                 condition_plato = abs(df[current_col] - df[previous_col]) <= threshold
#                 flag_column_name = f"Flag_Plato_{categoria}_{current_col}"
#                 if flag_column_name not in df.columns:
#                     df[flag_column_name] = 0
#                 df[flag_column_name] |= np.where(condition_plato, 4, 0)
#     func_name = inspect.currentframe().f_code.co_name

#     return df,func_name

def detectar_platos(df, threshold_plato, categorias=["Amplitude", "Speed", "Direction"]):
    for categoria in categorias:
        threshold = threshold_plato[categoria]["threshold"]
        window = threshold_plato[categoria]["window"]
        categoria_columns = [col for col in df.columns if col.lower().startswith(categoria.lower())]
        cell_numbers = [int(col.split('#')[1].split('_')[0]) for col in categoria_columns]
        categoria_order = pd.DataFrame({'Cell': cell_numbers, 'Column': categoria_columns}).sort_values('Cell')
        sorted_columns = categoria_order['Column'].tolist()
        df[sorted_columns] = df[sorted_columns].apply(pd.to_numeric, errors='coerce')
        for i in range(len(sorted_columns) - window + 1):
            window_columns = sorted_columns[i:i + window]
            is_plato = pd.Series(True, index=df.index)
            for j in range(1, len(window_columns)):
                diff = abs(df[window_columns[j]] - df[window_columns[j - 1]])
                is_plato &= diff <= threshold
            for col in window_columns:
                flag_col = f"Flag_{col}"
                if flag_col not in df.columns:
                    df[flag_col] = 0
                df[flag_col] = np.where(is_plato, np.maximum(df[flag_col], 4), df[flag_col])
    func_name = inspect.currentframe().f_code.co_name
    return df, func_name

#TESTE 18: Taxa de mudanca vertical

def taxa_de_mudanca_vertical(df, threshold_mudanca_abrupta, categorias=["amplitude", "speed", "direction"]):
    for categoria in categorias:
        threshold = threshold_mudanca_abrupta[categoria]["threshold"]
        window = threshold_mudanca_abrupta[categoria]["window"]
        categoria_columns = [col for col in df.columns if col.lower().startswith(categoria.lower())]
        cell_numbers = [int(col.split('#')[1].split('_')[0]) for col in categoria_columns]
        categoria_order = pd.DataFrame({'Cell': cell_numbers, 'Column': categoria_columns}).sort_values('Cell')
        sorted_columns = categoria_order['Column'].tolist()
        df[sorted_columns] = df[sorted_columns].apply(pd.to_numeric, errors='coerce')
        for i in range(len(sorted_columns) - window + 1):
            window_columns = sorted_columns[i:i + window]
            for j in range(1, len(window_columns)):
                previous_col = window_columns[j - 1]
                current_col = window_columns[j]
                condition_fail = abs(df[current_col] - df[previous_col]) > threshold
                flag_column_name = f"Flag_{current_col}"
                if flag_column_name not in df.columns:
                    df[flag_column_name] = 0
                df[flag_column_name] |= np.where(condition_fail, 4, 0)
    func_name = inspect.currentframe().f_code.co_name
    return df,func_name



##FIXME

