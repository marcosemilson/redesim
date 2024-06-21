import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar dados
uploaded_file = st.file_uploader("Empresa_Junta.xlsx", type="xlsx")
if uploaded_file is not None:
    dfs = pd.read_excel(uploaded_file, sheet_name=None)
    df_empresas = dfs['Empresas']
    df_evento = dfs['Evento']
    df_atividade_primaria = dfs['Atividade_Primaria']
    df_atividade_secundaria = dfs['Atividade_Secundaria']
    df_socio = dfs['Socio']

    # Limpeza e tratamento dos dados (exemplo)
    df_empresas.dropna(subset=['Número Redesim'], inplace=True) # Remover empresas sem Redesim

    # Integração das informações das diferentes planilhas (exemplo)
    df_empresas_completo = df_empresas.merge(df_socio, on='Número Redesim', how='left')

    # Página "Visão Geral"
    st.title('Visão Geral das Empresas')

    total_empresas = df_empresas['Número Redesim'].nunique()
    st.metric("Número total de empresas", total_empresas)

    st.subheader('Distribuição por Porte')
    fig, ax = plt.subplots()
    sns.countplot(data=df_empresas, x='Porte empresa', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader('Distribuição por Município (Top 10)')
    fig, ax = plt.subplots()
    top_municipios = df_empresas['Nome município'].value_counts().head(10)
    sns.barplot(x=top_municipios.index, y=top_municipios.values, ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader('Distribuição por Natureza Jurídica (Top 10)')
    fig, ax = plt.subplots()
    top_naturezas = df_empresas['Natureza jurídica'].value_counts().head(10)
    sns.barplot(x=top_naturezas.index, y=top_naturezas.values, ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Página "Empresas"
    st.title('Informações de Empresas')

    busca = st.text_input('Buscar empresa por nome ou Número Redesim:')
    if busca:
        df_busca = df_empresas_completo[
            (df_empresas_completo['Nome empresa'].str.contains(busca, case=False)) | 
            (df_empresas_completo['Número Redesim'].astype(str).str.contains(busca))
        ]
    else:
        df_busca = df_empresas_completo
        df_busca

    st.subheader('Empresas Encontradas:')
    if 'Nome município_x' in df_busca.columns:  # Check if column exists
        st.write(df_busca[['Número Redesim', 'Nome empresa', 'Porte empresa', 'Nome município_x']].to_markdown(index=False, numalign="left", stralign="left"))
    else:
        st.warning("A coluna 'Nome município' não foi encontrada nos dados filtrados.")
        st.write(df_busca[['Número Redesim', 'Nome empresa', 'Porte empresa']].to_markdown(index=False, numalign="left", stralign="left"))  # Display without the missing column

    if not df_busca.empty:
        empresa_selecionada = st.selectbox('Selecione uma empresa para ver detalhes:', df_busca['Nome empresa'])

        # Exibir informações da empresa selecionada
        st.write(df_busca[df_busca['Nome empresa'] == empresa_selecionada].to_markdown(index=False, numalign="left", stralign="left"))

        # Exibir sócios da empresa selecionada
        socios_empresa = df_socio[df_socio['Número Redesim'] == df_busca[df_busca['Nome empresa'] == empresa_selecionada]['Número Redesim'].iloc[0]]
        if not socios_empresa.empty:
            st.write("\nSócios:")
            st.write(socios_empresa[['Nome sócio', 'Descrição qualificacao']].to_markdown(index=False, numalign="left", stralign="left"))

        # Exibir atividades primárias e secundárias da empresa selecionada
        atividades_primaria_empresa = df_atividade_primaria[df_atividade_primaria['Número Redesim'] == df_busca[df_busca['Nome empresa'] == empresa_selecionada]['Número Redesim'].iloc[0]]
        atividades_secundaria_empresa = df_atividade_secundaria[df_atividade_secundaria['Número Redesim'] == df_busca[df_busca['Nome empresa'] == empresa_selecionada]['Número Redesim'].iloc[0]]
        if not atividades_primaria_empresa.empty:
            st.write("\nAtividade Primária:")
            st.write(atividades_primaria_empresa[['Código CNAE', 'Objeto social']].to_markdown(index=False, numalign="left", stralign="left"))
        if not atividades_secundaria_empresa.empty:
            st.write("\nAtividades Secundárias:")
            st.write(atividades_secundaria_empresa[['Código CNAE']].to_markdown(index=False, numalign="left", stralign="left"))

        # Exibir eventos da empresa selecionada
        alteracoes_empresa = df_evento[df_evento['Número Redesim'] == df_busca[df_busca['Nome empresa'] == empresa_selecionada]['Número Redesim'].iloc[0]].copy()  # Explicit copy

        if not alteracoes_empresa.empty:
            alteracoes_empresa.sort_values(by='Identificação solicitação', ascending=False, inplace=True)

            # Explicitly convert NaNs to NaT (datetime's null value)
            alteracoes_empresa['Data evento'] = pd.to_datetime(alteracoes_empresa['Data evento'], errors='coerce')

            # Apply strftime only to non-null values, fill NaN with empty string
            alteracoes_empresa.loc[alteracoes_empresa['Data evento'].notnull(), 'Data evento'] = alteracoes_empresa.loc[alteracoes_empresa['Data evento'].notnull(), 'Data evento'].dt.strftime('%Y-%m-%d')
            alteracoes_empresa['Data evento'] = alteracoes_empresa['Data evento'].fillna('')

            st.write("\nEventos:")
            st.write(alteracoes_empresa[['Data evento', 'Descrição evento', 'Recibo cadsinc', 'Identificação solicitação']].to_markdown(index=False, numalign="left", stralign="left"))

    # Página "Eventos"
    st.title('Eventos')
    st.write(df_evento.to_markdown(index=False, numalign="left", stralign="left"))

    # Página "Atualizar Dados" - (Implementação não incluída neste exemplo)
    st.title('Atualizar Dados')
    st.write("Funcionalidade de atualização de dados não implementada neste exemplo.")


