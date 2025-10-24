import os
import io
import streamlit as st
import pandas as pd
import plotly.express as px
from backend_mare import *
from OPERACIONAL_UMI_SIMPLIFICADO import processar_sensor

st.set_page_config(page_title="🌊 Monitoramento de Maré", layout="wide")

# ================================
# Home Page Inicial
# ================================
st.title("🌊 Monitoramento de Maré - Estações Interativas")
st.markdown("""
Bem-vindo(a) ao painel de monitoramento de maré.  
Selecione uma estação na barra lateral para carregar os dados e visualizar informações, gráficos e mapas interativos.
""")

# ================================
# SIDEBAR PARA SELEÇÃO DE ESTAÇÃO
# ================================
caminho_config = "f_configSensores.csv"
sensores_disponiveis = [6, 7, 8]
nomes_sensores = {6:"TIG",7:"JAGUANUM",8:"ITAGUAI"}

st.sidebar.title("📍 Estações Disponíveis")
registro_selecionado = st.sidebar.selectbox(
    "Selecione a Estação:",
    options=[None] + sensores_disponiveis,
    format_func=lambda x: nomes_sensores.get(x, "") if x else "Nenhuma"
)

# ================================
# Função para carregar dados do sensor
# ================================
@st.cache_data(show_spinner=False)
def carregar_dados_sensor(registro_id):
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
        df_filtrado = df[[time_col, height_col]].copy()
        df_filtrado = df_filtrado.rename(columns={time_col: "Tempo", height_col: "Altura da Maré (m)"})

        return {
            "df": df_filtrado,
            "resultados": resultados,
            "lat": lat,
            "lon": lon,
            "nome": nomes_sensores.get(registro_id, f"Estação {registro_id}"),
            "df_config": df_config
        }
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar sensor {registro_id}: {e}")
        return {
            "df": pd.DataFrame(),
            "resultados": {},
            "lat": None,
            "lon": None,
            "nome": f"Estação {registro_id}",
            "df_config": pd.DataFrame()
        }

# ================================
# Carregar dados apenas se uma estação for selecionada
# ================================
if registro_selecionado:
    dados = carregar_dados_sensor(registro_selecionado)
    df = dados["df"]

    # ================================
    # TABS PRINCIPAL
    # ================================
    tabs = st.tabs(["📊 Visualização", "💾 Exportar Dados", "ℹ️ Informações", "🗺️ Mapa das Estações"])

    # --- Aba Visualização ---
    with tabs[0]:
        st.subheader(f"Altura da Maré - {dados['nome']}")
        if not df.empty:
            fig = px.line(df, x="Tempo", y="Altura da Maré (m)",
                          labels={"Tempo":"Tempo (GMT-3)", "Altura da Maré (m)":"Altura da Maré (m)"},
                          color_discrete_sequence=["#0096c7"])
            fig.update_layout(height=450, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Nenhum dado disponível para esta estação.")

    # --- Aba Exportação ---
    with tabs[1]:
        st.subheader(f"Exportar dados da estação {dados['nome']}")
        pasta = r"C:\Users\campo\Desktop\SistamaQAQC\DASH\export_tides"

        # Salvar .tid
        if not df.empty and st.button(f"💾 Salvar {dados['nome']} como .tid"):
            os.makedirs(pasta, exist_ok=True)
            data_inicial = df["Tempo"].min().strftime("%Y%m%d")
            data_final = df["Tempo"].max().strftime("%Y%m%d")
            nome_arquivo = f"MeuProjeto_{dados['nome']}_{data_inicial}_{data_final}_UTC.tid"
            caminho_completo = os.path.join(pasta, nome_arquivo)
            with open(caminho_completo, "w") as f:
                f.write("--------\tNaN\n")
                for i in range(len(df)):
                    f.write("%s %6.3f\n" % (
                        df["Tempo"].iloc[i].strftime("%Y/%m/%d %H:%M:%S"),
                        df["Altura da Maré (m)"].iloc[i]
                    ))
            st.success(f"✅ Arquivo .tid salvo: {caminho_completo}")

        # Download CSV
        if not df.empty:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label=f"⬇️ Baixar {dados['nome']} como CSV",
                data=csv_buffer.getvalue(),
                file_name=f"{dados['nome']}_dados_mare.csv",
                mime="text/csv"
            )

    # --- Aba Informações ---
    with tabs[2]:
        st.subheader(f"ℹ️ Informações da Estação - {dados['nome']}")
        st.markdown("**📌 Dados gerais:**")
        st.write(f"**Nome da Estação:** {dados['nome']}")
        st.write(f"**Latitude:** {dados['lat']}")
        st.write(f"**Longitude:** {dados['lon']}")
        st.write(f"**Número de registros na série temporal:** {len(df)}")

        df_config = dados.get("df_config", pd.DataFrame())
        if not df_config.empty:
            st.markdown("**⚙️ Configuração do Sensor (df_config):**")
            colunas_relevantes = [
                "RegistroID","cp_guid_sensor","SensorID","EstacaoID","ProjetoID","tipo_sensor",
                "conexao_sensor","nome_sensor","serial_sensor","frequencia_sensor",
                "filtros_ativos_qc_sensor","numero_celulas_sensor","declinacao_magnetica_sensor",
                "reducao_sensor","a_sensor","b_sensor","start_data","ativar_previsao_futura",
                "ativar_preenchimento_gaps","forecast_days","tipo_de_filtro","height_col",
                "lat_estacao","long_estacao","nome_projeto","nome_cliente_projeto"
            ]
            colunas_exibir = [c for c in colunas_relevantes if c in df_config.columns]
            st.dataframe(df_config[colunas_exibir].T, use_container_width=True)
        else:
            st.info("Nenhuma configuração detalhada disponível para este sensor.")

    # --- Aba Mapa ---
    with tabs[3]:
        st.subheader("🗺️ Localização das Estações")
        lista_estacoes = []
        for reg in sensores_disponiveis:
            dados_est = carregar_dados_sensor(reg)
            if dados_est["lat"] is not None and dados_est["lon"] is not None:
                lista_estacoes.append({"Nome": dados_est["nome"], "Latitude": dados_est["lat"], "Longitude": dados_est["lon"]})
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

