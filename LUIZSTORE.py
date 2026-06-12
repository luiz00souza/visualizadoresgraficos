import streamlit as st

# ------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Portal de Soluções Industriais e Portuárias",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# NEURODESIGN B2B + MODERN CSS (Foco em Confiança e Solidez)
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
    background-color: #0b0f19;
    color: #f1f5f9;
}

.stApp {
    background-color: #0b0f19;
}

/* Banner Executivo (Foco na Proposta de Valor) */
.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 16px;
    padding: 45px 30px;
    text-align: center;
    margin-bottom: 35px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.05);
}

.hero-title {
    font-size: 34px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 12px;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    font-size: 16px;
    color: #94a3b8;
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Títulos de Seção focados em Resolução de Problemas */
.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #38bdf8;
    margin: 35px 0 15px 5px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.apps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

/* CARD INDUSTRIAL PREMIUM */
.app-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    height: 230px;
    justify-content: space-between;
    transition: all 0.25s ease-in-out;
    position: relative;
}

.app-card:hover {
    transform: translateY(-4px);
    border-color: #38bdf8;
    background: #131c2e;
    box-shadow: 0 10px 25px rgba(56, 189, 248, 0.08);
}

.card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.app-icon-box {
    font-size: 32px;
    background: rgba(56, 189, 248, 0.05);
    width: 54px;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    border: 1px solid rgba(56, 189, 248, 0.1);
}

/* Badges Corporativos de Impacto Direto */
.badge {
    font-size: 10px;
    font-weight: 700;
    padding: 5px 12px;
    border-radius: 6px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.badge-critico { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }
.badge-logistica { background: rgba(56, 189, 248, 0.1); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); }
.badge-custo { background: rgba(34, 197, 94, 0.1); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.2); }
.badge-produtividade { background: rgba(168, 85, 247, 0.1); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.2); }

.card-body {
    margin-top: 16px;
    flex-grow: 1;
}

.app-name {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 8px;
}

.app-desc {
    font-size: 13.5px;
    color: #94a3b8;
    line-height: 1.4;
}

/* Customização Input de Busca */
div.stTextInput > div > div > input {
    background-color: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #1f2937 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}
div.stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}

