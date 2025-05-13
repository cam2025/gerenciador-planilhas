import streamlit as st
import pandas as pd
import io
import base64
from urllib.parse import quote

st.set_page_config(
    page_title="Gerenciador de Planilhas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para baixar dados como Excel
def get_excel_download_link(df, filename):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    binary_data = output.getvalue()
    b64 = base64.b64encode(binary_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Baixar como Excel</a>'
    return href

# Função para aplicar filtros em um dataframe
def apply_filters(df, filters):
    filtered_df = df.copy()
    for column, value in filters.items():
        if value and column in filtered_df.columns:
            if isinstance(value, list):  # Para filtros de seleção múltipla
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            else:  # Para filtros de texto
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False)]
    return filtered_df

# Função para criar controles de filtro para um dataframe
def create_filters(df, key_prefix):
    filters = {}
    
    # Seleciona colunas para filtro (limitado a 10 para performance)
    filter_columns = st.multiselect(
        "Selecione colunas para filtrar:",
        options=df.columns.tolist(),
        key=f"{key_prefix}_select_columns"
    )
    
    # Cria um filtro para cada coluna selecionada
    for col in filter_columns:
        # Determina o tipo de filtro baseado no tipo de dados
        if df[col].nunique() < 20 and df[col].nunique() > 0:  # Para colunas categóricas com poucos valores únicos
            unique_values = df[col].dropna().unique().tolist()
            selected_values = st.multiselect(
                f"Filtrar {col}:",
                options=unique_values,
                key=f"{key_prefix}_{col}"
            )
            if selected_values:
                filters[col] = selected_values
        else:  # Para colunas com muitos valores únicos ou numéricas
            filter_text = st.text_input(
                f"Filtrar {col} (digite um valor):",
                key=f"{key_prefix}_{col}"
            )
            if filter_text:
                filters[col] = filter_text
    
    return filters

# Inicializa o estado da sessão para armazenar os dataframes
if 'campanhas_df' not in st.session_state:
    st.session_state.campanhas_df = None
if 'conjuntos_df' not in st.session_state:
    st.session_state.conjuntos_df = None
if 'anuncios_df' not in st.session_state:
    st.session_state.anuncios_df = None
if 'vendas_df' not in st.session_state:
    st.session_state.vendas_df = None

# Título da aplicação
st.title("Gerenciador de Planilhas de Marketing")
st.markdown("Faça upload, analise e combine suas planilhas de campanhas, conjuntos, anúncios e vendas.")

# Sidebar para upload de arquivos
with st.sidebar:
    st.header("Upload de Arquivos")
    
    # Upload de Campanhas
    st.subheader("Campanhas")
    campanhas_file = st.file_uploader("Carregar planilha de Campanhas", type=["csv", "xlsx"], key="campanhas_upload")
    if campanhas_file:
        try:
            if campanhas_file.name.endswith('.csv'):
                st.session_state.campanhas_df = pd.read_csv(campanhas_file)
            else:
                st.session_state.campanhas_df = pd.read_excel(campanhas_file)
            st.success(f"Campanhas carregadas: {st.session_state.campanhas_df.shape[0]} linhas, {st.session_state.campanhas_df.shape[1]} colunas")
        except Exception as e:
            st.error(f"Erro ao carregar arquivo de campanhas: {str(e)}")
    
    # Upload de Conjuntos
    st.subheader("Conjuntos")
    conjuntos_file = st.file_uploader("Carregar planilha de Conjuntos", type=["csv", "xlsx"], key="conjuntos_upload")
    if conjuntos_file:
        try:
            if conjuntos_file.name.endswith('.csv'):
                st.session_state.conjuntos_df = pd.read_csv(conjuntos_file)
            else:
                st.session_state.conjuntos_df = pd.read_excel(conjuntos_file)
            st.success(f"Conjuntos carregados: {st.session_state.conjuntos_df.shape[0]} linhas, {st.session_state.conjuntos_df.shape[1]} colunas")
        except Exception as e:
            st.error(f"Erro ao carregar arquivo de conjuntos: {str(e)}")
    
    # Upload de Anúncios
    st.subheader("Anúncios")
    anuncios_file = st.file_uploader("Carregar planilha de Anúncios", type=["csv", "xlsx"], key="anuncios_upload")
    if anuncios_file:
        try:
            if anuncios_file.name.endswith('.csv'):
                st.session_state.anuncios_df = pd.read_csv(anuncios_file)
            else:
                st.session_state.anuncios_df = pd.read_excel(anuncios_file)
            st.success(f"Anúncios carregados: {st.session_state.anuncios_df.shape[0]} linhas, {st.session_state.anuncios_df.shape[1]} colunas")
        except Exception as e:
            st.error(f"Erro ao carregar arquivo de anúncios: {str(e)}")
    
    # Upload de Vendas
    st.subheader("Vendas")
    vendas_file = st.file_uploader("Carregar planilha de Vendas", type=["csv", "xlsx"], key="vendas_upload")
    if vendas_file:
        try:
            if vendas_file.name.endswith('.csv'):
                st.session_state.vendas_df = pd.read_csv(vendas_file)
            else:
                st.session_state.vendas_df = pd.read_excel(vendas_file)
            st.success(f"Vendas carregadas: {st.session_state.vendas_df.shape[0]} linhas, {st.session_state.vendas_df.shape[1]} colunas")
        except Exception as e:
            st.error(f"Erro ao carregar arquivo de vendas: {str(e)}")

