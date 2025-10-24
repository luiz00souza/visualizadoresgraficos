import streamlit as st 

# Configurar o modo escuro
st.set_page_config(page_title="Loja de Aplicativos", layout="wide", initial_sidebar_state="collapsed")

# Ativar o tema escuro
st.markdown(
    """
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
    }
    .stApp {
        background-color: #1e1e1e;
    }
    .stButton>button {
        background-color: #444;
        color: white;
    }
    .stTextInput>div>input {
        background-color: #444;
        color: white;
    }
    .stTextArea>div>textarea {
        background-color: #444;
        color: white;
    }
    .stSelectbox, .stMultiselect {
        background-color: #444;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

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
        "nome": "Janela Operacional Marítima",
        "icone": "⚓",
        "link": "https://janelaoperacionalmare.streamlit.app/",
        "desc": "Indicador de janelas operacionais para embarcações de grande calado com base na previsão de maré."
    },
    {
        "nome": "Biblioteca Inteligente",
        "icone": "📚",
        "link": "https://bibliometrixdash.streamlit.app/",
        "desc": "Busca e analisa publicações científicas, gerando estatísticas e dashboards de revisão, tendências,redes colaborativas, palavras-chave."
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
        "link": "https://docs.google.com/forms/d/e/1FAIpQLSdDopECrhQyr1Z8PepxBQvYhDT2WbufJ7RBKbqSNJ3qOP-8yw/viewform?pli=1&pli=1",
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
        "nome": "OceanWatch Live",
        "icone": "🛰️",
        "link": "https://dinamicoastal.streamlit.app/",
        "desc": "Dados costeiros em tempo real: ondas, vento, nível do mar e correntes. Explore gráficos dinâmicos, alertas de limites críticos e mapa das estações."
    },
    {
        "nome": "Comparador de Arquivos TID",
        "icone": "🌊",
        "link": "https://comparadorarquivostid.streamlit.app/",
        "desc": "Faça upload de dois arquivos .tid e compare as séries de maré."
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




