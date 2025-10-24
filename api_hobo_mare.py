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
def acesso_API_HOBBO_mare(parameter_columns_mare,start,logger_ids):
    # Execução principal
    client = HobolinkClient(access_token)
    
    # start = "2025-05-05 10:00:00"
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    logger_ids=logger_ids
    df = client.get_data(logger_ids, start, end)
    
    # Conversão do timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Cria um rótulo mais descritivo para os sensores
    df["sensor_label"] = df["sensor_measurement_type"] + " (" + df["sensor_sn"] + ")"
    # Conversão do timestamp e formatação
    
    # Converte para formato wide
    df_wide = df.pivot_table(
        index="timestamp",
        columns="sensor_label",
        values="value",
        aggfunc="first"
    ).reset_index()


    # Verifica se o número de colunas bate com o DataFrame
    if len(df_wide.columns) == len(parameter_columns_mare):
        df_wide.columns = parameter_columns_mare
    else:
        raise ValueError("Número de colunas no DataFrame não corresponde ao número de nomes fornecidos.")
    
    return df_wide,parameter_columns_mare
# parameter_columns_mare = [ 
#     'GMT-03:00', 
#     'Battery(v)',
#     'Pressure_S1',
#     'Pressure_S2',
# ]
# df_mare,parameter_columns_mare= acesso_API_HOBBO_mare (parameter_columns_mare,start = "2025-05-05 10:00:00",logger_ids = ["21122423"])
# df_mare,parameter_columns_mare= acesso_API_HOBBO_mare (parameter_columns_mare,start = "2025-09-21 10:00:00",logger_ids = ["10915285"])
