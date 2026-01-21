#%% Modulos 
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Configuração de página (uma vez, no topo)
st.set_page_config(layout='wide')

#%% Função principal
def app_hovmoller(dados, time_col="GMT-03:00",
                  variavel_alvo=None, tipo_de_plot=None):
    """
    Gera gráfico Hovmöller interativo no Streamlit.
    
    Parâmetros
    ----------
    dados : pd.DataFrame
        DataFrame já carregado.
    time_col : str
        Nome da coluna de tempo.
    variavel_alvo : str, opcional
        Variável escolhida pelo usuário ('Amplitude', 'Speed', 'Direction').
    tipo_de_plot : str, opcional
        Tipo de gráfico ('plot_simples', 'plot_flags').
    """

    # Configurações internas
    dados = dados.set_index(time_col)

    # Seleção pelo usuário, caso não passada
    if variavel_alvo is None:
        variavel_alvo = st.selectbox('Escolha a variável:', ['Amplitude', 'Speed', 'Direction'])
    if tipo_de_plot is None:
        tipo_de_plot = st.selectbox('Tipo de gráfico:', ['plot_simples', 'plot_flags'])

    # Seleção de colunas
    colunas_alvo = []
    for coluna in dados.columns:
        if 'Speed' in variavel_alvo:
            if f'{variavel_alvo}(m/s)_Cell#' in coluna and f'Flag_{variavel_alvo}' not in coluna:
                colunas_alvo.append(coluna)
        else:
            if f'{variavel_alvo}_Cell#' in coluna and f'Flag_{variavel_alvo}' not in coluna:
                colunas_alvo.append(coluna)

    dados_alvo = dados[colunas_alvo]
    if 'Speed' in variavel_alvo:
        dados_alvo = dados_alvo[dados_alvo > -1.5].ffill().bfill()

    # Flags
    colunas_flag = [col for col in dados.columns if f'Flag_{variavel_alvo}' in col]
    dados_flag = dados[colunas_flag]

    # Coordenadas das flags
    profundidades = list(dados_alvo.columns)
    z = dados_alvo.transpose().interpolate(axis=1).ffill(axis=1).bfill(axis=1).values

    x_flag3, y_flag3 = [], []
    x_flag4, y_flag4 = [], []

    for col_idx, col in enumerate(profundidades):
        for row_idx, time in enumerate(dados_flag.index):
            flag_value = dados_flag.iloc[row_idx, col_idx]
            if flag_value == 3:
                x_flag3.append(time)
                y_flag3.append(col_idx)
            elif flag_value == 4:
                x_flag4.append(time)
                y_flag4.append(col_idx)

    # Eixo y invertido
    quantidade_de_profundidades = len(dados_alvo.columns)
    profundidade_final = np.max(range(quantidade_de_profundidades)) + 1
    resolucao = 1
    all_labels = np.arange(profundidade_final, profundidade_final - quantidade_de_profundidades * resolucao, -resolucao)
    step = 2
    ticks = np.arange(0, quantidade_de_profundidades, step)
    labels = all_labels[::step]

    # Dataviz
    fig = go.Figure()

    if 'plot_simples' in tipo_de_plot:
        fig.add_trace(go.Contour(
            z=z,
            x=dados_alvo.index,
            y=np.arange(len(profundidades)),
            colorscale='Jet',
            colorbar=dict(title=f'{variavel_alvo}'),
            contours=dict(showlines=False),
            zmin=np.nanmin(z),
            zmax=np.nanmax(z),
            zauto=False
        ))

    if 'plot_flags' in tipo_de_plot:
        fig.add_trace(go.Contour(
            z=z,
            x=dados_alvo.index,
            y=np.arange(len(profundidades)),
            colorscale='Jet',
            colorbar=dict(title=f'{variavel_alvo}'),
            contours=dict(showlines=False)
        ))
        fig.add_trace(go.Scatter(x=x_flag3, y=y_flag3, mode='markers',
                                 marker=dict(color='black', size=5), name='Dados suspeitos'))
        fig.add_trace(go.Scatter(x=x_flag4, y=y_flag4, mode='markers',
                                 marker=dict(color='red', size=5), name='Dados reprovados'))

    fig.update_layout(
        title=f'{variavel_alvo}: profundidade x tempo',
        xaxis_title='Tempo',
        yaxis_title='Profundidade',
        yaxis=dict(autorange=True, tickmode='array', tickvals=ticks, ticktext=labels),
        width=1000,
        height=500,
        template='ggplot2',
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)


#%% Exemplo de uso direto (sem main)
# Ler Excel
#caminho = r"C:\Users\campo\Desktop\SistamaQAQC\Grafico_Hovmoller\DADOS_CORRENTES.xlsx"
#df_c = pd.read_excel(caminho)

# Criar abas
# tab1, tab2 = st.tabs(["📊 Hovmöller", "ℹ️ Outra aba"])

# with tab1:
#     st.header("Gráfico Hovmöller")
#     # Chamando a função diretamente pelo nome
#     app_hovmoller(dados=df_c, time_col="GMT-03:00")
    
# with tab2:
#     st.write("Conteúdo de outra aba...")

