import streamlit as st

# ------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Hub de Aplicações | REMOBS",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# NEURODESIGN + MODERN CSS (Glassmorphism & Gradient Glow)
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset de Fonte */
html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

.stApp {
    background-color: #0d1117;
}

/* Banner de Destaque */
.hero-banner {
    background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
    border-radius: 24px;
    padding: 40px;
    text-align: center;
    margin-bottom: 35px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.05);
}

.hero-title {
    font-size: 32px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    font-size: 16px;
    color: #94a3b8;
    max-width: 600px;
    margin: 0 auto;
}

/* Títulos de Seções (Neurodesign: Categorias Claras) */
.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #f8fafc;
    margin: 25px 0 15px 5px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Container de Carrossel/Grid */
.apps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

/* CARD PREMIUM (Inspirado em Apple/PlayStore) */
.app-card {
    background: rgba(22, 28, 45, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    height: 220px;
    justify-content: space-between;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    position: relative;
    overflow: hidden;
    text-decoration: none !important;
}

.app-card:hover {
    transform: translateY(-5px);
    border-color: #38bdf8;
    background: rgba(22, 28, 45, 0.9);
    box-shadow: 0 12px 30px rgba(56, 189, 248, 0.15);
}

/* Efeito de brilho de fundo no Hover */
.app-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(135deg, rgba(56,189,248,0.05) 0%, transparent 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.app-card:hover::before {
    opacity: 1;
}

.card-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}

.app-icon-box {
    font-size: 38px;
    background: rgba(255,255,255,0.03);
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* Badges de Estado (Gera Curiosidade/Urgência) */
.badge {
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-live { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-novo { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
.badge-util { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }

.card-body {
    margin-top: 12px;
    flex-grow: 1;
}

.app-name {
    font-size: 17px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 6px;
}

.app-desc {
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Customização Estilosa do Input de Busca */
div.stTextInput > div > div > input {
    background-color: #161c2d !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
}
div.stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}

/* Remove a linha vermelha feia do link padrão do Streamlit */
a {
    text-decoration: none !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# BASE DE DADOS DOS APPS (Com Categorias e Badges Psicológicas)
# ------------------------------------------------------------------
apps = [
    {
        "nome": "REMOBS Store",
        "icone": "🛰️",
        "link": "https://remobstore.streamlit.app/",
        "desc": "Dashboard central de monitoramento meteoceanográfico em tempo real da costa brasileira.",
        "categoria": "Operações Marítimas",
        "badge": "LIVE"
    },
    {
        "nome": "Janela Operacional Marítima",
        "icone": "⚓",
        "link": "https://janelaoperacionalmare.streamlit.app/",
        "desc": "Indicador inteligente de janelas operacionais seguras para grandes embarcações.",
        "categoria": "Operações Marítimas",
        "badge": "LIVE"
    },
    {
        "nome": "SEASMART",
        "icone": "🐬",
        "link": "https://seasmart.streamlit.app/",
        "desc": "Medições de maré de alta precisão com sistema de alertas automáticos.",
        "categoria": "Operações Marítimas",
        "badge": "POPULAR"
    },
    {
        "nome": "OceanWatch Live",
        "icone": "🌊",
        "link": "https://dinamicoastal.streamlit.app/",
        "desc": "Análise integrada de dados costeiros em tempo real: ondas, vento e correntes.",
        "categoria": "Operações Marítimas",
        "badge": "LIVE"
    },
    {
        "nome": "Atlas Dinâmico BR",
        "icone": "🗺️",
        "link": "https://atlasdinamicobr.streamlit.app/",
        "desc": "Explore mapas interativos e habitats marinhos dinâmicos do Brasil.",
        "categoria": "Ciência & Dados",
        "badge": "NOVO"
    },
    {
        "nome": "Componentes Maré",
        "icone": "📈",
        "link": "https://componentesmare.streamlit.app/",
        "desc": "Decomposição e visualização harmônica dos componentes da maré em tempo real.",
        "categoria": "Ciência & Dados",
        "badge": "UTIL"
    },
    {
        "nome": "Previsão Maré",
        "icone": "📊",
        "link": "https://previsaomare.streamlit.app/",
        "desc": "Modelagem matemática e acompanhamento de previsões de maré detalhadas.",
        "categoria": "Ciência & Dados",
        "badge": "UTIL"
    },
    {
        "nome": "Biblioteca Inteligente",
        "icone": "📚",
        "link": "https://bibliometrixdash.streamlit.app/",
        "desc": "Análise bibliométrica avançada e geração de dashboards científicos.",
        "categoria": "Ciência & Dados",
        "badge": "NOVO"
    },
    {
        "nome": "Comparador de Arquivos TID",
        "icone": "🔄",
        "link": "https://comparadorarquivostid.streamlit.app/",
        "desc": "Algoritmo para validação e comparação de séries temporais de maré (.tid).",
        "categoria": "Ciência & Dados",
        "badge": "UTIL"
    },
    {
        "nome": "Visualizador CSV",
        "icone": "📉",
        "link": "https://visualizadoresgraficoscsv.streamlit.app/",
        "desc": "Transforme qualquer arquivo CSV em gráficos interativos instantaneamente.",
        "categoria": "Utilidades",
        "badge": "UTIL"
    },
    {
        "nome": "Formatador ABNT",
        "icone": "📝",
        "link": "https://formatadorabnt.streamlit.app/",
        "desc": "Geração automatizada de referências bibliográficas no padrão ABNT.",
        "categoria": "Utilidades",
        "badge": "UTIL"
    },
    {
        "nome": "Banco de Ideias",
        "icone": "💡",
        "link": "https://docs.google.com/forms/d/e/1FAIpQLSdDopECrhQyr1Z8PepxBQvYhDT2WbufJ7RBKbqSNJ3qOP-8yw/viewform",
        "desc": "Tem uma ideia inovadora? Envie sugestões de novos projetos e ferramentas.",
        "categoria": "Comunidade",
        "badge": "NOVO"
    },
    {
        "nome": "Publique seu App",
        "icone": "🚀",
        "link": "https://share.streamlit.io/new",
        "desc": "Desenvolveu algo incrível? Publique seu aplicativo no Streamlit Cloud agora.",
        "categoria": "Comunidade",
        "badge": "NOVO"
    }
]

# ------------------------------------------------------------------
# HERO BANNER (Primeiro Impacto Visual)
# ------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Ecosistema de Aplicações Oceanográficas</div>
    <div class="hero-subtitle">Explore ferramentas computacionais dinâmicas aplicadas à ciência, engenharia costeira e operações marítimas em tempo real.</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# FILTRO DE BUSCA INTELIGENTE
# ------------------------------------------------------------------
busca = st.text_input("🔍 O que você está procurando hoje?", placeholder="Ex: Maré, Dashboard, CSV, ABNT...")

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
# FUNÇÃO PARA RENDERIZAR O CARD EM HTML (Garantindo Estilo Limpo)
# ------------------------------------------------------------------
def render_card(app):
    badge_class = "badge-util"
    if app["badge"] == "LIVE": badge_class = "badge-live"
    elif app["badge"] == "NOVO": badge_class = "badge-novo"
    
    return f"""
    <a href="{app['link']}" target="_blank" style="text-decoration: none;">
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
# RENDERIZAÇÃO DAS CATEGORIAS (Neurodesign: Evita Sobrecarga Cognitiva)
# ------------------------------------------------------------------
categorias = ["Operações Marítimas", "Ciência & Dados", "Utilidades", "Comunidade"]

for cat in categorias:
    # Filtrar apps pertencentes a esta categoria específica
    apps_da_categoria = [a for a in apps_filtrados if a["categoria"] == cat]
    
    if apps_da_categoria:
        st.markdown(f'<div class="section-title">📂 {cat}</div>', unsafe_allow_html=True)
        
        # Criação da grade adaptativa do Streamlit
        cols = st.columns(3)
        for idx, app in enumerate(apps_da_categoria):
            col_idx = idx % 3
            with cols[col_idx]:
                st.markdown(render_card(app), unsafe_allow_html=True)
