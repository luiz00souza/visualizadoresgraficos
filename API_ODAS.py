"""
Created on Wed Nov 19 14:48:26 2025

@author: campo
"""

import requests
import pandas as pd
import requests
import os
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import signal as sgn
import matplotlib.pylab as plt
import matplotlib.pyplot as plt
url = "https://sdecsistema.com.br/v2umi747371/api_webhook_export.php"

payload_base = {
    "Client_ID": "CLIENT_123456",
    "Secret_ID": "SECRET_ABCDEF",
}

import time

def get_df_all(start="2025-12-04", end=None, max_retries=10, retry_delay=5):
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = payload_base.copy()
    payload["start_date"] = start
    payload["end_date"] = end

    headers = {"Connection": "close"}
    retries = 0

    while retries < max_retries:
        try:
            with requests.Session() as s:
                response = s.post(url, json=payload, headers=headers, verify=False)
                response.raise_for_status()

            data = response.json()
            df = pd.DataFrame(data["registros"])

            df["timestamp_utc"] = (
                pd.to_datetime(df["data"] + " " + df["hora"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
                .dt.round("5min")
                + pd.Timedelta(hours=3)
            )

            df = df[["timestamp_utc", "nivel", "nivel2", "serialnumber"]]
            df = df.sort_values(["serialnumber", "timestamp_utc"]).reset_index(drop=True)

            df = df.rename(columns={"serialnumber": "sensor_sn"})
            df["sensor_sn"] = df["sensor_sn"].astype(str)
            df["sensor_sn"] = df["sensor_sn"].replace({
                "01057818SKY0ABF": "10915285",
                "_182": "21663145"
            })

            return df

        except (requests.ConnectionError,
                requests.Timeout,
                requests.exceptions.SSLError,
                requests.exceptions.ChunkedEncodingError,
                ValueError) as e:

            retries += 1
            print(f"Erro de conexão ({e}). Tentando novamente {retries}/{max_retries}...")

            if retries >= max_retries:
                print("Máximo de tentativas alcançado. Não foi possível recuperar os dados.")
                return None

            time.sleep(retry_delay + random.uniform(0, 0.8))

def carregar_config_txt(caminho_arquivo):
    config = {}
    with open(caminho_arquivo, 'r') as f:
        for linha in f:
            if '=' in linha:
                chave, valor = linha.strip().split('=', 1)
                config[chave.strip()] = valor.strip()
    return config

# === Função para verificar sensores ativos ===
def obter_sensores_ativos(df):
    sensores = df["sensor_sn"].dropna().unique().tolist()
    sensores.sort()
    print(f"📡 Sensores ativos encontrados: {sensores}")
    return sensores

# === Função para aplicar calibração, redução e filtro ===
def processar_sensor(df, a, b, reducao, filtromare):
    df = df.copy()

    # Garantir timestamp_utc limpo
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], errors="coerce")

    # Calibração
    df["dados_calibrados_reduzidos"] = (a * df["nivel2"] + b) - reducao

    # Frequência equivalente (5 min): fs=1/300 Hz; Nyquist = fs/2
    Wa = 0.00083333333333335  

    if filtromare == 1:
        Wc = 0.000224014336917
        order = 4
    elif filtromare == 2:
        Wc = 0.0000224014336917
        order = 4
    else:
        raise ValueError("Filtro inválido: escolha 1 (fraco) ou 2 (médio)")

    Wn = (2 * Wc) / Wa
    if not (0 < Wn < 1):
        raise ValueError(f"Wn fora do intervalo (0,1): {Wn}")

    # Coeficientes do filtro
    b_filt, a_filt = sgn.butter(order, Wn, btype='lowpass')

    # -----------------------------
    # Ignorar None/NaN antes de filtrar
    # -----------------------------
    serie = df["dados_calibrados_reduzidos"]

    # Índices válidos
    mask_valid = serie.notna()

    # Se não houver pontos suficientes, evita crash
    if mask_valid.sum() < (order * 3):
        df["tide_filtrada"] = np.nan
        return df

    # Filtrar apenas o trecho válido
    filtrado = sgn.filtfilt(
        b_filt, a_filt,
        serie[mask_valid].astype(float),
        padtype=None
    )

    # Colocar NaN de volta no lugar
    resultado = pd.Series(np.nan, index=df.index)
    resultado[mask_valid] = filtrado

    df["tide_filtrada"] = resultado

    return df


    return df
    
# df_banco_mare = pd.DataFrame() 

def filtrar_por_sensor(df: pd.DataFrame, sensor_sn: str) -> pd.DataFrame:
    df_filtrado = df[df['sensor_sn'] == sensor_sn].drop(columns=['sensor_sn', 'nivel'])
    df_filtrado = df_filtrado.rename(columns={'nivel2': 'Pressure_S1', 'timestamp_utc': 'GMT-03:00'})
    df_filtrado['Pressure_S2'] = np.nan
    df_filtrado['Battery(v)'] = np.nan
    df_filtrado['Pressure_S1'] = pd.to_numeric(df_filtrado['Pressure_S1'], errors='coerce')

    return df_filtrado
# sensor_sn='10915285'
# df=filtrar_por_sensor(get_df_all(), sensor_sn)



