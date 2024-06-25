import streamlit as st
import pandas as pd
import hashlib
import os

# Constantes para os nomes dos arquivos CSV (sem extensão)
CSV_ATIVIDADES = 'Relatóriodedadosdeatividades'
CSV_EMPRESAS = 'Relatóriodedadosdeempresas'
CSV_SOCIOS = 'Relatóriodedadosdesócios'

# Lista de arquivos CSV (com extensão)
CSV_FILES = [f"{file}.csv" for file in [CSV_ATIVIDADES, CSV_EMPRESAS, CSV_SOCIOS]]

# Dicionário com os tipos de dados para cada coluna (usando os nomes dos arquivos sem extensão)
DTYPES = {
    CSV_ATIVIDADES: {
        'Identificador único empresa': str, 'codigocnae': str, 'codigo_municipio': str, 'codigoclase': int
    },
    CSV_EMPRESAS: {
        'Identificador único': str, 'cnpj': str, 'cep': str, 'telefone1': str, 'telefone2': str,
        'inscricao_municipal': str, 'inscricao_estadual': str, 'inscricao_imobiliaria': str,
        'codigocnae_fiscal': str, 'codigonatureza_juridica': str, 'codigo_municipio': str,
        'capital_social': float, 'porte': str, 'opcao_pelo_simples': str, 'opcao_pelo_mei': str,
        'situacao_cadastral': str, 'data_situacao_cadastral': str, 'motivo_situacao_cadastral': str,
        'nome_fantasia': str, 'tipo_logradouro': str, 'logradouro': str, 'numero': str, 'complemento': str,
        'bairro': str, 'uf': str, 'email': str, 'situacao_especial': str, 'data_situacao_especial': str
    },
    CSV_SOCIOS: {
        'Identificador único empresa': str, 'cpfcnpj': str, 'qualificacao': str, 'faixa_etaria': str,
        'codigo_municipio': str
    }
}

EXCEL_FILENAME = "empresas_exportadas.xlsx"

# Função para gerar um hash para os DataFrames
def hash_dfs(dfs):
    hash_values = []
    for df in dfs.values():
        hash_values.append(hashlib.sha256(pd.util.hash_pandas_object(df).values).hexdigest())
    return hash("".join(hash_values))

# Função para carregar e preparar os dados (com st.cache_resource)
@st.cache_resource(hash_funcs={dict: hash_dfs})
def load_data(csv_files, dfs=None):
    if dfs is None:  # Carrega os dados pela primeira vez
        for file in csv_files:
            if not os.path.exists(file):
                st.error(f"Arquivo {file} não encontrado. Certifique-se de que os arquivos CSV estejam na mesma pasta que este script.")
                st.stop()

        dfs = {}
        for csv_file in csv_files:
            file_name_without_ext = os.path.splitext(csv_file)[0]
            df = pd.read_csv(csv_file, delimiter=';', dtype=DTYPES[file_name_without_ext])
            df = df.rename(columns={'Identificador único empresa' if file_name_without_ext != CSV_EMPRESAS else 'Identificador único': 'id_empresa'})
            df['id_empresa'] = pd.to_numeric(df['id_empresa'], errors='coerce').astype(pd.Int64Dtype())
            dfs[file_name_without_ext] = df
    return dfs

# Carregar os dados
dfs = load_data(CSV_FILES)

# Aplicativo Streamlit
st.title('Detalhes de Empresas')

# Lista de empresas para seleção
empresas_disponiveis = dfs[CSV_EMPRESAS]['razao_social'].unique()
selected_empresa = st.selectbox('Selecione uma empresa:', empresas_disponiveis)

if selected_empresa:
    id_empresa = dfs[CSV_EMPRESAS][dfs[CSV_EMPRESAS]['razao_social'] == selected_empresa]['id_empresa'].values[0]

    # Input para a situação da empresa
    situacao_empresa = st.text_input("Digite a situação da empresa:", key=f"situacao_{id_empresa}")

    # Detalhes da Empresa
    detalhes_empresa = dfs[CSV_EMPRESAS][dfs[CSV_EMPRESAS]['id_empresa'] == id_empresa].copy()

    # Adicionar a situação da empresa ao DataFrame detalhes_empresa
    if 'Situação' not in detalhes_empresa.columns:
        detalhes_empresa.insert(0, 'Situação', situacao_empresa)
    else:
        detalhes_empresa['Situação'] = situacao_empresa

    st.subheader('Detalhes da Empresa')
    st.dataframe(detalhes_empresa.style.format({'id_empresa': '{:.0f}', 'capital_social': '{:.2f}', 'cep': '{}', 'Situação': '{}'}))

    # Atividades da Empresa
    atividades_empresa = dfs[CSV_ATIVIDADES][dfs[CSV_ATIVIDADES]['id_empresa'] == id_empresa]
    if not atividades_empresa.empty:
        st.subheader('Atividades da Empresa')
        st.dataframe(atividades_empresa.style.format({'id_empresa': '{:.0f}', 'codigoclase': '{:.0f}'}))

    # Sócios da Empresa
    socios_empresa = dfs[CSV_SOCIOS][dfs[CSV_SOCIOS]['id_empresa'] == id_empresa]
    if not socios_empresa.empty:
        st.subheader('Sócios')
        st.dataframe(socios_empresa.style.format({'id_empresa': '{:.0f}'}))

    # Botão para exportar para o Excel e remover dos CSVs
    if st.button("Exportar para Excel e Remover"):
        if situacao_empresa:
            try:
                 # Carregar dados existentes do Excel (se houver)
                if os.path.exists(EXCEL_FILENAME):
                    existing_data = pd.read_excel(EXCEL_FILENAME, sheet_name=None)
                else:
                    existing_data = {}

                # Criar o dicionário df_empresas_exportadas
                df_empresas_exportadas = {
                    CSV_EMPRESAS: detalhes_empresa,
                    CSV_ATIVIDADES: atividades_empresa,
                    CSV_SOCIOS: socios_empresa
                }

                # Concatenar os novos dados com os existentes
                for sheet_name, df in df_empresas_exportadas.items():
                    if sheet_name in existing_data:
                        existing_data[sheet_name] = pd.concat([existing_data[sheet_name], df], ignore_index=True)
                    else:
                        existing_data[sheet_name] = df

                # Exportar para Excel com caminho completo
                excel_path = os.path.join(os.getcwd(), EXCEL_FILENAME)
                with pd.ExcelWriter(excel_path) as writer:
                    for sheet_name, df in existing_data.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                st.success(f"Dados da empresa {id_empresa} exportados para {EXCEL_FILENAME} e removidos com sucesso!")

                # Remover a empresa dos DataFrames
                for nome_df, df in dfs.items():
                    dfs[nome_df] = df[df['id_empresa'] != id_empresa]

                # Salvar os CSVs atualizados e recarregar os dados
                for csv_file, df in dfs.items():
                    df.to_csv(f"{csv_file}.csv", sep=';', index=False)

                # Recarregar os dados (isso invalidará o cache devido à mudança nos DataFrames)
                dfs = load_data(CSV_FILES, dfs)  # Passa os DataFrames modificados como argumento
                st.experimental_rerun()

            except (PermissionError, Exception) as e:
                st.error(f"Erro ao exportar para Excel: {e}")
        else:
            st.warning("Por favor, digite a situação da empresa antes de exportar.")