# Abas principais da aplicação
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Campanhas", "Conjuntos", "Anúncios", "Vendas", "Combinações"])

# Aba de Campanhas
with tab1:
    st.header("Dados de Campanhas")
    
    if st.session_state.campanhas_df is not None:
        # Interface de filtro
        st.subheader("Filtros")
        with st.expander("Configurar filtros", expanded=False):
            filters = create_filters(st.session_state.campanhas_df, "camp")
        
        # Aplica filtros
        filtered_df = apply_filters(st.session_state.campanhas_df, filters)
        
        # Resumo dos dados
        st.write(f"Mostrando {filtered_df.shape[0]} de {st.session_state.campanhas_df.shape[0]} linhas após aplicar filtros")
        
        # Opções de download
        st.markdown(get_excel_download_link(filtered_df, "campanhas_filtradas"), unsafe_allow_html=True)
        
        # Mostra os dados
        st.dataframe(filtered_df, height=400)
    else:
        st.info("Faça upload de uma planilha de campanhas usando o painel lateral.")

# Aba de Conjuntos
with tab2:
    st.header("Dados de Conjuntos")
    
    if st.session_state.conjuntos_df is not None:
        # Interface de filtro
        st.subheader("Filtros")
        with st.expander("Configurar filtros", expanded=False):
            filters = create_filters(st.session_state.conjuntos_df, "conj")
        
        # Aplica filtros
        filtered_df = apply_filters(st.session_state.conjuntos_df, filters)
        
        # Resumo dos dados
        st.write(f"Mostrando {filtered_df.shape[0]} de {st.session_state.conjuntos_df.shape[0]} linhas após aplicar filtros")
        
        # Opções de download
        st.markdown(get_excel_download_link(filtered_df, "conjuntos_filtrados"), unsafe_allow_html=True)
        
        # Mostra os dados
        st.dataframe(filtered_df, height=400)
    else:
        st.info("Faça upload de uma planilha de conjuntos usando o painel lateral.")

# Aba de Anúncios
with tab3:
    st.header("Dados de Anúncios")
    
    if st.session_state.anuncios_df is not None:
        # Interface de filtro
        st.subheader("Filtros")
        with st.expander("Configurar filtros", expanded=False):
            filters = create_filters(st.session_state.anuncios_df, "anun")
        
        # Aplica filtros
        filtered_df = apply_filters(st.session_state.anuncios_df, filters)
        
        # Resumo dos dados
        st.write(f"Mostrando {filtered_df.shape[0]} de {st.session_state.anuncios_df.shape[0]} linhas após aplicar filtros")
        
        # Opções de download
        st.markdown(get_excel_download_link(filtered_df, "anuncios_filtrados"), unsafe_allow_html=True)
        
        # Mostra os dados
        st.dataframe(filtered_df, height=400)
    else:
        st.info("Faça upload de uma planilha de anúncios usando o painel lateral.")

