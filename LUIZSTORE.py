import streamlit as st

# ------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Loja de Aplicativos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# TEMA ESCURO + CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #1e1e1e;
    color: white;
}

.stApp {
    background-color: #1e1e1e;
}

/* CARD */
.app-card {
    text-align: center;
    padding: 24px 16px;
    border-radius: 18px;
    transition: all 0.25s ease;
    background-color: #ffffff10;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    height: 100%;
}

.app-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 28px rgba(0,0,0,0.35);
    background-color: #ffffff20;
}

.app-icon {
    font-size: 64px;
    margin-bottom: 10px;
}

.app-name {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 6px;
}

.app-desc {
    font-size: 14px;
    color: #cccccc;
}

a {
    text-decoration: none;
    color: inherit;
}

/* INPUT BUSCA */
.stTextInput>div>div>input {
    background-color: #2a2a2a;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# DADOS DOS APPS
# ------------------------------------------------------------------
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
        "desc": "Indicador de janelas operacionais para grandes embarcações."
    },
    {
        "nome": "SEASMART",
        "icone": "🐬",
        "link": "https://seasmart.streamlit.app/",
        "desc": "Medições de maré em tempo real com alertas automáticos."
    },
    {
        "nome": "REMOBS Store",
        "icone": "🟡🛰️",
        "link": "https://remobstore.streamlit.app/",
        "desc": "Dashboard das principais ferramentas para monitoramento meteoceanografico em tempo real da costa brasileira."
    },
    {
        "nome": "Biblioteca Inteligente",
        "icone": "📚",
        "link": "https://bibliometrixdash.streamlit.app/",
        "desc": "Análise bibliométrica e dashboards científicos."
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
        "link": "https://docs.google.com/forms/d/e/1FAIpQLSdDopECrhQyr1Z8PepxBQvYhDT2WbufJ7RBKbqSNJ3qOP-8yw/viewform",
        "desc": "Envie sugestões de novos projetos e funcionalidades."
    },
    {
        "nome": "Publique seu App",
        "icone": "🚀",
        "link": "https://share.streamlit.io/new",
        "desc": "Crie e publique seu app no Streamlit Cloud."
    },
    {
        "nome": "Visualizador CSV",
        "icone": "📊",
        "link": "https://visualizadoresgraficoscsv.streamlit.app/",
        "desc": "Visualize gráficos interativos a partir de CSVs."
    },
    {
        "nome": "OceanWatch Live",
        "icone": "🛰️",
        "link": "https://dinamicoastal.streamlit.app/",
        "desc": "Dados costeiros em tempo real: ondas, vento e correntes."
    },
    {
        "nome": "Comparador de Arquivos TID",
        "icone": "🌊",
        "link": "https://comparadorarquivostid.streamlit.app/",
        "desc": "Compare séries temporais de maré (.tid)."
    }
]

# ------------------------------------------------------------------
# TÍTULO
# ------------------------------------------------------------------
st.markdown("<h1 style='text-align:center;'>🌐 Loja de Aplicativos</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#aaaaaa;'>Explore ferramentas científicas, operacionais e acadêmicas</p>",
    unsafe_allow_html=True
)

st.write("")

# ------------------------------------------------------------------
# BUSCA
# ------------------------------------------------------------------
busca = st.text_input("🔍 Buscar aplicativo", placeholder="Digite o nome ou descrição")

if busca:
    apps_filtrados = [
        app for app in apps
        if busca.lower() in app["nome"].lower()
        or busca.lower() in app["desc"].lower()
    ]
else:
    apps_filtrados = apps

# ------------------------------------------------------------------
# GRID ESTILO PLAY STORE (ROLAGEM VERTICAL)
# ------------------------------------------------------------------
n_cols = 3
rows = [apps_filtrados[i:i+n_cols] for i in range(0, len(apps_filtrados), n_cols)]

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




