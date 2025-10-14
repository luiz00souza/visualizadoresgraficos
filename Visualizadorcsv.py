import streamlit as st
import pandas as pd
import plotly.express as px

# --- Título e descrição claros ---
st.title("📊 Visualizador de Dados CSV Interativo")
st.markdown("""
Aplique filtros intuitivos para explorar os dados e gerar gráficos interativos:
- Carregue seu CSV e visualize rapidamente suas informações.
- Filtro de datas ajuda a focar em períodos relevantes.
- Visualização de múltiplas variáveis no mesmo gráfico para comparações eficazes.
""")

# --- Upload de arquivo com feedback visual claro ---
uploaded_file = st.file_uploader("📁 Envie seu arquivo CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Confirmação visual de que o arquivo foi carregado
    st.success("Arquivo carregado com sucesso! Você pode visualizar e analisar os dados abaixo.")

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

    # --- Filtro de datas com interface clara e feedback --- 
    if date_cols:
        st.subheader("📅 Filtre por Período")
        date_col = st.selectbox("Escolha a coluna de data", date_cols)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data Inicial", df[date_col].min())
        with col2:
            end_date = st.date_input("Data Final", df[date_col].max())
        
        # Feedback claro sobre o filtro aplicado
        if start_date and end_date:
            st.markdown(f"🔄 Filtro aplicado: {start_date} até {end_date}")
        
        df = df[(df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))]

    # --- Seleção de colunas numéricas com feedback visual para escolha ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        st.subheader("📈 Visualize seus Dados")
        selected_cols = st.multiselect(
            "Escolha as variáveis para o gráfico", 
            numeric_cols, 
            default=numeric_cols[:1]
        )

        # Visualizar as primeiras linhas das colunas selecionadas para garantir clareza
        st.markdown("🔍 Pré-visualização dos dados selecionados:")
        st.dataframe(df[selected_cols].head(5))

        # --- Gráfico com múltiplas variáveis e interatividade (zoom, tooltips) ---
        fig = px.line(
            df,
            x=date_col if date_cols else df.index,
            y=selected_cols,
            title=f"Comparação de {', '.join(selected_cols)} ao longo do tempo",
            template="plotly_white"
        )
        fig.update_traces(mode="lines", hovertemplate='%{y:.2f}<extra></extra>')
        fig.update_layout(
            title={'x':0.5, 'xanchor':'center'},
            xaxis_title=date_col if date_cols else "Index",
            yaxis_title="Valores",
            font=dict(size=14),
            hovermode="x unified",  # Melhora o feedback ao passar o mouse
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Estatísticas rápidas com contexto e transposição ---
    st.subheader("📊 Estatísticas Rápidas (Transposta)")
    if numeric_cols:
        stats = df[numeric_cols].describe().T
        st.dataframe(stats.style.format("{:.2f}"))

