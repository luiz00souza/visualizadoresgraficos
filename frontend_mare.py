# -*- coding: utf-8 -*-
import io
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from backend_mare import *
from OPERACIONAL_UMI_SIMPLIFICADO import processar_sensor

# ================================
# CONFIGURAÇÃO DA PÁGINA
# ================================
st.set_page_config(page_title="🌊 Monitoramento de Maré", layout="wide")

# Caminho do arquivo de configuração
caminho_config = "f_configSensores.csv"

# ================================
# HOME PAGE INICIAL
# ================================
st.title("🌊 Monitoramento de Maré - Estações Interativas")
st.markdown("""
Bem-vindo(a) ao painel de monitoramento de maré.  
Selecione uma estação na barra lateral para carregar os dados e visualizar informações, gráficos e mapas interativos.
""")

# ================================
# SIDEBAR PARA SELEÇÃO DE ESTAÇÃO
# ================================
sensores_disponiveis = [7, 8]
nomes_sensores = {7: "JAGUANUM", 8: "ITAGUAI"}

st.sidebar.title("📍 Estações Disponíveis")
registro_selecionado = st.sidebar.selectbox(
    "Selecione a Estação:",
    options=[None] + sensores_disponiveis,
    format_func=lambda x: nomes_sensores.get(x, "") if x else "Nenhuma"
)

# ================================
# FUNÇÃO PARA CARREGAR DADOS DO SENSOR
# ================================
@st.cache_data(ttl=300, show_spinner=False)
def carregar_dados_sensor(registro_id):
    """
    Carrega os dados do sensor e os mantém em cache por 5 minutos (TTL = 300 s)
    """
    try:
        ret = processar_sensor(registro_id=registro_id, caminho_config=caminho_config)
        df = ret[0]
        resultados = ret[1]
        lat = ret[2]
        lon = ret[3]
        df_config = ret[4] if len(ret) >= 5 else pd.DataFrame()

        # Colunas de tempo e altura
        time_col = "GMT-03:00" if "GMT-03:00" in df.columns else df.columns[0]
        height_col = "Altura Final" if "Altura Final" in df.columns else df.columns[-1]

        # Cria cópia e corrige timezone (remove tzinfo se existir)
        df_filtrado = df[[time_col, height_col]].copy()
        df_filtrado[time_col] = pd.to_datetime(df_filtrado[time_col], errors="coerce")

        # Remove timezone se houver (evita erro de +3h)
        if pd.api.types.is_datetime64tz_dtype(df_filtrado[time_col]):
            df_filtrado[time_col] = df_filtrado[time_col].dt.tz_localize(None)

        # Renomeia colunas
        df_filtrado = df_filtrado.rename(columns={time_col: "Tempo", height_col: "Altura da Maré (m)"})

        # Marca horário da atualização
        hora_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        return {
            "df": df_filtrado,
            "resultados": resultados,
            "lat": lat,
            "lon": lon,
            "nome": nomes_sensores.get(registro_id, f"Estação {registro_id}"),
            "df_config": df_config,
            "hora_atualizacao": hora_atualizacao
        }

    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar sensor {registro_id}: {e}")
        return {
            "df": pd.DataFrame(),
            "resultados": {},
            "lat": None,
            "lon": None,
            "nome": f"Estação {registro_id}",
            "df_config": pd.DataFrame(),
            "hora_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

# ================================
# EXIBIÇÃO PRINCIPAL
# ================================
if registro_selecionado:
    dados = carregar_dados_sensor(registro_selecionado)
    df = dados["df"]

    st.info(f"⏱️ Última atualização automática: **{dados['hora_atualizacao']}** (atualiza a cada 5 min)")

    tabs = st.tabs(["📊 Visualização", "💾 Exportar Dados", "ℹ️ Informações", "🗺️ Mapa das Estações"])

    # --- Aba Visualização ---
    with tabs[0]:
        st.subheader(f"Altura da Maré - {dados['nome']}")
        if not df.empty:
            fig = px.line(
                df,
                x="Tempo",
                y="Altura da Maré (m)",
                labels={"Tempo": "Tempo (UTC-3)", "Altura da Maré (m)": "Altura da Maré (m)"},
                color_discrete_sequence=["#0096c7"]
            )
            fig.update_layout(
                height=500,
                template="plotly_white",
                margin=dict(l=40, r=40, t=40, b=40),
                xaxis=dict(
                    rangeslider=dict(
                        visible=True,
                        thickness=0.12,
                        bgcolor="rgba(240,240,240,0.9)"
                    ),
                    rangeselector=dict(
                        buttons=list([
                            dict(count=6, label="6h", step="hour", stepmode="backward"),
                            dict(count=12, label="12h", step="hour", stepmode="backward"),
                            dict(count=1, label="1d", step="day", stepmode="backward"),
                            dict(count=7, label="7d", step="day", stepmode="backward"),
                            dict(step="all", label="Tudo")
                        ])
                    ),
                    type="date"
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Nenhum dado disponível para esta estação.")

    # --- Aba Exportação ---
    with tabs[1]:
        st.subheader(f"Exportar dados da estação {dados['nome']}")
        if not df.empty:
            # Exportar CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label=f"⬇️ Baixar {dados['nome']} como CSV",
                data=csv_buffer.getvalue(),
                file_name=f"{dados['nome']}_dados_mare.csv",
                mime="text/csv"
            )

            # Exportar .tid
            tid_buffer = io.StringIO()
            tid_buffer.write("--------\tNaN\n")
            for i in range(len(df)):
                tid_buffer.write("%s %6.3f\n" % (
                    df["Tempo"].iloc[i].strftime("%Y/%m/%d %H:%M:%S"),
                    df["Altura da Maré (m)"].iloc[i]
                ))
            st.download_button(
                label=f"💾 Baixar {dados['nome']} como .tid",
                data=tid_buffer.getvalue(),
                file_name=f"{dados['nome']}_dados_mare.tid",
                mime="text/plain"
            )

    # --- Aba Informações ---
    with tabs[2]:
        st.subheader(f"ℹ️ Informações da Estação - {dados['nome']}")
        st.markdown("**📌 Dados gerais:**")
        st.write(f"**Nome da Estação:** {dados['nome']}")
        # st.write(f"**Latitude:** {dados['lat']}")
        # st.write(f"**Longitude:** {dados['lon']}")
        # st.write(f"**Número de registros:** {len(df)}")

    # --- Aba Mapa ---
    with tabs[3]:
        st.subheader("🗺️ Localização das Estações")
        lista_estacoes = []
        for reg in sensores_disponiveis:
            dados_est = carregar_dados_sensor(reg)
            if dados_est["lat"] is not None and dados_est["lon"] is not None:
                lista_estacoes.append({
                    "Nome": dados_est["nome"],
                    "Latitude": dados_est["lat"],
                    "Longitude": dados_est["lon"]
                })
        df_mapa = pd.DataFrame(lista_estacoes)
        if not df_mapa.empty:
            fig_map = px.scatter_mapbox(
                df_mapa,
                lat="Latitude",
                lon="Longitude",
                hover_name="Nome",
                zoom=5,
                height=500,
                mapbox_style="open-street-map"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Nenhuma estação com coordenadas válidas para exibir no mapa.")
