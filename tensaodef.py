import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Deformação × Tensão por amostra (A, B, ...)")

ARQUIVO_EXEMPLO = "dados_exemplo_tensao_deformormacao.csv"  # do seu repo

# =============================
# Fonte de dados
# =============================
modo = st.radio("Fonte dos dados:", ["Usar arquivo exemplo", "Enviar meu CSV"], horizontal=True)

df = None
if modo == "Usar arquivo exemplo":
    if not os.path.exists(ARQUIVO_EXEMPLO):
        st.error(f"Não achei o arquivo exemplo no diretório: {ARQUIVO_EXEMPLO}")
        st.stop()
    df = pd.read_csv(ARQUIVO_EXEMPLO)
    st.success("Usando arquivo exemplo do repositório")
else:
    arquivo = st.file_uploader("Envie o CSV", type=["csv"])
    if not arquivo:
        st.stop()
    df = pd.read_csv(arquivo)

if df is None or df.empty:
    st.error("CSV vazio ou não carregou.")
    st.stop()

# =============================
# Detectar colunas automaticamente
# =============================
def pick_col_contains(df, must_contain_list):
    cols = list(df.columns)
    for c in cols:
        ok = True
        for s in must_contain_list:
            if s.lower() not in str(c).lower():
                ok = False
                break
        if ok:
            return c
    return None

# tenta inferir
col_id = "amostra" if "amostra" in df.columns else None
col_x = pick_col_contains(df, ["deforma"])  # pega algo com "deforma"
col_y = pick_col_contains(df, ["tens"])    # pega algo com "tens"

# UI para corrigir caso não detecte
st.subheader("Configuração das colunas")
c1, c2, c3 = st.columns(3)

with c1:
    col_id = st.selectbox("Coluna de amostra (ID)", options=list(df.columns), index=(list(df.columns).index(col_id) if col_id in df.columns else 0))

with c2:
    # prioridade pra inferida
    x_default = list(df.columns).index(col_x) if col_x in df.columns else 0
    col_x = st.selectbox("Coluna X (Deformação)", options=list(df.columns), index=x_default)

with c3:
    y_default = list(df.columns).index(col_y) if col_y in df.columns else 0
    col_y = st.selectbox("Coluna Y (Tensão)", options=list(df.columns), index=y_default)

# =============================
# Debug rápido (pra não ficar cego)
# =============================
with st.expander("Debug (rápido)"):
    st.write("Linhas:", len(df))
    st.write("Colunas:", list(df.columns))
    st.dataframe(df.head(10), use_container_width=True)

# =============================
# Preparação
# =============================
df = df.copy()
df[col_id] = df[col_id].astype(str).str.strip()
df["grupo"] = df[col_id].str[0].str.upper()

grupos = sorted([g for g in df["grupo"].dropna().unique() if g not in ["", "N"]])  # "N" aparece quando vira "nan"
if not grupos:
    st.error("Não encontrei grupos (A, B, ...). Verifique se a coluna de amostra está preenchida.")
    st.stop()

selecionados = st.multiselect("Quais grupos plotar?", grupos, default=grupos)

def r2_score(y, yhat):
    y = np.asarray(y)
    yhat = np.asarray(yhat)
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1.0 - (ss_res / ss_tot) if ss_tot != 0 else np.nan

def plot_grupo(df_grupo, titulo):
    fig = go.Figure()
    n_curvas = 0

    for amostra, d in df_grupo.groupby(col_id):
        d = d.copy()

        d[col_x] = pd.to_numeric(d[col_x], errors="coerce")
        d[col_y] = pd.to_numeric(d[col_y], errors="coerce")
        d = d.dropna(subset=[col_x, col_y])

        if len(d) < 2:
            continue

        d = d.sort_values(col_x)
        x = d[col_x].values
        y = d[col_y].values

        m, b = np.polyfit(x, y, 1)
        y_fit = m * x + b
        r2 = r2_score(y, y_fit)

        eq = f"{amostra} — y={m:.4f}x+{b:.4f} (R²={r2:.3f})"

        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=eq))
        fig.add_trace(go.Scatter(x=x, y=y_fit, mode="lines", line=dict(dash="dash"), showlegend=False))
        n_curvas += 1

    fig.update_layout(
        title=titulo,
        xaxis_title=str(col_x),
        yaxis_title=str(col_y),
        template="plotly_white"
    )
    return fig, n_curvas

# =============================
# Plot por grupo
# =============================
for g in selecionados:
    dfg = df[df["grupo"] == g]
    fig, n_curvas = plot_grupo(dfg, f"Grupo {g} — {col_x} × {col_y}")

    if n_curvas == 0:
        st.warning(f"Grupo {g}: nenhuma curva plotada (provável conversão numérica deu NaN ou poucas linhas por amostra).")
        with st.expander(f"Ver linhas do grupo {g}"):
            st.dataframe(dfg[[col_id, col_x, col_y]].head(200), use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)
