import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from HOVMOLLER_streamlit import *
from OPERACIONAL_UMI_SIMPLIFICADO import *
from espelhadiretorio_FTP_SIG1000 import *
import altair as alt
import re
import json
import os

CAMINHO_LOG = r"C:\Users\campo\Desktop\SistamaQAQC\DASH\alertas2.log"
caminho_config=r"C:\Users\campo\Desktop\SistamaQAQC\DASH\f_configSensores.csv"
json_path = r"C:\Users\campo\Desktop\SistamaQAQC\DASH\dicionarios.json"


@st.cache_data
def carregar_dados(todos_os_resultados):
    df = todos_os_resultados
    df.rename(columns={"Teste": "Filtro"}, inplace=True)
    return df

def exibir_matriz_calor(df, parametro_selecionado):
    df_filtrado = df[df['parameter_column'] == parametro_selecionado].copy()
    if not df_filtrado.empty:
        st.subheader(f"Tabela de Dados: {parametro_selecionado}")
        df_filtrado['Porcentagem Falhos'] = df_filtrado['Porcentagem Falhos'].clip(upper=100)
        matriz_calor = df_filtrado.pivot_table(
            index="Parametro", columns="Filtro", values="Porcentagem Falhos", aggfunc="mean"
        ).reset_index()
        matriz_calor_melt = matriz_calor.melt(id_vars=["Parametro"], var_name="Filtro", value_name="Porcentagem Falhos")
        chart = alt.Chart(matriz_calor_melt).mark_rect().encode(
            x='Filtro:N',
            y=alt.Y('Parametro:N', sort=alt.SortField(field='Indice Extraido', order='ascending')),
            color=alt.Color('Porcentagem Falhos:Q', scale=alt.Scale(domain=[0, 100])),
            tooltip=['Parametro', 'Filtro', 'Porcentagem Falhos']
        ).properties(
            title=f"Matriz de Calor: {parametro_selecionado}",
            width=800,
            height=500)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(df_filtrado)  # Exibir dados sem a coluna auxiliar
    else:
        st.warning(f"Não há dados para {parametro_selecionado}.")

def exibir_tabela(df):
    """Exibe a tabela com os dados e inclui opção para download."""
    st.subheader("Tabela de Dados")
    st.sidebar.subheader("Filtrar por Período")
    data_inicio = st.sidebar.date_input("Data Inicial", df['GMT-03:00'].min().date())
    data_fim = st.sidebar.date_input("Data Final", df['GMT-03:00'].max().date())
    if data_inicio > data_fim:
        st.error("A data inicial não pode ser posterior à data final.")
        return
    df_filtrado = df[(df['GMT-03:00'].dt.date >= data_inicio) & (df['GMT-03:00'].dt.date <= data_fim)]
    df_filtrado = df_filtrado[[col for col in df_filtrado.columns if not col.endswith("flag")]]
    st.dataframe(df_filtrado)
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="Baixar Dados",
        data=csv,
        file_name="dados_mare_filtrados.csv",
        mime="text/csv"
    )

def exibir_graficos(df):
    st.subheader("Gráficos Dinâmicos")    
    df_exibicao = df.copy()
    colunas_para_graficos = [col for col in df.columns if not col.startswith('Flag') ]
    abas = st.tabs(colunas_para_graficos)
    def gerar_grafico(coluna):
        cores_legenda = {4: '#D72638', 3: '#FFD700', 0: '#348AA7'}
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_exibicao['GMT-03:00'], 
            y=df_exibicao[coluna], 
            mode='lines',
            name=coluna,
            line=dict(color='blue'), 
            showlegend=False
        ))
        flag_col = f'Flag_{coluna}'
        if flag_col in df.columns:
            for flag_value, color in cores_legenda.items():
                mask = df[flag_col] == flag_value
                fig.add_trace(go.Scatter(
                    x=df_exibicao['GMT-03:00'][mask], 
                    y=df_exibicao[coluna][mask], 
                    mode='markers',
                    name=f'Flag {flag_value}',
                    marker=dict(color=color, size=8),
                    visible=True if flag_value == 4 else 'legendonly'
                ))
        fig.update_layout(
            title=f"Série Temporal de {coluna}",
            yaxis_title=coluna,
            legend_title="Flag",
            showlegend=True,
            xaxis=dict(
                rangeslider=dict(visible=False),
                type='date'
            )
        )
        return fig
    for aba, coluna in zip(abas, colunas_para_graficos):
        with aba:
            st.plotly_chart(gerar_grafico(coluna), use_container_width=True)

