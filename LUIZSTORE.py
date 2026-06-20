import streamlit as st
import requests

# ------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (Deve ser obrigatoriamente o primeiro comando)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Portal de Soluções Industriais e Portuárias",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 📌 URL OFICIAL DA SUA API NA RENDER
API_URL = "https://mysaas-demo.onrender.com"

# ------------------------------------------------------------------
# CONTROLE DE SESSÃO ANTI-LOOP ULTRA-BLINDADO (JAVASCRIPT-FORCED)
# ------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "token" not in st.session_state:
    st.session_state["token"] = ""
if "usuario_email" not in st.session_state:
    st.session_state["usuario_email"] = ""
if "login_processado" not in st.session_state:
    st.session_state["login_processado"] = False

# Captura os parâmetros da URL
parametros = st.query_params

# Se existem parâmetros e a sessão local ainda diz que não está autenticado
if "token" in parametros and "email" in parametros and not st.session_state["autenticado"]:
    # Define os estados na memória estável (o Streamlit NÃO perde isso ao recarregar)
    st.session_state["autenticado"] = True
    st.session_state["token"] = parametros["token"]
    st.session_state["usuario_email"] = parametros["email"]
    st.session_state["login_processado"] = True
    
    # 🛡️ BLINDAGEM MÁXIMA JAVASCRIPT: Força o navegador a limpar a URL imediatamente
    # Isso remove os parâmetros ?token=... e ?email=... direto da barra de endereços do Chrome/Edge
    # sem fazer o Streamlit disparar loops internos de recarregamento.
    st.components.v1.html(
        """
        <script>
            window.parent.history.replaceState({}, document.title, window.parent.location.pathname);
            window.location.reload();
        </script>
        """,
        height=0,
        width=0
    )
    st.stop() # Para a execução do script Python aqui para o HTML/JS acima rodar primeiro

# Se por acaso a URL limpou mas o Streamlit Cloud tentar ler parâmetros fantasmas na cache:
if st.session_state["login_processado"]:
    # Forçamos o estado a se manter true e ignoramos qualquer parâmetro de URL
    st.session_state["autenticado"] = True

# ------------------------------------------------------------------
# NEURODESIGN B2B + MODERN CSS ... (O resto do seu código continua exatamente igual daqui para baixo)

# ------------------------------------------------------------------
# NEURODESIGN B2B + MODERN CSS ... (O resto do código continua igual daqui para baixo)
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

/* Container do Form de Login */
.login-box {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 40px;
    max-width: 450px;
    margin: 80px auto 0 auto;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    text-align: center;
}

.login-title {
    font-size: 24px;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 8px;
}

.login-subtitle {
    font-size: 13px;
    color: #94a3b8;
    margin-bottom: 24px;
}

/* Banner Executivo */
.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 16px;
    padding: 45px 30px;
    text-align: center;
    margin-bottom: 35px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.05);
    position: relative;
}