# Aba de Vendas
with tab4:
    st.header("Dados de Vendas")
    
    if st.session_state.vendas_df is not None:
        # Interface de filtro
        st.subheader("Filtros")
        with st.expander("Configurar filtros", expanded=False):
            filters = create_filters(st.session_state.vendas_df, "vend")
        
        # Aplica filtros
        filtered_df = apply_filters(st.session_state.vendas_df, filters)
        
        # Resumo dos dados
        st.write(f"Mostrando {filtered_df.shape[0]} de {st.session_state.vendas_df.shape[0]} linhas após aplicar filtros")
        
        # Opções de download
        st.markdown(get_excel_download_link(filtered_df, "vendas_filtradas"), unsafe_allow_html=True)
        
        # Mostra os dados
        st.dataframe(filtered_df, height=400)
    else:
        st.info("Faça upload de uma planilha de vendas usando o painel lateral.")

# Aba de Combinações
with tab5:
    st.header("Combinações Personalizadas")
    
    # Verifica quais dataframes estão disponíveis
    available_dfs = []
    if st.session_state.campanhas_df is not None:
        available_dfs.append("Campanhas")
    if st.session_state.conjuntos_df is not None:
        available_dfs.append("Conjuntos")
    if st.session_state.anuncios_df is not None:
        available_dfs.append("Anúncios")
    if st.session_state.vendas_df is not None:
        available_dfs.append("Vendas")
    
    if len(available_dfs) >= 2:
        st.subheader("Configurar Combinação")
        
        # Seleciona as tabelas para combinar
        selected_tables = st.multiselect(
            "Selecione as tabelas para combinar:",
            options=available_dfs,
            default=available_dfs[:2]
        )
        
        if len(selected_tables) >= 2:
            # Para cada tabela selecionada, escolhe as colunas para incluir
            selected_columns = {}
            for table in selected_tables:
                if table == "Campanhas" and st.session_state.campanhas_df is not None:
                    selected_columns[table] = st.multiselect(
                        f"Selecione as colunas de {table}:",
                        options=st.session_state.campanhas_df.columns.tolist(),
                        default=st.session_state.campanhas_df.columns.tolist()[:5]
                    )
                elif table == "Conjuntos" and st.session_state.conjuntos_df is not None:
                    selected_columns[table] = st.multiselect(
                        f"Selecione as colunas de {table}:",
                        options=st.session_state.conjuntos_df.columns.tolist(),
                        default=st.session_state.conjuntos_df.columns.tolist()[:5]
                    )
                elif table == "Anúncios" and st.session_state.anuncios_df is not None:
                    selected_columns[table] = st.multiselect(
                        f"Selecione as colunas de {table}:",
                        options=st.session_state.anuncios_df.columns.tolist(),
                        default=st.session_state.anuncios_df.columns.tolist()[:5]
                    )
                elif table == "Vendas" and st.session_state.vendas_df is not None:
                    selected_columns[table] = st.multiselect(
                        f"Selecione as colunas de {table}:",
                        options=st.session_state.vendas_df.columns.tolist(),
                        default=st.session_state.vendas_df.columns.tolist()[:5]
                    )
            
            # Configuração para junção de tabelas
            st.subheader("Configurar Junção")
            
            # Seleciona o tipo de junção
            join_type = st.selectbox(
                "Tipo de junção:",
                options=["inner", "left", "right", "outer"],
                format_func=lambda x: {
                    "inner": "Inner Join (apenas correspondências)",
                    "left": "Left Join (mantém todos da primeira tabela)",
                    "right": "Right Join (mantém todos da segunda tabela)",
                    "outer": "Outer Join (mantém todos de ambas as tabelas)"
                }[x]
            )
            
            # Escolhe as colunas para junção
            join_keys = {}
            
            # Para cada par de tabelas, escolhe as colunas de junção
            for i in range(len(selected_tables) - 1):
                table1 = selected_tables[i]
                table2 = selected_tables[i+1]
                
                if table1 == "Campanhas":
                    df1 = st.session_state.campanhas_df
                elif table1 == "Conjuntos":
                    df1 = st.session_state.conjuntos_df
                elif table1 == "Anúncios":
                    df1 = st.session_state.anuncios_df
                elif table1 == "Vendas":
                    df1 = st.session_state.vendas_df
                
                if table2 == "Campanhas":
                    df2 = st.session_state.campanhas_df
                elif table2 == "Conjuntos":
                    df2 = st.session_state.conjuntos_df
                elif table2 == "Anúncios":
                    df2 = st.session_state.anuncios_df
                elif table2 == "Vendas":
                    df2 = st.session_state.vendas_df
                
                col1, col2 = st.columns(2)
                
                with col1:
                    join_key1 = st.selectbox(
                        f"Coluna de {table1} para junção com {table2}:",
                        options=df1.columns.tolist()
                    )
                
                with col2:
                    join_key2 = st.selectbox(
                        f"Coluna de {table2} para junção:",
                        options=df2.columns.tolist()
                    )
                
                join_keys[(table1, table2)] = (join_key1, join_key2)
            
            # Botão para executar a combinação
            if st.button("Combinar Dados"):
                # Preparar dataframes com colunas selecionadas
                dfs = {}
                
                for table in selected_tables:
                    if table == "Campanhas":
                        dfs[table] = st.session_state.campanhas_df[selected_columns[table]].copy()
                    elif table == "Conjuntos":
                        dfs[table] = st.session_state.conjuntos_df[selected_columns[table]].copy()
                    elif table == "Anúncios":
                        dfs[table] = st.session_state.anuncios_df[selected_columns[table]].copy()
                    elif table == "Vendas":
                        dfs[table] = st.session_state.vendas_df[selected_columns[table]].copy()
                
                # Executar a combinação
                result_df = dfs[selected_tables[0]].copy()
                
                for i in range(len(selected_tables) - 1):
                    table1 = selected_tables[i]
                    table2 = selected_tables[i+1]
                    
                    join_col1, join_col2 = join_keys[(table1, table2)]
                    
                    # Adiciona prefixo às colunas para evitar conflitos
                    result_df = result_df.merge(
                        dfs[table2],
                        left_on=join_col1,
                        right_on=join_col2,
                        how=join_type,
                        suffixes=(f'_{table1}', f'_{table2}')
                    )
                
                # Mostra resultado
                st.subheader("Resultado da Combinação")
                st.write(f"Linhas resultantes: {result_df.shape[0]}, Colunas: {result_df.shape[1]}")
                
                # Opções de download
                st.markdown(get_excel_download_link(result_df, "combinacao_personalizada"), unsafe_allow_html=True)
                
                # Mostra os dados
                st.dataframe(result_df, height=400)
        else:
            st.warning("Selecione pelo menos duas tabelas para combinar.")
    else:
        st.info("Carregue pelo menos duas planilhas para criar combinações personalizadas.")

# Instruções de uso
with st.sidebar:
    st.markdown("---")
    st.subheader("Instruções de Uso")
    st.markdown("""
    1. Faça upload das planilhas usando os botões acima
    2. Navegue entre as abas para visualizar os dados
    3. Use os filtros para refinar a visualização
    4. Na aba "Combinações", crie análises personalizadas
    5. Exporte os resultados como Excel para uso posterior
    """)
    
    st.markdown("---")
    st.subheader("Suporte a Arquivos Grandes")
    st.markdown("""
    Esta aplicação foi otimizada para lidar com arquivos grandes:
    - Carrega arquivos por partes quando necessário
    - Filtra dados antes de exibir para melhor desempenho
    - Permite combinar dados seletivamente para economizar memória
    """)

# Rodapé da aplicação
st.markdown("---")
st.markdown(
    "Desenvolvido para análise de campanhas, conjuntos, anúncios e vendas. Suporta arquivos grandes de até 100 mil linhas."
)
Adicionar aplicação principal
