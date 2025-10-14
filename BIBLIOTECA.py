# -*- coding: utf-8 -*-
"""
Biblioteca Digital — Streamlit
Autoload CSV do repositório para nuvem
"""

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Biblioteca Digital", layout="wide")

# --- Estilo neuropsicológico (cores suaves, foco cognitivo) ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(180deg, #0f2027, #203a43, #2c5364);
        color: #f2f2f2;
        font-family: 'Segoe UI', sans-serif;
    }
    .book-card {
        background-color: rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 20px;
        margin: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    .book-card:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        background-color: rgba(255,255,255,0.12);
    }
    .book-title {
        font-size: 20px;
        font-weight: 600;
        color: #eaf6f6;
    }
    .book-author {
        color: #b3e5e5;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .book-year {
        color: #a9d6d6;
        font-size: 13px;
    }
    .book-desc {
        color: #d9e9e9;
        font-size: 14px;
        margin-top: 10px;
        line-height: 1.4;
    }
    .book-link {
        display: inline-block;
        margin-top: 12px;
        padding: 8px 14px;
        background-color: #29b6f6;
        color: white;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 500;
        transition: 0.3s;
    }
    .book-link:hover {
        background-color: #4dd0e1;
    }
    </style>
""", unsafe_allow_html=True)

# --- Título ---
st.markdown("<h1 style='text-align:center; color:#e0f7fa;'>📚 Biblioteca Digital</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#b2ebf2;'>Explore e descubra conhecimento com leveza e clareza mental</p>", unsafe_allow_html=True)

# --- Carregar CSV automaticamente ---
# Opção 1: arquivo local dentro do repo
CSV_PATH = os.path.join(os.path.dirname(__file__), "biblioteca.csv")

# Opção 2: arquivo hospedado no GitHub
# CSV_PATH = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/biblioteca.csv"

@st.cache_data(ttl=600)
def carregar_csv(path):
    try:
        df = pd.read_csv(path, sep=";")
        df.columns = [c.strip().capitalize() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Não foi possível carregar o CSV: {e}")
        return pd.DataFrame()

df = carregar_csv(CSV_PATH)

# --- Interatividade ---
if not df.empty:
    categorias = df["Categoria"].dropna().unique()
    filtro_categoria = st.multiselect("Filtrar por categoria:", categorias)
    busca = st.text_input("🔎 Buscar por palavra-chave (título, autor, descrição):")

    df_filtrado = df.copy()
    if filtro_categoria:
        df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(filtro_categoria)]
    if busca:
        busca_lower = busca.lower()
        df_filtrado = df_filtrado[df_filtrado.apply(lambda x: busca_lower in str(x).lower(), axis=1)]

    if not df_filtrado.empty:
        cols = st.columns(3)
        for i, (_, row) in enumerate(df_filtrado.iterrows()):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div class='book-card'>
                        <div class='book-title'>{row['Título']}</div>
                        <div class='book-author'>{row['Autor']} ({row['Ano']})</div>
                        <div class='book-desc'>{row['Descrição']}</div>
                        <a href='{row['Link']}' target='_blank' class='book-link'>Acessar</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("Nenhum item encontrado para os filtros aplicados.")
else:
    st.info("Biblioteca vazia ou CSV não encontrado 📁")
