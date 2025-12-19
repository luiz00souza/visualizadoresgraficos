import streamlit as st

# ------------------------------------------------------------------
# CONFIGURAÇÃO
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Loja de Aplicativos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# CSS UX-FOCUSED
# ------------------------------------------------------------------
st.markdown("""
<style>
body, .stApp {
    background-color: #1e1e1e;
    color: white;
}

/* HEADER */
.header-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
}

.header-subtitle {
    text-align: center;
    color: #aaaaaa;
    margin-bottom: 30px;
}

/* SEARCH */
.stTextInput>div>div>input {
    background-color: #2a2a2a;
    color: white;
    border-radius: 14px;
    padding: 10px;
}

/* TAGS */
.tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    background-color: #ffffff15;
    color: #ddd;
    font-size: 13px;
    margin-right: 8px;
    margin-bottom: 8px;
}

/* CARD */
.app-card {
    padding: 22px 18px;
    border-radius: 20px;
    background-color: #ffffff10;
    transition: all 0.25s ease;
    height: 100%;
}

.app-card:hover {
    transform: translateY(-6px);
    background-color: #ffffff20;
    box-shadow: 0 14px 30px rgba(0,0,0,0.35);
}

.app-icon {
    font-size: 56px;
    margin-bottom: 10px;
}

.app-name {
    font-size: 18px;
    font-weight: 600;
}

.app-desc {
    font-size: 14px;
    color: #cccccc;
    margin: 6px 0 10px;
}

a {
    text-decoration: none;
    color: inherit;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# DADOS
# ------------------------------------------------------------------
apps = [
    {
        "nome": "Atlas Dinâmico BR",
        "icone": "🗺️",
        "link": "https://atlasdinamicobr.streamlit.app/",
        "desc": "Mapeamento dinâmico de habitats marinhos.",
        "tags": ["Dados", "Mapa", "Pesquisa"]
    },
    {
        "nome": "Componentes Maré",
        "icone": "🌊",
        "link": "https://componentesmare.streamlit.app/",
        "desc": "Análise dos componentes harmônicos da maré.",
        "tags": ["Maré", "Tempo Real"]
    },
    {
        "nome": "Previsão Maré",
        "icone": "📈",
        "link": "https://previsaomare.streamlit.app/",
        "desc": "Previsões detalhadas de nível do mar.",
        "tags": ["Maré", "Previsão"]
    },
    {
        "nome": "Janela Operacional Marítima",
        "icone": "⚓",
        "link": "https://janelaoperacionalmare.streamlit.app/",
        "desc": "Avaliação de janelas seguras de operação.",
        "tags": ["Operacional", "Maré"]
    },
    {
        "nome": "Monitoramento Maré",
        "icone": "🌐",
        "link": "https://umimare.streamlit.app/",
        "desc": "Dados em tempo real com alertas.",
        "tags": ["Tempo Real", "Maré"]
    },
    {
        "nome": "Biblioteca Inteligente",
        "icone": "📚",
        "link": "https://bibliometrixdash.streamlit.app/",
        "desc": "Dashboards bibliométricos científicos.",
        "tags": ["Acadêmico", "Pesquisa"]
    },
    {
        "nome": "Formatador ABNT",
        "icone": "📝",
        "link": "https://formatadorabnt.streamlit.app/",
        "desc": "Referências automáticas no padrão ABNT.",
        "tags": ["Acadêmico"]
    },
    {
        "nome": "Visualizador CSV",
        "icone": "📊",
        "link": "https://visualizadoresgraficoscsv.streamlit.app/",
        "desc": "Gráficos interativos a partir de CSV.",
        "tags": ["Dados"]
    }
]

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.markdown("<div class='header-title'>🌐 Loja de Aplicativos</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>Ferramentas científicas, operacionais e acadêmicas</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# BUSCA + FILTRO
# ------------------------------------------------------------------
busca = st.text_input("🔍 Buscar aplicativo", placeholder="Ex: maré, mapa, tempo real")

tags_disponiveis = sorted({tag for app in apps for tag in app["tags"]})
tag_selecionada = st.selectbox("🏷️ Categoria", ["Todas"] + tags_disponiveis)

# ------------------------------------------------------------------
# FILTRAGEM
# ------------------------------------------------------------------
apps_filtrados = []

for app in apps:
    cond_busca = busca.lower() in app["nome"].lower() or busca.lower() in app["desc"].lower()
    cond_tag = tag_selecionada == "Todas" or tag_selecionada in app["tags"]

    if cond_busca and cond_tag:
        apps_filtrados.append(app)

st.markdown(f"**{len(apps_filtrados)} aplicativos encontrados**")

# ------------------------------------------------------------------
# GRID
# ------------------------------------------------------------------
n_cols = 3
rows = [apps_filtrados[i:i+n_cols] for i in range(0, len(apps_filtrados), n_cols)]

for row in rows:
    cols = st.columns(n_cols)
    for col, app in zip(cols, row):
        with col:
            tags_html = "".join([f"<span class='tag'>{t}</span>" for t in app["tags"]])

            st.markdown(
                f"""
                <a href="{app['link']}" target="_blank">
                    <div class="app-card">
                        <div class="app-icon">{app['icone']}</div>
                        <div class="app-name">{app['nome']}</div>
                        <div class="app-desc">{app['desc']}</div>
                        {tags_html}
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )
