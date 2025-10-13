import streamlit as st
import pandas as pd
import plotly.express as px

# --- Título e descrição claros ---
st.title("📊 Visualizador Inteligente de CSV")
st.markdown("""
Este visualizador permite explorar seus dados de forma intuitiva:
- Filtre por datas para focar no período relevante.
- Visualize colunas numéricas com gráficos interativos.
- Cores e organização ajudam a identificar padrões rapidamente.
""")

# --- Upload de arquivo ---
uploaded_file = st.file_uploader("📁 Envie seu arquivo CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("🗂️ Pré-visualização dos Dados")
    st.dataframe(df.head(10))  # mostra apenas as 10 primeiras linhas

    # --- Identificação e tratamento de colunas de data ---
    date_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            pass
    date_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

    # --- Filtro de datas (se houver) ---
    if date_cols:
        st.subheader("📅 Filtro por Data")
        date_col = st.selectbox("Escolha a coluna de data", date_cols)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data inicial", df[date_col].min())
        with col2:
            end_date = st.date_input("Data final", df[date_col].max())
        df = df[(df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))]

    # --- Seleção de colunas numéricas ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        st.subheader("📈 Gráfico Interativo")
        col_y = st.selectbox("Escolha a coluna para o gráfico", numeric_cols)
        
        # --- Gráfico sem marcadores ---
        fig = px.line(
            df,
            x=date_col if date_cols else df.index,
            y=col_y,
            title=f"{col_y} ao longo do tempo",
            template="plotly_white",
            color_discrete_sequence=["#1f77b4"],  # azul calmante
        )
        fig.update_traces(mode="lines")  # remove marcadores
        fig.update_layout(
            title={'x':0.5, 'xanchor':'center'},
            xaxis_title=date_col if date_cols else "Index",
            yaxis_title=col_y,
            font=dict(size=14)
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Estatísticas rápidas ---
    st.subheader("📊 Estatísticas Rápidas")
    if numeric_cols:
        st.table(df[numeric_cols].describe().round(2))