def formatar_dados(dados):
    """Converte um dicionário aninhado em um DataFrame formatado."""
    dados_formatados = []
    for categoria, filtros in dados.items():
        for tipo_filtro, parametros in filtros.items():
            for parametro, valores in parametros.items():
                for filtro, valor in valores.items():
                    dados_formatados.append({
                        'Categoria': categoria,
                        'Tipo de Filtro': tipo_filtro,
                        'Parâmetro': parametro,
                        'Filtro': filtro,
                        'Valor': valor})
    return pd.DataFrame(dados_formatados)

def exibir_grafico_e_tabela_qc(df,opcao):
    """Exibe conteúdo da aba Maré"""
    opcao = st.radio("Escolha a opção de visualização", ["Gráfico", "Tabela"])
    if opcao == "Gráfico":
        exibir_graficos(df)
    elif opcao == "Tabela":
        exibir_tabela(df)
def criar_grafico(df, titulo):
    """Cria um gráfico de matriz de calor usando Altair."""
    df['Porcentagem Falhos'] = df['Porcentagem Falhos'].clip(upper=100)
    def extrair_indice(valor):    
        if isinstance(valor, str) and '#' in valor:
            return int(valor.split('#')[-1])
        return 0
    df.loc[:, 'Indice Extraido'] = df['Parametro'].apply(extrair_indice)
    matriz_calor = df.pivot_table(index="Parametro", columns="Filtro", values="Porcentagem Falhos", aggfunc="mean").reset_index()
    matriz_calor_melt = matriz_calor.melt(id_vars=["Parametro"], var_name="Filtro", value_name="Porcentagem Falhos")
    matriz_calor_melt.loc[:, 'Indice Extraido'] = matriz_calor_melt['Parametro'].apply(extrair_indice)
    matriz_calor_melt = matriz_calor_melt.sort_values(by="Indice Extraido", ascending=True)
    chart = alt.Chart(matriz_calor_melt).mark_rect().encode(
        x='Filtro:N',
        y=alt.Y('Parametro:N', sort=list(matriz_calor_melt['Parametro'].unique())),  # Ordenação manual baseada nos dados
        color=alt.Color('Porcentagem Falhos:Q', scale=alt.Scale(domain=[0, 100])),
        tooltip=['Parametro', 'Filtro', 'Porcentagem Falhos']
    ).properties(
        title=titulo,
        width=800,
        height=500)
    return chart

def normalizar_texto(texto):
    texto = str(texto).lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = re.sub(r'[^a-z0-9]', '', texto)
    return texto

def reconstruir_json(df):
    """Reconstrói um dicionário JSON a partir de um DataFrame."""
    novo_json = {}
    for _, row in df.iterrows():
        categoria = row['Categoria']
        tipo_filtro = row['Tipo de Filtro']
        parametro = row['Parâmetro']
        filtro = row['Filtro']
        try:
            valor = int(row['Valor'])
        except ValueError:
            valor = 0  # Define um valor padrão caso não seja possível converter
        if categoria not in novo_json:
            novo_json[categoria] = {}
        if tipo_filtro not in novo_json[categoria]:
            novo_json[categoria][tipo_filtro] = {}
        if parametro not in novo_json[categoria][tipo_filtro]:
            novo_json[categoria][tipo_filtro][parametro] = {}
        novo_json[categoria][tipo_filtro][parametro][filtro] = valor
    return novo_json
