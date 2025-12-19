import streamlit as st

# ------------------------------------------------------------
# CONFIGURAÇÃO
# ------------------------------------------------------------
st.set_page_config(
    page_title="Loja de Aplicativos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# CSS — APP STORE STYLE
# ------------------------------------------------------------
st.markdown("""
<style>
body, .stApp {
    background-color: #1c1c1e;
    color: white;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* HEADER */
.header-title {
    font-size: 40px;
    font-weight: 600;
    text-align: center;
}
.header-subtitle {
    text-align: center;
    color: #9a9a9e;
    margin-bottom: 28px;
}

/* SEARCH */
.stTextInput>div>div>input {
    background-color: #2c2c2e;
    color: white;
    border-radius: 12px;
    padding: 10px 14px;
    border: none;
}

/* CARD */
.app-card {
    background-color: #2c2c2e;
    border-radius: 18px;
    padding: 20px;
    transition: background-color 0.15s ease;
    height: 100%;
}

.app-card:hover {
    background-color: #3a3a3c;
}

/* ICON */
.app-icon {
    font-size: 64px;
    margin-bottom: 14px;
}

/* TEXT */
.app-name {
    font-size: 17px;
    font-weight: 600;
    margin-bottom: 4px;
}

.app-desc {
    font-size: 14px;
    color: #9a9a9e;
    line-height: 1.3;
}

/* LINK RESET */
a {
    text-decoration: none;
    color: inherit;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# DADOS
# ------------------------------------------------------------
apps = [
    {
        "nome": "Atlas Dinâmico BR",
        "icone": "🗺️",
        "link": "https://atlasdinamicobr.streamlit.app/",
        "desc": "Mapeamento dinâmico de habitats marinhos."
    },
    {
        "nome": "Monitoramento Maré",
        "icone": "🌊",
        "link": "https://umimare.streamlit.app/",
        "desc": "Dados de maré em tempo real."
    },
    {
        "nome": "Previsão Maré",
        "icone": "📈",
        "link": "https://previsaomare.streamlit.app/",
        "desc": "Previsões do nível do mar."
    },
    {
        "nome": "Biblioteca Inteligente",
        "icone": "📚",
        "link": "https://bibliometrixdash.streamlit.app/",
        "desc": "Dashboards bibliométricos científicos."
    },
    {
        "nome": "Formatador ABNT",
        "icone": "📝",
        "link": "https://formatadorabnt.streamlit.app/",
        "desc": "Referências automáticas ABNT."
    }
]

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
st.markdown("<div class='header-title'>App Store</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>Descubra aplicativos científicos e acadêmicos</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# SEARCH
# ------------------------------------------------------------
busca = st.text_input("Buscar apps", placeholder="Pesquisar")

if busca:
    apps = [
        app for app in apps
        if busca.lower() in app["nome"].lower()
        or busca.lower() in app["desc"].lower()
    ]

# ------------------------------------------------------------
# GRID SIMPLES (ESTILO APP STORE)
# ------------------------------------------------------------
n_cols = 3
rows = [apps[i:i+n_cols] for i in range(0, len(apps), n_cols)]

for row in rows:
    cols = st.columns(n_cols)
    for col, app in zip(cols, row):
        with col:
            st.markdown(
                f"""
                <a href="{app['link']}" target="_blank">
                    <div class="app-card">
                        <div class="app-icon">{app['icone']}</div>
                        <div class="app-name">{app['nome']}</div>
                        <div class="app-desc">{app['desc']}</div>
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )
