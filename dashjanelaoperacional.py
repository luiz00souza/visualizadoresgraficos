# -*- coding: utf-8 -*-
"""
JanelaMar — Monitor Operacional
Versão UX/Neuropsicológica: janelas passadas, atuais e futuras destacadas
Com previsão de janelas futuras
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# -------------------------------
# 🌤️ CONFIGURAÇÕES INICIAIS / NOME
# -------------------------------
APP_NAME = "JanelaMar — Monitor Operacional"
st.set_page_config(page_title=APP_NAME, layout="wide")
st.title(f"🌊 {APP_NAME}")

st.markdown(
    "Analisa janelas operacionais com base na **Altura Final** de sensores. "
    "Ajuste parâmetros à esquerda e exporte resultados em CSV."
)

# -------------------------------
# --- PATHS dos arquivos
# -------------------------------
arquivos = {
    "Sensor 6": r"C:\Users\campo\Desktop\SistamaQAQC\JANELAS_OPERACIONAIS\JANELAOPERACIONAL6.csv",
    "Sensor 7": r"C:\Users\campo\Desktop\SistamaQAQC\JANELAS_OPERACIONAIS\JANELAOPERACIONAL7.csv",
    "Sensor 8": r"C:\Users\campo\Desktop\SistamaQAQC\JANELAS_OPERACIONAIS\JANELAOPERACIONAL8.csv",
}

# -------------------------------
# 🧭 SIDEBAR: CONTROLES PRINCIPAIS
# -------------------------------
st.sidebar.header("Parâmetros de Análise")
st.sidebar.markdown("Ajuste e teste cenários rapidamente. Valores padrão preservados.")

# Nome do app editável
app_name_input = st.sidebar.text_input(
    "Nome do App", value=APP_NAME, help="Personalize o título do app", key="app_name_input"
)
if app_name_input.strip():
    st.title(app_name_input)

# Sensores e seleção
sensores_default = list(arquivos.keys())
sensores_selecionados = st.sidebar.multiselect(
    "Sensores incluídos na análise",
    options=list(arquivos.keys()),
    default=sensores_default,
    help="Escolha os sensores que participarão da condição conjunta.",
    key="sensores_multiselect"
)

# Parâmetros principais
col1, col2 = st.sidebar.columns(2)
with col1:
    limite = st.number_input(
        "Limite (m)",
        min_value=0.0,
        max_value=10.0,
        value=0.5,
        step=0.1,
        help="Valor de altura que define a condição (p.ex. 0.5 m).",
        key="limite_input"
    )
with col2:
    duracao_min = st.number_input(
        "Duração mínima (min)",
        min_value=1,
        max_value=1440,
        value=120,
        step=1,
        help="Duração mínima de continuidade para considerar janela válida.",
        key="duracao_input"
    )

# Parâmetros Avançados
with st.sidebar.expander("⚙️ Critérios avançados", expanded=False):
    modo = st.selectbox(
        "Como combinar sensores",
        ["Todos (AND)", "Qualquer (OR)"],
        index=0,
        help="Todos: condição verdadeira em todos os sensores. Qualquer: condição verdadeira em pelo menos um.",
        key="modo_select"
    )
    merge_method = st.selectbox(
        "Tipo de junção temporal",
        ["inner", "outer"],
        index=0,
        help="inner: mantém apenas timestamps comuns; outer: mantém a união (pode gerar NaNs).",
        key="merge_select"
    )
    show_range_slider = st.checkbox(
        "Mostrar range slider no gráfico",
        value=True,
        key="range_slider_checkbox"
    )
    enable_range_recalc = st.checkbox(
        "Recalcular somente intervalo selecionado (quando usar range slider)",
        value=False,
        key="range_recalc_checkbox"
    )

min_duration = pd.Timedelta(minutes=int(duracao_min))

# -------------------------------
# 📥 CARREGAMENTO DOS CSVs
# -------------------------------
@st.cache_data(ttl=60)
def carregar_csv(caminho):
    df = pd.read_csv(caminho)
    if 'GMT-03:00' in df.columns:
        df['GMT-03:00'] = pd.to_datetime(df['GMT-03:00'])
    else:
        for c in df.columns:
            try:
                df[c] = pd.to_datetime(df[c])
                df.rename(columns={c: 'GMT-03:00'}, inplace=True)
                break
            except Exception:
                continue
    return df

dfs = {}
load_errors = []
for nome in sensores_selecionados:
    try:
        df = carregar_csv(arquivos[nome])
        if 'Altura Final' not in df.columns:
            st.warning(f"O arquivo do {nome} não contém coluna 'Altura Final'. Verifique o CSV.")
        df = df[['GMT-03:00', 'Altura Final']].rename(columns={'Altura Final': nome})
        dfs[nome] = df
    except Exception as e:
        load_errors.append(f"{nome}: {e}")

if load_errors:
    st.error("Erros ao carregar alguns arquivos:")
    for err in load_errors:
        st.write("-", err)

if not dfs:
    st.stop()

# -------------------------------
# 🔗 JUNÇÃO TEMPORAL
# -------------------------------
with st.spinner("🔄 Unindo séries e calculando janelas..."):
    keys = list(dfs.keys())
    df_combined = dfs[keys[0]]
    for nome in keys[1:]:
        df_combined = pd.merge(df_combined, dfs[nome], on='GMT-03:00', how=merge_method)
    df_combined = df_combined.sort_values('GMT-03:00').reset_index(drop=True)

    sensor_cols = keys
    for c in sensor_cols:
        df_combined[c] = pd.to_numeric(df_combined[c], errors='coerce')

    if modo == "Todos (AND)":
        mask_conjunta = (df_combined[sensor_cols] > limite).all(axis=1)
    else:
        mask_conjunta = (df_combined[sensor_cols] > limite).any(axis=1)

    df_combined['window_group'] = (mask_conjunta != mask_conjunta.shift()).cumsum()
    windows = df_combined[mask_conjunta].groupby('window_group')

    valid_windows = []
    for _, group in windows:
        group = group.dropna(subset=['GMT-03:00'])
        if len(group) < 1:
            continue
        duration = group['GMT-03:00'].iloc[-1] - group['GMT-03:00'].iloc[0]
        if duration >= min_duration:
            resumo_sensor = {c: (group[c].min(), group[c].max()) for c in sensor_cols}
            summary_row = {
                "Início": group['GMT-03:00'].iloc[0],
                "Fim": group['GMT-03:00'].iloc[-1],
                "Duração (min)": int(duration.total_seconds() / 60),
                "Pontos": len(group)
            }
            for c in sensor_cols:
                summary_row[f"{c} min"] = resumo_sensor[c][0]
                summary_row[f"{c} max"] = resumo_sensor[c][1]
            valid_windows.append((group, summary_row))

# -------------------------------
# 🧾 CARDS RESUMO
# -------------------------------
num_janelas = len(valid_windows)
total_min = sum(w[1]["Duração (min)"] for w in valid_windows) if num_janelas else 0

c1, c2, c3, c4 = st.columns([1.2,1.2,1.2,1.6])
c1.metric("Limite (m)", f"{limite}")
c2.metric("Duração mínima (min)", f"{int(duracao_min)}")
c3.metric("Sensores usados", f"{len(sensor_cols)}")
c4.metric("Janelas válidas", f"{num_janelas}", delta=f"{int(total_min)} min" if num_janelas else "—")

# -------------------------------
# 🔮 PREVISÃO DE JANELAS FUTURAS
# -------------------------------
st.sidebar.header("Previsão de Janelas Futuras")
horas_futuras = st.sidebar.number_input(
    "Horas para previsão",
    min_value=1,
    max_value=168,
    value=72,
    step=1,
    help="Defina o horizonte temporal para contar janelas futuras.",
    key="horas_futuras_input"
)

agora = pd.Timestamp.now()
horizonte = agora + pd.Timedelta(hours=horas_futuras)
future_windows = [
    w for w in valid_windows
    if w[1]["Início"] > agora and w[1]["Início"] <= horizonte
]

num_futuras = len(future_windows)
total_duracao_fut = sum(w[1]["Duração (min)"] for w in future_windows)
c1, c2 = st.columns([1,1])
c1.metric(f"🟦 Janelas futuras próximas {horas_futuras}h", f"{num_futuras}")
horas_fut = total_duracao_fut // 60
min_fut = total_duracao_fut % 60
c2.metric(f"⏱️ Duração total prevista", f"{horas_fut}h {min_fut}min")

# -------------------------------
# 🧾 RESUMO AUTOMÁTICO
# -------------------------------
st.markdown("---")
if num_janelas:
    horas = total_min // 60
    minutos = total_min % 60
    st.success(
        f"✅ Foram identificadas **{num_janelas}** janelas válidas usando {len(sensor_cols)} sensor(es). "
        f"Total: **{int(horas)}h {int(minutos)}min** de operação."
    )
    st.markdown(
        "Dica: clique em uma linha da tabela abaixo para focar na janela no gráfico (use o range slider)."
    )
else:
    st.info(
        "Nenhuma janela válida encontrada com os parâmetros atuais. "
        "Sugestão: reduza levemente o limite ou diminua a duração mínima para explorar possibilidades."
    )

# -------------------------------
# 📈 GRÁFICO INTERATIVO (Plotly)
# -------------------------------
fig = go.Figure()
palette = ["#0077b6", "#ff7b00", "#2ca02c", "#8e44ad", "#e63946"]

for i, nome in enumerate(sensor_cols):
    fig.add_trace(go.Scatter(
        x=df_combined['GMT-03:00'],
        y=df_combined[nome],
        mode='lines',
        name=nome,
        line=dict(color=palette[i % len(palette)], width=2),
        hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>%{y:.3f} m<extra></extra>"
    ))

# destacar janelas válidas com UX cognitivo
for group, _ in valid_windows:
    if group['GMT-03:00'].iloc[-1] < agora:
        fillcolor = "#2ca02c"  # verde passado
        opacity = 0.15
    elif group['GMT-03:00'].iloc[0] > agora:
        fillcolor = "#0077b6"  # azul futuro
        opacity = 0.2
    else:
        fillcolor = "#ff7b00"  # laranja atual
        opacity = 0.25

    fig.add_vrect(
        x0=group['GMT-03:00'].iloc[0],
        x1=group['GMT-03:00'].iloc[-1],
        fillcolor=fillcolor,
        opacity=opacity,
        layer="below",
        line_width=0
    )

# linha limite
fig.add_hline(
    y=limite,
    line_dash="dash",
    line_color="#e63946",
    annotation_text=f"Limite {limite} m",
    annotation_position="top left"
)

fig.update_layout(
    xaxis_title="Tempo (GMT-03:00)",
    yaxis_title="Altura Final (m)",
    template="plotly_white",
    height=560,
    legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
    margin=dict(l=40, r=40, t=60, b=40)
)

# aplica range slider se selecionado
if show_range_slider:
    fig.update_xaxes(rangeslider_visible=True)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📋 TABELA DE JANELAS DETECTADAS + EXPORT
# -------------------------------
st.markdown("### 📅 Janelas operacionais detectadas")
if num_janelas:
    resumo_df = pd.DataFrame([r for (_, r) in valid_windows])
    resumo_df['Início'] = pd.to_datetime(resumo_df['Início']).dt.strftime("%Y-%m-%d %H:%M:%S")
    resumo_df['Fim'] = pd.to_datetime(resumo_df['Fim']).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(resumo_df, use_container_width=True, height=280)

    csv_bytes = resumo_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar janelas (CSV)",
        data=csv_bytes,
        file_name="janelas_operacionais.csv",
        mime="text/csv"
    )

    with st.expander("🔎 Ver / exportar dados brutos por janela"):
        sel = st.selectbox("Escolha a janela para visualizar dados brutos", options=list(range(len(valid_windows))), key="janela_bruta_select")
        group, summary = valid_windows[sel]
        st.write(summary)
        st.dataframe(group.reset_index(drop=True), use_container_width=True, height=300)
        csv_raw = group.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Exportar dados da janela {sel+1} (CSV)",
            data=csv_raw,
            file_name=f"janela_{sel+1}_dados.csv",
            mime="text/csv"
        )
else:
    st.markdown("Nenhuma janela para mostrar — ajuste os parâmetros no painel lateral e tente novamente.")

# -------------------------------
# 🦴 RODAPÉ
# -------------------------------
st.markdown("---")
st.caption("Desenvolvido para decisões operacionais claras — JanelaMar • UX cognitivo aplicado")
