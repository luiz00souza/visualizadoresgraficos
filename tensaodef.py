import os
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Deformação × Tensão por amostra (A, B, ...)")

ARQUIVO_EXEMPLO = "dados_exemplo_tensao_deformormacao.csv"  # mesmo diretório do .py

# =============================
# Leitura CSV com separador automático
# =============================
def read_csv_auto(source, prefer_utf8=True):
    """
    Lê CSV detectando separador automaticamente.
    source pode ser:
      - caminho (str)
      - objeto do st.file_uploader (UploadedFile)
    Retorna: (df, sep_usado, encoding_usado)
    """
    # ---- obter bytes ----
    if isinstance(source, str):
        with open(source, "rb") as f:
            raw = f.read()
    else:
        raw = source.getvalue()

    # ---- decodificar ----
    encodings = ["utf-8", "utf-8-sig", "latin1"] if prefer_utf8 else ["latin1", "utf-8", "utf-8-sig"]
    text = None
    used_enc = None
    for enc in encodings:
        try:
            text = raw.decode(enc)
            used_enc = enc
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        # último recurso
        text = raw.decode("latin1", errors="replace")
        used_enc = "latin1(errors=replace)"

    # ---- 1) tentativa: pandas sniff (csv.Sniffer) ----
    # se der 1 coluna só, provavelmente separador errado ou arquivo "estranho"
    try:
        df = pd.read_csv(io.StringIO(text), sep=None, engine="python", on_bad_lines="skip")
        if df is not None and df.shape[1] > 1:
            return df, None, used_enc
    except Exception:
        pass

    # ---- 2) fallback: testar separadores comuns e escolher o melhor ----
    seps = [";", ",", "\t", "|"]
    best_df = None
    best_sep = None
    best_cols = -1

    for sep in seps:
        try:
            dft = pd.read_csv(io.StringIO(text), sep=sep, engine="python", on_bad_lines="skip")
            ncols = dft.shape[1]
            if ncols > best_cols:
                best_cols = ncols
                best_df = dft
                best_sep = sep
        except Exception:
            continue

    if best_df is None:
        # última tentativa: default do pandas
        df = pd.read_csv(io.StringIO(text))
        return df, None, used_enc

    return best_df, best_sep, used_enc


# =============================
# Fonte de dados
# =============================
modo = st.radio("Fonte dos dados:", ["Usar arquivo exemplo", "Enviar meu CSV"], horizontal=True)

df = None
sep_usado = None
enc_usado = None

if modo == "Usar arquivo exemplo":
    if not os.path.exists(ARQUIVO_EXEMPLO):
        st.error(f"Não achei o arquivo exemplo no diretório: {ARQUIVO_EXEMPLO}")
        st.stop()
    df, sep_usado, enc_usado = read_csv_auto(ARQUIVO_EXEMPLO)
    st.success(f"Usando arquivo exemplo do repositório (sep: {sep_usado or 'auto'}, enc: {enc_usado})")
else:
    arquivo = st.file_uploader("Envie o CSV", type=["csv"])
    if not arquivo:
        st.stop()
    df, sep_usado, enc_usado = read_csv_auto(arquivo)
    st.success(f"CSV carregado (sep: {sep_usado or 'auto'}, enc: {enc_usado})")

if df is None or df.empty:
    st.error("CSV vazio ou não carregou.")
    st.stop()

# Se o CSV veio todo "colapsado" numa coluna só, mostra dica rápida
if df.shape[1] == 1:
    st.warning(
        "Seu CSV ficou com 1 coluna só. Isso normalmente indica separador não detectado ou arquivo fora do padrão."
    )
    with st.expander("Ver primeiras linhas (debug)"):
        st.dataframe(df.head(50), use_container_width=True)


# =============================
# Detectar colunas automaticamente
# =============================
def pick_col_contains(df_, must_contain_list):
    cols = list(df_.columns)
    for c in cols:
        ok = True
        for s in must_contain_list:
            if s.lower() not in str(c).lower():
                ok = False
                break
        if ok:
            return c
    return None


col_id_guess = "amostra" if "amostra" in df.columns else None
col_x_guess = pick_col_contains(df, ["deforma"])
col_y_guess = pick_col_contains(df, ["tens"])

st.subheader("Configuração das colunas")
c1, c2, c3 = st.columns(3)

with c1:
    col_id = st.selectbox(
        "Coluna de amostra (ID)",
        options=list(df.columns),
        index=(list(df.columns).index(col_id_guess) if col_id_guess in df.columns else 0),
    )

with c2:
    x_default = list(df.columns).index(col_x_guess) if col_x_guess in df.columns else 0
    col_x = st.selectbox("Coluna X (Deformação)", options=list(df.columns), index=x_default)

with c3:
    y_default = list(df.columns).index(col_y_guess) if col_y_guess in df.columns else 0
    col_y = st.selectbox("Coluna Y (Tensão)", options=list(df.columns), index=y_default)


# =============================
# Preparação
# =============================
df = df.copy()
df[col_id] = df[col_id].astype(str).str.strip()
df["grupo"] = df[col_id].str[0].str.upper()

grupos = sorted([g for g in df["grupo"].dropna().unique() if g not in ["", "N"]])
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


def to_numeric_br(series: pd.Series) -> pd.Series:
    """
    Converte números aceitando decimal com vírgula e removendo espaços.
    Ex:
      '0,694' -> 0.694
      ' 1.23 ' -> 1.23
    """
    s = series.astype(str).str.strip()
    # troca vírgula por ponto (decimal)
    s = s.str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def plot_grupo(df_grupo, titulo):
    fig = go.Figure()
    n_curvas = 0

    for amostra, d in df_grupo.groupby(col_id):
        d = d.copy()

        d[col_x] = to_numeric_br(d[col_x])
        d[col_y] = to_numeric_br(d[col_y])
        d = d.dropna(subset=[col_x, col_y])

        if len(d) < 2:
            continue

        d = d.sort_values(col_x)
        x = d[col_x].values
        y = d[col_y].values

        # ajuste linear
        try:
            m, b = np.polyfit(x, y, 1)
        except Exception:
            continue

        y_fit = m * x + b
        r2 = r2_score(y, y_fit)

        eq = f"{amostra} — y={m:.4f}x+{b:.4f} (R²={r2:.3f})"

        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=eq))
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y_fit,
                mode="lines",
                line=dict(dash="dash"),
                showlegend=False
            )
        )
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
        st.warning(f"Grupo {g}: nenhuma curva plotada (provável NaN, separador/decimal, ou poucas linhas por amostra).")
        with st.expander(f"Ver linhas do grupo {g}"):
            st.dataframe(dfg[[col_id, col_x, col_y]].head(200), use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)

# =============================
# Abaixo de tudo: ver planilha + baixar
# =============================
st.divider()
st.subheader("Dados (planilha) e download")

with st.expander("Ver planilha completa"):
    st.dataframe(df, use_container_width=True)

csv_bytes = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Baixar dados (CSV)",
    data=csv_bytes,
    file_name="dados_filtrados.csv",
    mime="text/csv",
)
