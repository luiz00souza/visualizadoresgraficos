import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Deformação × Tensão por amostra (A, B, ...)")

arquivo = st.file_uploader("Carregue o CSV unificado", type=["csv"])

COL_X = "Deformação à flexão (Deslocamento)"
COL_Y = "Tensão à flexão"
COL_ID = "amostra"

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
        d = d.dropna(subset=[COL_X, COL_Y])

        if len(d) < 2:
            continue

        d = d.sort_values(COL_X)

        x = d[COL_X].values
        y = d[COL_Y].values

        m, b = np.polyfit(x, y, 1)
        y_fit = m * x + b
        r2 = r2_score(y, y_fit)

        eq = f"{amostra} — y={m:.4f}x+{b:.4f} (R²={r2:.3f})"

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=eq
            )
        )

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y_fit,
                mode="lines",
                line=dict(dash="dash"),
                showlegend=False
            )
        )

    fig.update_layout(
        title=titulo,
        xaxis_title="Deformação (%)",
        yaxis_title="Tensão (MPa)",
        template="plotly_white",
        legend_title_text="Amostras (equação da reta)"
    )

    return fig


if arquivo:

    df = pd.read_csv(arquivo)

    for c in [COL_X, COL_Y, COL_ID]:
        if c not in df.columns:
            st.error(f"Coluna não encontrada: {c}")
            st.stop()

    df = df.copy()
    df[COL_ID] = df[COL_ID].astype(str).str.strip()
    df["grupo"] = df[COL_ID].str[0].str.upper()

    grupos = sorted([g for g in df["grupo"].dropna().unique() if g != ""])

    selecionados = st.multiselect(
        "Quais grupos plotar?",
        grupos,
        default=grupos
    )

    if not selecionados:
        st.warning("Selecione pelo menos um grupo (A, B, ...)")
        st.stop()

    for g in selecionados:

        dfg = df[df["grupo"] == g]

        fig = plot_grupo(
            dfg,
            f"Grupo {g} — Deformação × Tensão"
        )

        st.plotly_chart(fig, use_container_width=True)
