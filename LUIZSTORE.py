import streamlit as st

st.set_page_config(page_title="Loja de Aplicativos", layout="wide")

# --- CSS estilizado (hover, sombra, transições) ---
st.markdown("""
    <style>
    .app-card {
        text-align: center;
        padding: 30px 10px;
        border-radius: 20px;
        transition: all 0.3s ease;
        background-color: #ffffff10;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .app-card:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        background-color: #ffffff20;
    }
    .app-icon {
        font-size: 80px;
        margin-bottom: 10px;
    }
    .app-name {
        font-size: 18px;
        font-weight: 600;
        color: #f5f5f5;
        text-decoration: none;
    }
    .app-desc {
        font-size: 14px;
        color: #ddd;
        margin-top: 5px;
    }
    a {
        text-decoration: none;
        color: inherit;
    }
    </style>
""", unsafe_allow_html=True)

# --- Lista dos apps ---
apps = [
    {
        "nome": "Atlas Dinâmico BR",
        "icone": "🗺️",
        "link": "https://atlasdinamicobr.streamlit.app/",
        "desc": "Explore habitats marinhos dinâmicos do Brasil."
    },
    {
        "nome": "Componentes Maré",
        "icone": "🌊",
        "link": "https://componentesmare.streamlit.app/",
        "desc": "Visualize os componentes da maré em tempo real."
    },
    {
        "nome": "Previsão Maré",
        "icone": "📈",
        "link": "https://previsaomare.streamlit.app/",
        "desc": "Acompanhe previsões de maré detalhadas."
    },
    {
        "nome": "Biblioteca",
        "icone": "📚",
        "link": "https://biblioteca.streamlit.app/",
        "desc": "Acesse artigos, livros e materiais técnicos organizados."
    },
    {
        "nome": "Formatador ABNT",
        "icone": "📝",
        "link": "https://formatadorabnt.streamlit.app/",
        "desc": "Gere referências automaticamente no padrão ABNT."
    },
    {
        "nome": "Banco de Ideias",
        "icone": "💡",
        "link": "https://forms.gle/SEU_LINK_DO_FORMS",
        "desc": "Envie sugestões de novos projetos e funcionalidades."
    },
    {
        "nome": "Publique seu App",
        "icone": "🚀",
        "link": "https://share.streamlit.io/new",
        "desc": "Crie e publique seu app diretamente no Streamlit Share."
    },
    {
        "nome": "Visualizador CSV",
        "icone": "📊",
        "link": "https://visualizadoresgraficoscsv.streamlit.app/",
        "desc": "Carregue CSVs e visualize gráficos interativos facilmente."
    },
    {
        "nome": "Catálogo de Estações Costeiras",
        "icone": "🛰️",
        "link": "http://localhost:8501",  # ou link remoto se publicado
        "desc": "Explore estações costeiras, dashboards 3x2 e mapas interativos."
    }
]

# --- Título ---
st.markdown("<h1 style='text-align: center; color: white;'>🌐 Loja de Aplicativos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa;'>Escolha um aplicativo para explorar</p>", unsafe_allow_html=True)
st.write("")

# --- Layout responsivo ---
cols = st.columns(len(apps))

for col, app in zip(cols, apps):
    with col:
        st.markdown(
            f"""
            <a href='{app['link']}' target='_blank'>
                <div class='app-card'>
                    <div class='app-icon'>{app['icone']}</div>
                    <div class='app-name'>{app['nome']}</div>
                    <div class='app-desc'>{app['desc']}</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )


