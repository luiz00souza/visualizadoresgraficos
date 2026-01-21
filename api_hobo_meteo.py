# hobolink_client.py
import requests
import pandas as pd
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Token da API HOBOlink
access_token = "WoEQBNXYLT3uKCoMIEd3KeZAZ2jTDmDbhEyyjBJEjKj5V4dI"

class HobolinkClient:
    def __init__(self, token: str):
        self.base_url = "https://api.licor.cloud/v1/data"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

    def get_data(self, logger_ids: list, start: str, end: str):
        params = {
            "loggers": ",".join(logger_ids),
            "start_date_time": start,
            "end_date_time": end
        }

        response = requests.get(self.base_url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        return pd.DataFrame(data)
def acesso_API_HOBBO_meteo(parameter_columns_meteo,start,logger_ids):
    # Execução principal
    client = HobolinkClient(access_token)
    
    # start = "2025-04-24 10:00:00"
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # logger_ids = ["21663137"]
    
    df = client.get_data(logger_ids, start, end)
    if "timestamp" in df.columns:
        df = df.rename(columns={"timestamp": "GMT-03:00"})

    # Conversão do timestamp
    df["GMT-03:00"] = pd.to_datetime(df["GMT-03:00"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Cria um rótulo mais descritivo para os sensores
    df["sensor_label"] = df["sensor_measurement_type"] + " (" + df["sensor_sn"] + ")"
    # Conversão do timestamp e formatação
    print(df["sensor_measurement_type"].value_counts())

    df_wide=df

    df_wide = df.pivot_table(
        index="GMT-03:00",
        columns="sensor_measurement_type",
        values="value",
        aggfunc="first").reset_index()
    # df_wide = df_wide.rename(columns=sensor_map)

    # Verifica se o número de colunas bate com o DataFrame
    # if len(df_wide.columns) == len(parameter_columns_meteo):
    #     # df_wide.columns = parameter_columns_meteo

    # else:
    #     # print(len(df_wide.columns))
    #     raise ValueError(f"Número de colunas no DataFrame não corresponde ao número de nomes fornecidos. Numero de colunas esperado {len(df_wide.columns)}")
    
    return df_wide
sensor_map = {
    "Battery": "Battery__(v)",
    "Dew Point": "Dew Point",
    "Gust Speed": "Gust Speed(m/s)",
    "Pressure": "Pressure(hPa)",
    "RH": "RH(%)",
    "Rain": "Rain",
    "Temperature": "Temperature(*C)",
    "Wind Direction": "Wind Direction(*)",
    "Wind Speed": "Wind Speed(m/s)"
}

parameter_columns_meteo=1

# df= acesso_API_HOBBO_meteo(parameter_columns_meteo, start="2025-09-03 11:00:00", logger_ids=["21663137"])