def wide_para_long_multivariaveis(df_wide):
    df_wide['Time'] = pd.to_datetime(df_wide['GMT-03:00'])
    df_wide['Dia'] = df_wide['Time'].dt.strftime('%Y-%m-%d')
    df_wide['Hora'] = df_wide['Time'].dt.strftime('%H:%M')
    var_cell_cols = [
        col for col in df_wide.columns
        if col not in ['Time', 'Dia', 'Hora'] and not col.startswith('Flag')]
    data = []
    for col in var_cell_cols:
        m = re.match(r"(?P<variavel>.+)_Cell#(?P<cell_idx>\d+)", col)
        if m:
            variavel = m.group("variavel")
            cell_idx = int(m.group("cell_idx"))
            cell = f"Cell#{cell_idx}"
            temp_df = df_wide[['Time', 'Dia', 'Hora', col]].copy()
            temp_df = temp_df.rename(columns={col: 'Valor'})
            temp_df['Cell'] = cell
            temp_df['Variavel'] = variavel
            temp_df['Cell_Index'] = cell_idx
            data.append(temp_df)
    df_long = pd.concat(data, ignore_index=True)
    df_long = df_long[['Time', 'Dia', 'Hora', 'Cell', 'Cell_Index', 'Variavel', 'Valor']]
    return df_long

def criar_heatmap_temporal_altair(dataframe, eixo_x, eixo_y, valor, titulo, x_order=None, y_order=None, vmin=None, vmax=None):
    df_plot = dataframe.copy()
    df_plot['Cell_Index'] = df_plot['Cell'].str.extract(r'Cell#(\d+)').astype(int)
    if y_order is None:
        y_order_df = df_plot[['Cell', 'Cell_Index']].drop_duplicates().sort_values('Cell_Index')
        y_order = y_order_df['Cell'].tolist()
    if x_order is not None:
        df_plot[eixo_x] = pd.Categorical(df_plot[eixo_x], categories=x_order, ordered=True)
    if vmin is not None and vmax is not None:
        color_scale = alt.Scale(domain=[vmin, vmax], scheme='inferno')
    else:
        color_scale = alt.Scale(scheme='inferno')
    chart = alt.Chart(df_plot).mark_rect().encode(
        x=alt.X(f'{eixo_x}:N', title=eixo_x),
        y=alt.Y(f'{eixo_y}:N', title=eixo_y, sort=y_order),
        color=alt.Color(f'{valor}:Q', scale=color_scale),
        tooltip=['Cell', 'Cell_Index', eixo_x, valor]
    ).properties(
        width=900,
        height=400,
        title=titulo)
    return chart

def heatmap_media_por_dia_var(df_long, variavel, dias_ordenados, cell_order):
    df_filtrado = df_long[df_long['Variavel'] == variavel]
    matriz = df_filtrado.pivot_table(index='Cell', columns='Dia', values='Valor', aggfunc='mean').reset_index()
    melt = matriz.melt(id_vars=['Cell'], var_name='Dia', value_name='Valor')
    return criar_heatmap_temporal_altair(melt, 'Dia', 'Cell', 'Valor',
                                         titulo=f'Mapa de calor - Média {variavel} por Célula e Dia',
                                         x_order=dias_ordenados, y_order=cell_order)

def heatmap_por_hora_no_dia_var(df_long, variavel, dia, cell_order): 
    df_filtrado = df_long[(df_long['Variavel'] == variavel) & (df_long['Dia'] == dia)]
    horas_ordenadas = sorted(df_filtrado['Hora'].unique())
    matriz = df_filtrado.pivot_table(index='Cell', columns='Hora', values='Valor', aggfunc='mean').reset_index()
    melt = matriz.melt(id_vars=['Cell'], var_name='Hora', value_name='Valor')
    vmin = vmax = None
    if variavel.lower() == 'v2':
        vmin = -5
        vmax = 5
    return criar_heatmap_temporal_altair(
        melt, 'Hora', 'Cell', 'Valor',
        titulo=f"Mapa de calor - {variavel} detalhado para {dia}",
        x_order=horas_ordenadas, y_order=cell_order,
        vmin=vmin, vmax=vmax 
    ) 

