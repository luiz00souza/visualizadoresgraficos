import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Comparação de Marés", layout="wide")
st.title("📊 Comparação de Marés - Upload de Arquivos .tid")
st.markdown("""
Este aplicativo permite comparar séries de marés de dois arquivos `.tid`.  
Faça upload dos arquivos e visualize as séries temporais individuais, o comparativo e o residual.
""")

# Upload dos arquivos
uploaded_file1 = st.file_uploader("Escolha o primeiro arquivo (.tid)", type=["tid"])
uploaded_file2 = st.file_uploader("Escolha o segundo arquivo (.tid)", type=["tid"])

# Função para ler .tid
def ler_tid(file):
    df = pd.read_csv(file, delim_whitespace=True, skiprows=1, header=None, engine='python')
    df['tempo'] = df[0] + ' ' + df[1].astype(str)
    df['valor'] = df[2]
    df['tempo'] = pd.to_datetime(df['tempo'], format='%Y/%m/%d %H:%M:%S', errors='coerce')
    df = df.dropna(subset=['tempo'])
    df.set_index('tempo', inplace=True)
    return df[['valor']]

if uploaded_file1 and uploaded_file2:
    # Extrair nomes dos arquivos sem extensão
    label1 = os.path.splitext(uploaded_file1.name)[0]
    label2 = os.path.splitext(uploaded_file2.name)[0]

    # Ler arquivos
    df1 = ler_tid(uploaded_file1)
    df2 = ler_tid(uploaded_file2)

    # Interseção de datas
    tempo_comum = df1.index.intersection(df2.index)
    df1_comum = df1.loc[tempo_comum]
    df2_comum = df2.loc[tempo_comum]

    # Residual
    residual = df1_comum['valor'] - df2_comum['valor']

    # Criar abas para cada gráfico
    tabs = st.tabs([f"{label1}", f"{label2}", "Comparativo + Residual"])
    
    # Aba 1 - Série temporal primeiro arquivo
    with tabs[0]:
        st.subheader(f"Série Temporal - {label1}")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df1.index, y=df1['valor'], mode='lines', name=label1, line=dict(color='blue')))
        fig1.update_layout(xaxis_title='Tempo', yaxis_title='Altura da Maré', height=400)
        st.plotly_chart(fig1, use_container_width=True)

    # Aba 2 - Série temporal segundo arquivo
    with tabs[1]:
        st.subheader(f"Série Temporal - {label2}")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df2.index, y=df2['valor'], mode='lines', name=label2, line=dict(color='red')))
        fig2.update_layout(xaxis_title='Tempo', yaxis_title='Altura da Maré', height=400)
        st.plotly_chart(fig2, use_container_width=True)

    # Aba 3 - Comparativo + Residual
    with tabs[2]:
        st.subheader("Comparativo entre sensores + Residual")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df1_comum.index, y=df1_comum['valor'], mode='lines', name=label1, line=dict(color='blue')))
        fig3.add_trace(go.Scatter(x=df2_comum.index, y=df2_comum['valor'], mode='lines', name=label2, line=dict(color='red')))
        fig3.add_trace(go.Scatter(x=df1_comum.index, y=residual, mode='lines', name='Residual', line=dict(color='green')))
        fig3.update_layout(xaxis_title='Tempo', yaxis_title='Altura / Diferença', height=500)
        st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("📌 Faça upload de **dois arquivos .tid** para visualizar os gráficos.")
