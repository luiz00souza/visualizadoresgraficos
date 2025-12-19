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
# CSS UX AVANÇADO
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
    margin-bottom: 25px;
}

/* SEARCH */
.stTextInput>div>div>input {
    background-color: #2a2a2a;
    color: white;
    border-radius: 14px;
    padding: 10px;
}

/* TAG */
.tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    background-color: #ffffff15;
    color: #ddd;
    font-size: 13px;
    margin-right: 6px;
    margin-bottom: 6px;
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

/* FEATURED */
.featured {
    background: linear-gradient(135deg, #2d2d2d, #1f1f1f);
    border-radius: 24px;
    padding: 30px;
    margin-bottom: 35px;
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
        "tags": ["Mapa", "Pesquisa"],
        "destaque": True
    },
    {
        "nome": "Monitoramento Maré",
        "icone": "🌐",
        "link": "https://umimare.streamlit.app/",
        "desc": "Dados de maré em tempo real com alertas.",
        "tags": ["Maré", "Tempo Real"],
        "destaque": True
    },
    {
        "nome": "Previsão Maré",
        "icone": "📈",
        "link": "https://previsaomare.streamlit.app/",
        "desc": "Previsões detalhadas do nível do mar.",
        "tags": ["Maré"],
        "destaque": False
    },
    {
        "nome": "Biblioteca Inteligente",
        "icone": "📚",
        "link": "https://bibliometrixdash.streamlit.app/",
        "desc": "Dashboards bibliométricos científicos.",
        "tags": ["Acadêmico"],
        "destaque": False
    },
    {
        "nome": "Formatador ABNT",
        "icone": "📝",
        "link": "https://formatadorabnt.streamlit.app/",
        "desc": "Referências automáticas no padrão ABNT.",
        "tags": ["Acadêmico"],
        "destaque": False
    }
]

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.markdown("<div class='header-title'>🌐 Loja de Aplicativos</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>Ferramentas científicas, operacionais e acadêmicas</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# BUSCA
# ------------------------------------------------------------------
busca = st.text_input("🔍 Buscar aplicativo", placeholder="Ex: maré, mapa, tempo real")

# ------------------------------------------------------------------
# DESTAQUES
# ------------------------------------------------------------------
destaques = [a for a in apps if a["destaque"]]

if destaques:
    st.markdown("## ⭐ Destaques")
    cols = st.columns(len(destaques))
    for col, app in zip(cols, destaques):
        with col:
            st.markdown(
                f"""
                <a href="{app['link']}" target="_blank">
                    <div class="featured">
                        <div class="app-icon">{app['icone']}</div>
                        <div class="app-name">{app['nome']}</div>
                        <div class="app-desc">{app['desc']}</div>
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )

# ------------------------------------------------------------------
# LISTA PRINCIPAL
# ------------------------------------------------------------------
apps_filtrados = [
    app for app in apps
    if busca.lower() in app["nome"].lower()
    or busca.lower() in app["desc"].lower()
]

st.markdown(f"### 📦 Todos os aplicativos ({len(apps_filtrados)})")

# GRID RESPONSIVO
n_cols = 3 if st.session_state.get("wide", True) else 2
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