def matriz_calor_correntes(df,opcao):
    df_filtrado = df[df["parameter_column"] == opcao]
    df_amplitude = df_filtrado[df_filtrado['Parametro'].str.contains('Amplitude', case=False, na=False)]
    df_velocidade = df_filtrado[df_filtrado['Parametro'].str.contains('Speed', case=False, na=False)]
    df_direcao = df_filtrado[df_filtrado['Parametro'].str.contains('Direction', case=False, na=False)]
    df_outros = df_filtrado[~df_filtrado['Parametro'].str.contains('Amplitude|Speed|Direction|A1|A2|A3|A4|C1|C2|C3|C4|v1|v2|v3|v4', case=False, na=False)]
    st.subheader("Gráfico de Outros Parâmetros")
    st.altair_chart(criar_grafico(df_outros, "Matriz de Calor: Outros Parâmetros"))
    st.subheader("Tabela de Outros Parâmetros")
    st.dataframe(df_outros)
    st.subheader("Gráfico de Amplitude")
    st.altair_chart(criar_grafico(df_amplitude, "Matriz de Calor: Amplitude"))
    st.subheader("Tabela de Amplitude")
    st.dataframe(df_amplitude)
    st.subheader("Gráfico de Velocidade")
    st.altair_chart(criar_grafico(df_velocidade, "Matriz de Calor: Velocidade"))
    st.subheader("Tabela de Velocidade")
    st.dataframe(df_velocidade)
    st.subheader("Gráfico de Direção")
    st.altair_chart(criar_grafico(df_direcao, "Matriz de Calor: Direção"))
    st.subheader("Tabela de Direção")
    st.dataframe(df_direcao)

