# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import os

# -----------------------
# Config geral
# -----------------------
st.set_page_config(page_title="🛰 CoastalHub — Dark Neuro UI", layout="wide")
CSV_PATH = os.path.join(os.path.dirname(__file__), "estacoes.csv")
VARIAVEIS = ["Hs", "Tp", "Direcao", "Vento", "Nivel", "Corrente"]
ICONES = {"Hs": "🌊", "Tp": "⏱", "Direcao": "🧭", "Vento": "💨", "Nivel": "🌡", "Corrente": "🌐"}
COLOR_SERIES = {"Hs":"#2E86AB","Tp":"#FF8C42","Direcao":"#2CA02C","Vento":"#D62828","Nivel":"#6A4C93","Corrente":"#8C5C4B"}

# -----------------------
# CSS Dark + Neuro Design
# -----------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root { --bg:#0f1113; --card:#121416; --muted:#98A4AB; --accent:#2E86AB; }
[data-testid="stAppViewContainer"] { background-color: var(--bg) !important; color: #E6EEF6 !important; font-family: "Inter", sans-serif; }
[data-testid="stHeader"] { background-color: var(--bg) !important; }
[data-testid="stSidebar"] { background-color: #0b0c0e !important; color: #e6eef6 !important; }

/* Cards */
.app-card {
    text-align: center;
    padding: 18px 14px;
    border-radius: 14px;
    transition: transform .18s ease, box-shadow .18s ease;
    color: #eaf4ff;
    cursor: pointer;
    position: relative;
    min-height: 110px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
}
.app-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 30px rgba(0,0,0,0.6);
}
.app-icon { font-size: 36px; margin-bottom: 6px; filter: drop-shadow(0 1px 2px rgba(0,0,0,0.6)); }
.app-name { font-size: 15px; font-weight: 700; margin-bottom:2px; color:#F1F8FF }
.tooltip {
    visibility: hidden;
    background: linear-gradient(180deg, rgba(20,20,20,0.98), rgba(28,28,28,0.98));
    color: #e6eef6;
    text-align: left;
    border-radius: 8px;
    padding: 10px;
    position: absolute;
    z-index: 3;
    bottom: 115%;
    left: 50%;
    transform: translateX(-50%);
    width: 300px;
    font-size: 13px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.6);
}
.app-card:hover .tooltip { visibility: visible; }

/* small helper */
.small-muted { color: #9AA6B2; font-size:13px; }
.btn-ghost { 
    background:transparent; 
    border:1px solid rgba(255,255,255,0.06); 
    color:#e6eef6; 
    padding:6px 10px; 
    border-radius:8px; 
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# CSV default
# -----------------------
def create_default_csv(path):
    df0 = pd.DataFrame([
        {"nome":"Praia de Itaparica - Vila Velha","localizacao":"Vila Velha","lat":-20.334,"lon":-40.312,
         "limite_inf_Hs":0.3,"limite_sup_Hs":2.0,"limite_inf_Tp":4.0,"limite_sup_Tp":12.0,
         "limite_inf_Direcao":0.0,"limite_sup_Direcao":360.0,"limite_inf_Vento":0.0,"limite_sup_Vento":10.0,
         "limite_inf_Nivel":0.0,"limite_sup_Nivel":0.8,"limite_inf_Corrente":0.0,"limite_sup_Corrente":1.5},
        {"nome":"Porto de Tubarão - Serra","localizacao":"Serra","lat":-20.147,"lon":-40.315,
         "limite_inf_Hs":0.3,"limite_sup_Hs":2.5,"limite_inf_Tp":4.0,"limite_sup_Tp":13.0,
         "limite_inf_Direcao":0.0,"limite_sup_Direcao":360.0,"limite_inf_Vento":0.0,"limite_sup_Vento":12.0,
         "limite_inf_Nivel":0.0,"limite_sup_Nivel":1.0,"limite_inf_Corrente":0.0,"limite_sup_Corrente":1.8},
        {"nome":"Baía de Vitória - Vitória","localizacao":"Vitória","lat":-20.319,"lon":-40.337,
         "limite_inf_Hs":0.3,"limite_sup_Hs":2.0,"limite_inf_Tp":4.0,"limite_sup_Tp":12.0,
         "limite_inf_Direcao":0.0,"limite_sup_Direcao":360.0,"limite_inf_Vento":0.0,"limite_sup_Vento":10.0,
         "limite_inf_Nivel":0.0,"limite_sup_Nivel":0.9,"limite_inf_Corrente":0.0,"limite_sup_Corrente":1.6}
    ])
    df0.to_csv(path, index=False)

if not os.path.exists(CSV_PATH):
    create_default_csv(CSV_PATH)

# -----------------------
# Load / save stations
# -----------------------
@st.cache_data(ttl=30)
def load_stations(path):
    return pd.read_csv(path)

def save_stations(df, path):
    df.to_csv(path,index=False)
    try: load_stations.clear()
    except: pass

stations_df = load_stations(CSV_PATH)
stations_df = load_stations(CSV_PATH)  # Reload

# -----------------------
# Simular séries temporais
# -----------------------
def gerar_dados_simulados(seed_offset=0, n=144):
    rng = np.random.default_rng(1234 + seed_offset)
    datas = pd.date_range(end=datetime.now(), periods=n, freq="H")
    return pd.DataFrame({
        "datetime": datas,
        "Hs": rng.uniform(0.3, 2.6, n),
        "Tp": rng.uniform(4, 15, n),
        "Direcao": rng.uniform(0, 360, n),
        "Vento": rng.uniform(0, 12, n),
        "Nivel": rng.uniform(0.0, 1.2, n),
        "Corrente": rng.uniform(0.0, 1.9, n)
    })

DATA = {}
for i, row in stations_df.iterrows():
    DATA[row["nome"]] = gerar_dados_simulados(seed_offset=i)

# -----------------------
# Session state
# -----------------------
if "selected_station" not in st.session_state: st.session_state.selected_station = None
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False
if "edited_stations" not in st.session_state: st.session_state.edited_stations = stations_df.copy()

# -----------------------
# Header
# -----------------------
col1, col2 = st.columns([6,2])
with col1:
    st.markdown("<h1 style='color:white; margin:0;'>🛰 CoastalHub — Monitoramento Inteligente</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='small-muted'>
    Bem-vindo ao CoastalHub! Aqui você pode monitorar ondas, vento, corrente e nível do mar das principais estações costeiras.<br>
    Siga os passos abaixo para explorar os dados:
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#121416; padding:12px; border-radius:10px; margin-bottom:12px;'>
    <b>Passo a passo:</b>
    <ol style='margin-left:15px; color:#E6EEF6;'>
    <li>Observe os cards das estações abaixo. Os ícones 🔴 e 🟢 indicam se algum parâmetro ultrapassou o limite ou está dentro do limite.</li>
    <li>Clique em um card para abrir o <b>dashboard</b> da estação.</li>
    <li>No dashboard, você pode <b>selecionar quais variáveis deseja visualizar</b>. A ordem e quantidade de gráficos ficam a seu critério.</li>
    <li>Para editar ou adicionar estações, clique em ⚙️ <b>Editar / Adicionar estações</b>.</li>
    <li>Use os gráficos e linhas de limite para monitorar os parâmetros em tempo real ou simulados.</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Escolha uma estação para ver os indicadores de ondas, vento e corrente.</div>", unsafe_allow_html=True)
with col2:
    if st.button("⚙️ Editar / Adicionar estações"):
        st.session_state.edit_mode = True
        st.session_state.edited_stations = stations_df.copy()
st.markdown("---")

# -----------------------
# Edit mode (CRUD)
# -----------------------
if st.session_state.edit_mode:
    st.markdown("<h3 style='color:white;'>⚙️ Editor de Estações</h3>", unsafe_allow_html=True)
    edited = st.data_editor(st.session_state.edited_stations, num_rows="dynamic", use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Salvar alterações"):
            save_stations(edited, CSV_PATH)
            stations_df = load_stations(CSV_PATH)
            DATA.clear()
            for i, row in stations_df.iterrows():
                DATA[row["nome"]] = gerar_dados_simulados(seed_offset=i)
            st.success("Estações salvas com sucesso.")
            st.session_state.edit_mode = False
    with c2:
        if st.button("⬅ Voltar sem salvar"):
            st.session_state.edit_mode = False

# -----------------------
# Catalog view (cards + mapa)
# -----------------------
elif st.session_state.selected_station is None:
    names = stations_df["nome"].tolist()
    cols_per_row = 2
    rows = int(np.ceil(len(names)/cols_per_row))


    # -------- Mapa
    map_df = stations_df.copy()
    for v in VARIAVEIS:
        map_df[f"latest_{v}"] = map_df["nome"].apply(lambda n: DATA[n][v].iloc[-1])

    def format_tooltip(row):
        lines = [f"<b>{row['nome']}</b> - {row['localizacao']}<br>"]
        for v in VARIAVEIS:
            val = row[f"latest_{v}"]
            sup = row.get(f"limite_sup_{v}", np.nan)
            inf = row.get(f"limite_inf_{v}", 0.0)
            out_of_range = (not np.isnan(sup) and val>sup) or (val<inf)
            emoji = "🔴" if out_of_range else "🟢"
            lines.append(f"{ICONES[v]} {v}: {val:.2f} {emoji} (inf:{inf} sup:{sup})")
        return "<br>".join(lines)

    map_df["tooltip"] = map_df.apply(format_tooltip, axis=1)

    fig_map = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        hover_name="nome",
        hover_data={"lat":False,"lon":False,"tooltip":True},
        color_discrete_sequence=["#2E86AB"],
        size_max=15,
        zoom=10,
    )

    fig_map.update_traces(hovertemplate=map_df["tooltip"])
    fig_map.update_layout(
        mapbox_style="carto-darkmatter",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=0,b=0)
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("---")
    for r in range(rows):
        cols = st.columns(cols_per_row, gap="large")
        for c in range(2):
            idx = r*cols_per_row + c
            if idx < len(names):
                name = names[idx]
                if name not in DATA:
                    continue
                latest = DATA[name].iloc[-1]
                df_filtered = stations_df[stations_df["nome"] == name]
                if df_filtered.empty: continue
                station_row = df_filtered.iloc[0]
                is_critical = False
                details = []
                for v in VARIAVEIS:
                    val = latest[v]
                    sup = station_row.get(f"limite_sup_{v}", np.nan)
                    inf = station_row.get(f"limite_inf_{v}", 0.0)
                    out_of_range = (not np.isnan(sup) and val>sup) or (val<inf)
                    if out_of_range: is_critical = True
                    details.append(f"{ICONES[v]} {v}: {val:.2f} {'🔴' if out_of_range else '🟢'} (inf:{inf} sup:{sup})")
                bg = "#E74C3C" if is_critical else "#2E7D32"
                with cols[c]:
                    if st.button("", key=f"open_{name}"):
                        st.session_state.selected_station = name
                    st.markdown(f"""
                        <div class="app-card" style="background: linear-gradient(180deg, {bg}, rgba(0,0,0,0.18));">
                            <div class="app-icon">🛰️</div>
                            <div class="app-name">{name}</div>
                            <div class="tooltip">{'<br>'.join(details)}</div>
                            <div style="margin-top:6px; font-size:13px; color:#e8eef6;">{station_row.get('localizacao', '')}</div>
                        </div>
                    """, unsafe_allow_html=True)
# -----------------------
# Station dashboard (3x2)
# -----------------------
else:
    station = st.session_state.selected_station
    st.markdown(f"<h3 style='color:white;'>📊 Dashboard 3x2 — <b>{station}</b></h3>", unsafe_allow_html=True)
    df = DATA.get(station)
    if df is None:
        st.error(f"Nenhum dado encontrado para {station}")
    else:
        station_row = stations_df[stations_df["nome"]==station].iloc[0]
        limites_sup = {v: station_row.get(f"limite_sup_{v}", np.nan) for v in VARIAVEIS}
        limites_inf = {v: station_row.get(f"limite_inf_{v}", 0.0) for v in VARIAVEIS}

        sel = st.multiselect("Variáveis para exibir", VARIAVEIS, default=VARIAVEIS)
        if len(sel)==0:
            st.info("Selecione ao menos uma variável.")
        else:
            for i in range(0, len(sel),3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i+j
                    if idx < len(sel):
                        v = sel[idx]
                        fig = px.line(df, x="datetime", y=v, color_discrete_sequence=[COLOR_SERIES[v]])
                        last = df[v].iloc[-1]
                        sup = limites_sup[v]
                        inf = limites_inf[v]
                        if not np.isnan(sup):
                            fig.add_hline(y=sup, line_dash="dash", line_color="red" if last>sup else "green",
                                          annotation_text=f"Sup {sup}", annotation_position="top right")
                        if not np.isnan(inf):
                            fig.add_hline(y=inf, line_dash="dash", line_color="red" if last<inf else "green",
                                          annotation_text=f"Inf {inf}", annotation_position="bottom right")
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                          font=dict(color="#E6EEF6"), margin=dict(l=8,r=8,t=28,b=18),
                                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        fig.update_xaxes(showgrid=False)
                        fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)")
                        cols[j].plotly_chart(fig, use_container_width=True)

        cb1, cb2 = st.columns([1,3])
        with cb1:
            if st.button("⬅ Voltar para Catálogo"):
                st.session_state.selected_station = None
        with cb2:
            st.markdown(f"<div style='text-align:right; color:#9AA6B2; font-size:13px;'>Última atualização (simulada): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)


