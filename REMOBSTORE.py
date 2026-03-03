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
        "nome": "Plot Séries Temporais",
        "icone": "📈",
        "link": "https://plotseriestemporais.streamlit.app/",
        "desc": "Aplicativo para visualização e análise de séries temporais das boias REMOBS."
    },
    {
        "nome": "Boias Spotter (SOFAR)",
        "icone": "🟡🛰️",
        "link": "https://spotter.sofarocean.com/login",
        "desc": "Dashboard das boias Spotter (SOFAR Ocean) para monitoramento de ondas e dados em tempo real."
    },
    {
        "nome": "Dashboard REMOBS",
        "icone": "📡",
        "link": "https://dashboard-remobs.vercel.app/",
        "desc": "Dashboard central REMOBS para monitoramento e análises."
    },
    {
        "nome": "Portal Sailbuoy (Iridium)",
        "icone": "⛵🛰️",
        "link": "https://iridium2.azurewebsites.net/",
        "desc": "Portal operacional do Sailbuoy via Iridium: mapas, dados, arquivos e controle."
    },
    {
        "nome": "Flutuadores ARGO",
        "icone": "🧪",
        "link": "https://fleetmonitoring.euro-argo.eu/dashboard?Status=Active&Country=Brazil",
        "desc": "Monitoramento da frota de flutuadores ARGO ativos (Brasil)."
    },
    {
        "nome": "Glider Dashboard",
        "icone": "🚀",
        "link": "https://sfmc.webbresearch.com/sfmc/dashboard",
        "desc": "Painel de controle e monitoramento de missões Glider (SFMC)."
    },
{
    "nome": "Padrão de String de Transmissão",
    "icone": "📡🔢",
    "link": "https://setek.com.br/chm/",
    "desc": "Referência dos padrões de string de transmissão para cada sistema de comunicação das boias."
},
{
    "nome": "Instrumentação e Manuais",
    "icone": "🔧📚",
    "link": "https://drive.google.com/drive/folders/1aQe68m0sRdwLkGHnnuIIy4dJbfhpTPDa",
    "desc": "Repositório de instrumentação: manuais, especificações técnicas e scripts de datalogger."
},
    {
        "nome": "PAM - DHN",
        "icone": "🌊",
        "link": "https://pam.dhn.mar.mil.br/",
        "desc": "Plataforma de Dados Ambientais Marinhos da DHN."
    },
    {
        "nome": "SHOWCast (SMM)",
        "icone": "🌍",
        "link": "https://www.smm.mil.br/smm/satelite/SHOWCast_v_2_5_1/SHOWCast.html",
        "desc": "Visualização de dados de satélite e meteorologia do SMM."
    },
    {
        "nome": "Rastreamento CLS (Novo)",
        "icone": "🛰️",
        "link": "https://vts.clsbrasil.com/",
        "desc": "Mapa com a posição atual dos equipamentos via sistema CLS mais recente."
    },
    {
        "nome": "Rastreamento CLS (Backup)",
        "icone": "📡",
        "link": "https://argos-system.cls.fr/argos-cwi2/login.html",
        "desc": "Sistema alternativo de rastreamento satelital caso o principal não esteja disponível."
    },
    {
        "nome": "OPERANTAR Live",
        "icone": "❄️",
        "link": "https://www.operantar.live",
        "desc": "Acompanhamento em tempo real das operações na Antártica."
    },
    {
        "nome": "Oceano Live",
        "icone": "🔵",
        "link": "https://www.oceano.live",
        "desc": "Monitoramento oceanográfico ao vivo."
    },
    {
        "nome": "Boia Abrolhos",
        "icone": "🐠",
        "link": "http://boia-abrolhos.herokuapp.com/",
        "desc": "Dados em tempo real da unidade de monitoramento em Abrolhos."
    },
    {
        "nome": "Boia Alcatrazes",
        "icone": "🏝️",
        "link": "http://alcatrazes.herokuapp.com",
        "desc": "Monitoramento oceanográfico do Arquipélago de Alcatrazes."
    },
    {
        "nome": "BNDO - Marinha",
        "icone": "🗄️",
        "link": "https://www.marinha.mil.br/chm/bndo",
        "desc": "Banco Nacional de Dados Oceanográficos."
    },
    {
        "nome": "IDEM - DHN",
        "icone": "🗺️",
        "link": "https://idem.dhn.mar.mil.br/geonetwork/srv/por/catalog.search#/home",
        "desc": "Infraestrutura de Dados Espaciais Marinhos."
    },
    {
        "nome": "PNBOIA",
        "icone": "📍",
        "link": "https://www.marinha.mil.br/chm/dados-do-goos-brasil/pnboia",
        "desc": "Programa Nacional de Boias - Dados do GOOS Brasil."
    },
    {
        "nome": "Modelagem Numérica",
        "icone": "💻",
        "link": "https://www.marinha.mil.br/chm/dados-do-smm-modelagem-numerica-tela-de-chamada",
        "desc": "Dados de modelos numéricos do Serviço Meteorológico Marinho."
    },
    {
        "nome": "Corrente de Maré",
        "icone": "⏳",
        "link": "https://www.marinha.mil.br/chm/dados-do-smm/corrente-de-mare",
        "desc": "Previsões e dados de correntes de maré da Marinha."
    },
    {
        "nome": "Controle de Ponto",
        "icone": "⏱️",
        "link": "https://controle-ponto-front.vercel.app/login",
        "desc": "Sistema de controle de ponto e registro de jornada."
    },
    {
        "nome": "Banco de Ideias",
        "icone": "💡",
        "link": "https://docs.google.com/forms/d/e/1FAIpQLSdDopECrhQyr1Z8PepxBQvYhDT2WbufJ7RBKbqSNJ3qOP-8yw/viewform",
        "desc": "Envie sugestões de novos projetos e funcionalidades."
    },
    {
        "nome": "Visualizador CSV",
        "icone": "📊",
        "link": "https://visualizadoresgraficoscsv.streamlit.app/",
        "desc": "Visualize gráficos interativos a partir de CSVs."
    },
    {
        "nome": "Visualizador DADOS",
        "icone": "💾",
        "link": "http://10.0.0.35:8502",
        "desc": "Visualize gráficos interativos a partir do Banco de dados local."
    },
    {
        "nome": "Drive REMOBS",
        "icone": "🗂️",
        "link": "https://drive.google.com/drive/folders/1kaRpRkv7gnEOcsHAx9L6cAgdUe2Rdtq5",
        "desc": "Repositório oficial REMOBS para documentos e materiais de apoio."
    },
    {
        "nome": "Publique seu App",
        "icone": "🚀",
        "link": "https://share.streamlit.io/new",
        "desc": "Crie e publique seu app no Streamlit Cloud."
    },
]


# ------------------------------------------------------------------
# TÍTULO
# ------------------------------------------------------------------
st.markdown(
    """
    <div style="text-align:center; margin-bottom: 3rem;">
        <h1 style="
            font-size: 2.8rem;
            font-weight: 700;
            letter-spacing: 0.4px;
        ">
            🛰️ Portal REMOBS
        </h1>
        <p style="
            color:#9fb3c8;
            font-size:1.1rem;
            max-width: 760px;
            margin: 0 auto;
        ">
            Acesso centralizado aos sistemas de monitoramento, operação e análise de dados oceânicos
        </p>
    </div>
    """,
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