.user-badge {
    position: absolute;
    top: 15px;
    right: 20px;
    font-size: 11px;
    background: rgba(56, 189, 248, 0.1);
    color: #38bdf8;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(56, 189, 248, 0.2);
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

.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #38bdf8;
    margin: 35px 0 15px 5px;
    display: flex;
    align-items: center;
    gap: 12px;
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

/* Customização Inputs */
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
# LÓGICA DE INTERFACE: TELA DE LOGIN VS CONTEÚDO RESTRITO
# ------------------------------------------------------------------
if not st.session_state["autenticado"]:
    # Renderiza o cabeçalho visual do formulário de login via HTML customizado
    st.markdown("""
    <div class="login-box">
        <div class="login-title">🛡️ Portal Industrial B2B</div>
        <div class="login-subtitle">Insira suas credenciais corporativas autorizadas para acessar os sistemas de monitoramento.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Alinha os inputs no centro da página para acompanhar o design do box
    _, col_centro, _ = st.columns([1, 2, 1])
    
    with col_centro:
        # 1. FLUXO TRADICIONAL (E-MAIL E SENHA)
        email = st.text_input("E-mail corporativo", value="luizccindras@gmail.com", key="login_email")
        senha = st.text_input("Senha de acesso", type="password", key="login_senha")
        
        if st.button("🔑 Autenticar com Senha", use_container_width=True):
            try:
                resposta = requests.post(
                    f"{API_URL}/auth/login-front",
                    json={"email": email, "password": senha},
                    timeout=10
                )
                dados = resposta.json()
                
                if resposta.status_code == 200:
                    st.session_state["autenticado"] = True
                    st.session_state["token"] = dados.get("access_token")
                    st.session_state["usuario_email"] = email
                    st.success("Autenticação bem-sucedida! Carregando portal...")
                    st.rerun()
                else:
                    st.error(f"Erro: {dados.get('detail', 'Acesso negado.')}")
            except Exception as e:
                st.error("Falha ao comunicar com o servidor de autenticação.")
        
        # DIVISOR VISUAL
        st.markdown("""
        <div style="position: relative; flex-direction: row; display: flex; align-items: center; margin: 20px 0;">
            <div style="flex-grow: 1; border-top: 1px solid #1f2937;"></div>
            <span style="flex-shrink: 1; margin: 0 15px; color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">ou</span>
            <div style="flex-grow: 1; border-top: 1px solid #1f2937;"></div>
        </div>
        """, unsafe_allow_html=True)

        # 2. FLUXO BOTÃO GOOGLE
        try:
            # Busca a URL do Supabase direto do seu backend na Render
            res_url = requests.get(f"{API_URL}/auth/supabase-url", timeout=5)
            if res_url.status_code == 200:
                supabase_project_url = res_url.json().get("supabase_url")
                
                # Monta a URL exata de redirecionamento que o Google precisa
                callback_url = f"{API_URL}/auth/callback"
                google_auth_url = f"{supabase_project_url}/auth/v1/authorize?provider=google&redirect_to={callback_url}"
                
                # Renderiza o botão HTML do Google estilizado
                botao_google_html = f"""
                <a href="{google_auth_url}" target="_self" style="text-decoration: none !important;">
                    <div style="background-color: #ffffff; color: #111827; font-weight: 600; font-size: 14px; padding: 10px; border-radius: 8px; display: flex; align-items: center; justify-content: center; gap: 10px; border: 1px solid #e5e7eb; cursor: pointer; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: background-color 0.2s;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" alt="Google" width="18" style="margin-bottom: 0px;">
                        Acessar com o Google
                    </div>
                </a>
                """
                st.markdown(botao_google_html, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Não foi possível carregar a URL de autenticação do Google do servidor backend.")
        except Exception as e:
            st.warning("⚠️ Servidor backend offline ou inacessível para login social.")
else:
    # ------------------------------------------------------------------
    # PORTAL DE CARDS (SÓ ABRE SE ESTIVER AUTENTICADO)
    # ------------------------------------------------------------------
    
    # BASE DE DADOS DOS CARDS
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
            "desc": "Sua empresa tem um problem logístico ou ambiental sob medida? Solicite uma ferramenta personalizada aqui.",
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

    # HERO BANNER EXECUTIVO
    st.markdown(f"""
    <div class="hero-banner">
        <div class="user-badge">👤 {st.session_state['usuario_email']}</div>
        <div class="hero-title">Hub de Soluções Inteligentes para o Setor Marítimo e Industrial</div>
        <div class="hero-subtitle">Reduza riscos operacionais, otimize suas janelas logísticas e acesse dados em tempo real para proteger seus ativos e otimizar processos de tomada de decisão.</div>
    </div>
    """, unsafe_allow_html=True)

    # BARRA LATERAL OU TOPO: BOTÃO DE LOGOUT
    if st.sidebar.button("🚪 Encerrar Sessão"):
        st.session_state["autenticado"] = False
        st.session_state["token"] = ""
        st.session_state["usuario_email"] = ""
        st.rerun()

    # BUSCA INTELIGENTE POR PROBLEMA
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

    # RENDERIZADOR DE CARD B2B
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

    # CATEGORIZAÇÃO FOCADA NAS DORES DO CLIENTE
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
