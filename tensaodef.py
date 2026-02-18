import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide")
st.title("Deformação × Tensão por amostra")

# ===== Arquivo exemplo no repo
ARQUIVO_EXEMPLO = "dados_exemplo_tensao_deformormacao.csv"

COL_X = "Deformação à flexão (Deslocamento)"
COL_Y = "Tensão à flexão"
COL_ID = "amostra"


# =============================
# SELETOR DE FONTE DE DADOS
# =============================

modo = st.radio(
    "Fonte dos dados:",
    ["Usar arquivo exemplo", "Enviar meu CSV"],
    horizontal=True
)

if modo == "Usar arquivo exemplo":

    if os.path.exists(ARQUIVO_EXEMPLO):
        df = pd.read_csv(ARQUIVO_EXEMPLO)
        st.success("Usando arquivo exemplo do repositório")
    else:
        st.error("Arquivo exemplo não encontrado no diretório")
        st.stop()

else:
    arquivo = st.file_uploader("Envie o CSV", type=["csv"])
    if not arquivo:
        st.stop()
    df = pd.read_csv(arquivo)


# =============================
# VALIDAÇÃO
# =============================

for c in [COL_X, COL_Y, COL_ID]:
    if c not in df.columns:
        st.error(f"Coluna não encontrada: {c}")
        st.stop()

df = df.copy()
df[COL_ID] = df[COL_ID].astype(str).str.strip()
df["grupo"] = df[COL_ID].str[0].str.upper()


# =============================
# FUNÇÕES
# =============================

def r2_score(y, yhat):
    y = np.asarray(y)
    yhat = np.asarray(yhat)
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1.0 - (ss_res / ss_tot) if ss_tot != 0 else np.nan


def plot_grupo(df_grupo, titulo):

    fig = go.Figure()

    for amostra, d in df_grupo.groupby(COL_ID):

        d = d.copy()

        d[COL_X] = pd.to_numeric(d[COL_X], errors="coerce")
        d[COL_Y] = pd.to_numeric(d[COL_Y], errors="coerce")
        d = d.dro