def processar_dados(df, opcao,df_matriz_qc):
    """ Processa e exibe os dados de acordo com a opção selecionada. """
    df = df.set_index("GMT-03:00", drop=False)
    st.sidebar.subheader("Opções de Visualização")
    st.sidebar.write(f"Total de registros: {len(df)}")
    st.sidebar.subheader("Filtro de Data")
    min_date, max_date = df.index.min(), df.index.max()
    date_range = st.sidebar.date_input("Selecione o intervalo", [min_date, max_date], min_value=min_date, max_value=max_date)
    if len(date_range) == 2:
        start_date, end_date = map(pd.to_datetime, date_range)
        df.index = pd.to_datetime(df.index)
        df = df[(df.index >= start_date) & (df.index <= end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]
    st.sidebar.subheader("Colunas para Visualização")
    colunas_disponiveis = [col for col in df.columns if col not in ["TIMESTAMP", "RECORD"]]
    colunas_selecionadas = st.sidebar.multiselect("Selecione as colunas", colunas_disponiveis, default=colunas_disponiveis)
    aba1, aba2, aba3, aba4, aba5,aba6,aba7 = st.tabs([ "Dados Processados","QA/QC","Dicionários","Hovmoller","HeatMap temporal","ALERTAS","Sobre"])
    with aba1:
        exibir_grafico_e_tabela_qc(df,opcao)
        # if opcao =="MARE":
            # streamlituploadautomatico(df,time_col = 'GMT-03:00',height_col = 'Pressure_S1', latitude =-21,tipo_de_filtro='Filtro Médio',avg_delta_t = 300)# UTILIZAR PARA ARQUIVO PREDEFINIDO COM CONFIGURACOES PREDEFINIDAS
    with aba2: 
        if opcao!="CORRENTES":
            exibir_matriz_calor(df_matriz_qc,opcao)   
        if opcao=="CORRENTES":
            matriz_calor_correntes(df_matriz_qc,opcao)
    with aba3:
        with open(json_path, 'r') as file:
            dados = json.load(file)        
        dados = formatar_dados(dados)   
        dados["Valor"] = pd.to_numeric(dados["Valor"], errors="coerce").astype(float)
        categorias = dados["Categoria"].unique().tolist()
        categoria_selecionada = st.selectbox("Selecione uma categoria:", ["Todas"] + categorias)
        if categoria_selecionada != "Todas":
            dadosf = dados[dados["Categoria"] == categoria_selecionada]
        else:
            dadosf = dados
        edited_df = st.data_editor(dadosf, disabled=["Categoria", "Tipo de Filtro", "Parâmetro", "Filtro"], key="editable_table")
        if st.button("Salvar Alterações"):
            dados_atualizados = reconstruir_json(edited_df)
            if categoria_selecionada != "Todas":
                dados.loc[dados["Categoria"] == categoria_selecionada] = dados_atualizados
            else:
                dados = dados_atualizados
            with open(json_path, 'w') as file:
                def formatar_floats(d):
                    if isinstance(d, dict):
                        return {k: formatar_floats(v) for k, v in d.items()}
                    elif isinstance(d, list):
                        return [formatar_floats(i) for i in d]
                    elif isinstance(d, float):
                        return round(d, 2) if d % 1 else int(d)  # opcionalmente converte 6.0 em 6
                    return d
                dados_formatados = formatar_floats(dados)
                with open(json_path, 'w') as file:
                    json.dump(dados_formatados, file, indent=4)
            st.success("Alterações salvas com sucesso!")
    with aba4:
        if opcao in {"CORRENTES"}:
            st.header("Gráfico Hovmöller")
            app_hovmoller(dados=df, time_col="GMT-03:00")
        else:
            st.info("Não há dados disponíveis no momento.")
    with aba5:
        # st.header("Heatmap")
        if opcao in {"CORRENTES"}:
            df_wide = df
            df_long = wide_para_long_multivariaveis(df_wide)
            dias_ordenados = sorted(df_long['Dia'].unique())
            cell_order_df = df_long[['Cell', 'Cell_Index']].drop_duplicates().sort_values('Cell_Index', ascending=False)
            cell_order = cell_order_df['Cell'].tolist()
            variaveis = df_long['Variavel'].unique().tolist()
            variavel_selecionada = st.selectbox("Selecione a variável", variaveis)
            st.subheader(f"Heatmap Temporal 1 - Média por Dia para {variavel_selecionada}")
            chart1 = heatmap_media_por_dia_var(df_long, variavel_selecionada, dias_ordenados, cell_order)
            st.altair_chart(chart1, use_container_width=True)
            st.subheader(f"Heatmap Temporal - Detalhado por hora para {variavel_selecionada}")
            dia_selecionado = st.selectbox("Selecione um dia", dias_ordenados)
            chart2 = heatmap_por_hora_no_dia_var(df_long, variavel_selecionada, dia_selecionado, cell_order)
            st.altair_chart(chart2, use_container_width=True)
            df_wide.drop(columns=['Time', 'Dia', 'Hora'], inplace=True)
        else:
            st.info("Não há dados disponíveis no momento.")
    with aba6:
        st.info("Não há dados disponíveis no momento.")
        # alertasnostreamlit.mostrar_alertas()

    with aba7:
        st.subheader("Configurações aplicadas nesta estação")
        
        df_cfg = st.session_state.get("df_config_estacao", None)
    
        if df_cfg is None or len(df_cfg) == 0:
            st.warning("Nenhuma configuração encontrada para esta estação.")
        else:
            # Busca rápida
            busca = st.text_input("Buscar na configuração (qualquer campo):")
    
            df_show = df_cfg.copy()
            
            # garante que estamos trabalhando com apenas a config da estação
            df_show = df_show.reset_index(drop=True)
            
            # wide -> long (coluna / valor)
            df_show = df_show.melt(
                var_name="Configuração",
                value_name="Valor"
            )
            
            # remove configs vazias
            df_show = df_show.dropna(subset=["Valor"])    
            if busca:
                mask = df_show.astype(str).apply(lambda row: row.str.contains(busca, case=False, na=False)).any(axis=1)
                df_show = df_show[mask]
    
            st.dataframe(df_show, use_container_width=True)
    
            # Download
            csv_cfg = df_show.to_csv(index=False)
            st.download_button(
                "📥 Baixar configuração (CSV)",
                data=csv_cfg,
                file_name=f"config_estacao_registro_{st.session_state.registro_id}.csv",
                mime="text/csv"
            )
def selecionar_estacao():
    st.title("Selecione a Estação")

    st.markdown(
        """
        Antes de acessar o sistema, selecione a estação
        meteoceanográfica que deseja analisar.
        """
    )

    registro_id = st.selectbox(
        "Estação (registro_id)",
        options=list(range(1, 11)),
        index=None,
        placeholder="Selecione a estação"
    )

    if registro_id is not None:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("➡️ Acessar dados"):
                st.session_state.registro_id = registro_id
                st.rerun()

def home_page():
    st.markdown(
        """
        <style>
        .home-container {
            text-align: center;
            padding-top: 100px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="home-container">
            <h1>🌊 SEASMART</h1>
            <h3>Decisão segura começa no mar</h3>
            <p>
            Plataforma integrada para controle de qualidade, visualização
            e análise de dados meteoceanográficos.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Entrar no sistema", use_container_width=True):
            st.session_state.entrou = True
            st.rerun()
@st.cache_data(show_spinner=True)
def carregar_estacao(registro_id, caminho_config):
    df, todos_os_resultados, lat, long, df_config = processar_sensor(
        registro_id=registro_id,
        caminho_config=caminho_config
    )

    df_map = {
        "ONDAS_NAO_DIRECIONAIS":df,
        "METEOROLOGIA": df,
        "MARE": df,
        "ONDAS": df,
        "CORRENTES": df,
    }
    df_matriz_qc = carregar_dados(todos_os_resultados)
    lista_totais = []
    for tipo in df_matriz_qc['parameter_column'].unique():
        df_grupo = df_matriz_qc[df_matriz_qc['parameter_column'] == tipo]
        df_soma = df_grupo.groupby('Parametro', as_index=False)['Porcentagem Falhos'].sum()
        df_soma['parameter_column'] = tipo
        df_soma['Filtro'] = '_TOTAL'
        for col in df_matriz_qc.columns:
            if col not in df_soma.columns:
                df_soma[col] = None
        df_soma = df_soma[df_matriz_qc.columns.tolist()]
        lista_totais.append(df_soma)

    df_totais = pd.concat(lista_totais, ignore_index=True)
    df_matriz_qc = pd.concat([df_matriz_qc, df_totais], ignore_index=True)

    return df_map, df_matriz_qc, lat, long, df_config
def voltar_para_home():
    st.session_state.entrou = False
    st.session_state.registro_id = None
    st.rerun()

def main():

    if "entrou" not in st.session_state:
        st.session_state.entrou = False

    if "registro_id" not in st.session_state:
        st.session_state.registro_id = None

    # ===== HOME =====
    if not st.session_state.entrou:
        home_page()
        return

    # ===== ESTAÇÃO =====
    if st.session_state.registro_id is None:
        selecionar_estacao()
        return 

    # ===== CARREGAMENTO =====
    registro_id = st.session_state.registro_id

    df_map, df_matriz_qc, lat, long, df_config = carregar_estacao(
        registro_id,
        caminho_config
    )
    
    st.session_state.df_config_estacao = df_config
    opcao = df_config["tipo_sensor"].iloc[0]
    st.sidebar.info(f"Sensor ativo: {opcao}")

    with st.sidebar:
        st.divider()
        if st.button("🏠 Voltar para Home"):
            voltar_para_home()

    # ===== UI =====
    st.title("SEASMART. Decisão segura começa no mar.")

    if opcao in df_map:
        processar_dados(df_map[opcao], opcao,df_matriz_qc)
    else:
        st.error(f"tipo_sensor='{opcao}' não existe no df_map. Chaves disponíveis: {list(df_map.keys())}")

if __name__ == "__main__":
    main()