a { text-decoration: none !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# BASE DE DADOS TRADUZIDA PARA NEGÓCIOS E SOLUÇÃO DE PROBLEMAS
# ------------------------------------------------------------------
apps = [
    {
        "nome": "Monitoramento Costeiro Live",
        "icone": "🛰️",
        "link": "https://remobstore.streamlit.app/",
        "desc": "Acompanhamento em tempo real das condições meteoceanográficas para antecipação de eventos severos na costa.",
        "categoria": "Gestão de Riscos & Segurança",
        "badge": "CRÍTICO"
    },
    {
        "nome": "Janela Operacional Segura",
        "icone": "⚓",
        "link": "https://janelaoperacionalmare.streamlit.app/",
        "desc": "Indicador de janelas ideais e seguras para atracação e navegação de grandes navios, evitando atrasos e multas.",
        "categoria": "Eficiência Logística & Operações",
        "badge": "LOGÍSTICA"
    },
    {
        "nome": "Alertas Automáticos SeaSmart",
        "icone": "🐬",
        "link": "https://seasmart.streamlit.app/",
        "desc": "Sistema de segurança preditiva com alertas automáticos sobre variações críticas de maré.",
        "categoria": "Gestão de Riscos & Segurança",
        "badge": "CRÍTICO"
    },
    {
        "nome": "Radar Integrado OceanWatch",
        "icone": "🌊",
        "link": "https://dinamicoastal.streamlit.app/",
        "desc": "Dados consolidados de ondas, correntes e ventos para tomadas de decisão rápidas em operações marítimas.",
        "categoria": "Gestão de Riscos & Segurança",
        "badge": "CRÍTICO"
    },
    {
        "nome": "Mapeador Ambiental Dinâmico",
        "icone": "🗺️",
        "link": "https://atlasdinamicobr.streamlit.app/",
        "desc": "Visualizador de habitats costeiros para suporte em licenciamentos ambientais e estudos de impacto.",
        "categoria": "Inteligência Científica & Relatórios",
        "badge": "PRODUTIVIDADE"
    },
    {
        "nome": "Decompositor de Tendências",
        "icone": "📈",
        "link": "https://componentesmare.streamlit.app/",
        "desc": "Análise isolada das variações de maré para engenharia portuária e planejamento de estruturas de longo prazo.",
        "categoria": "Inteligência Científica & Relatórios",
        "badge": "PRODUTIVIDADE"
    },
    {
        "nome": "Preditor Marítimo de Alta Precisão",
        "icone": "📊",
        "link": "https://previsaomare.streamlit.app/",
        "desc": "Modelagem estatística de previsão de marés para subsidiar cronogramas logísticos de médio e longo prazo.",
        "categoria": "Eficiência Logística & Operações",
        "badge": "LOGÍSTICA"
    },
    {
        "nome": "Inteligência Documental",
        "icone": "📚",
        "link": "https://bibliometrixdash.streamlit.app/",
        "desc": "Agrupador inteligente de dados científicos e papers para auditorias e embasamento técnico de relatórios.",
        "categoria": "Inteligência Científica & Relatórios",
        "badge": "PRODUTIVIDADE"
    },
    {
        "nome": "Validador de Séries Temporais (TID)",
        "icone": "🔄",
        "link": "https://comparadorarquivostid.streamlit.app/",
        "desc": "Auditoria automatizada e comparação de arquivos de dados de maré para compliance regulatório.",
        "categoria": "Eficiência Logística & Operações",
        "badge": "REDUÇÃO DE CUSTO"
    },
    {
        "nome": "Transformador Instantâneo de Dados",
        "icone": "📉",
        "link": "https://visualizadoresgraficoscsv.streamlit.app/",
        "desc": "Transforme planilhas pesadas de auditoria (CSVs) em gráficos visuais claros para reuniões executivas.",
        "categoria": "Suporte à Decisão",
        "badge": "REDUÇÃO DE CUSTO"
    },
    {
        "nome": "Automação Normativa ABNT",
        "icone": "📝",
        "link": "https://formatadorabnt.streamlit.app/",
        "desc": "Reduza o tempo gasto na formatação de relatórios técnicos exigidos por órgãos fiscalizadores.",
        "categoria": "Suporte à Decisão",
        "badge": "REDUÇÃO DE CUSTO"
    },
    {
        "nome": "Central de Demandas Corporativas",
        "icone": "💡",
        "link": "https://docs.google.com/forms/d/e/1FAIpQLSdDopECrhQyr1Z8PepxBQvYhDT2WbufJ7RBKbqSNJ3qOP-8yw/viewform",
        "desc": "Sua empresa tem um problema logístico ou ambiental sob medida? Solicite uma ferramenta personalizada aqui.",
        "categoria": "Suporte à Decisão",
        "badge": "PRODUTIVIDADE"
    },
    {
        "nome": "Laboratório de Deploy",
        "icone": "🚀",
        "link": "https://share.streamlit.io/new",
        "desc": "Ambiente para desenvolvedores internos homologarem novas soluções para a indústria.",
        "categoria": "Suporte à Decisão",
        "badge": "PRODUTIVIDADE"
    }
]

# ------------------------------------------------------------------
# HERO BANNER EXECUTIVO
# ------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Hub de Soluções Inteligentes para o Setor Marítimo e Industrial</div>
    <div class="hero-subtitle">Reduza riscos operacionais, otimize suas janelas logísticas e acesse dados em tempo real para proteger seus ativos e otimizar processos de tomada de decisão.</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# BUSCA INTELIGENTE POR PROBLEMA
# ------------------------------------------------------------------
busca = st.text_input("🔍 Qual problema operacional ou de conformidade você precisa resolver hoje?", placeholder="Ex: Evitar atraso de navio, gerar relatórios, monitorar em tempo real...")

if busca:
    apps_filtrados = [
        app for app in apps
        if busca.lower() in app["nome"].lower()
        or busca.lower() in app["desc"].lower()
        or busca.lower() in app["categoria"].lower()
    ]
else:
    apps_filtrados = apps

# ------------------------------------------------------------------
# RENDERIZADOR DE CARD B2B
# ------------------------------------------------------------------
def render_card(app):
    badge_class = "badge-produtividade"
    if app["badge"] == "CRÍTICO": badge_class = "badge-critico"
    elif app["badge"] == "LOGÍSTICA": badge_class = "badge-logistica"
    elif app["badge"] == "REDUÇÃO DE CUSTO": badge_class = "badge-custo"
    
    return f"""
    <a href="{app['link']}" target="_blank">
        <div class="app-card">
            <div class="card-top">
                <div class="app-icon-box">{app['icone']}</div>
                <span class="badge {badge_class}">{app['badge']}</span>
            </div>
            <div class="card-body">
                <div class="app-name">{app['nome']}</div>
                <div class="app-desc">{app['desc']}</div>
            </div>
        </div>
    </a>
    """

# ------------------------------------------------------------------
# CATEGORIZAÇÃO FOCADA NAS DORES DO CLIENTE
# ------------------------------------------------------------------
categorias = ["Gestão de Riscos & Segurança", "Eficiência Logística & Operações", "Inteligência Científica & Relatórios", "Suporte à Decisão"]

for cat in categorias:
    apps_da_categoria = [a for a in apps_filtrados if a["categoria"] == cat]
    
    if apps_da_categoria:
        st.markdown(f'<div class="section-title">🛡️ {cat}</div>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, app in enumerate(apps_da_categoria):
            col_idx = idx % 3
            with cols[col_idx]:
                st.markdown(render_card(app), unsafe_allow_html=True)
