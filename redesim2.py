import streamlit as st
import pandas as pd
import openpyxl 
import os

# 1. Verificar a existência dos arquivos CSV
csv_files = ['Relatóriodedadosdeatividades.csv', 'Relatóriodedadosdeempresas.csv', 'Relatóriodedadosdesócios.csv']
for file in csv_files:
    if not os.path.exists(file):
        st.error(f"Arquivo {file} não encontrado. Certifique-se de que os arquivos CSV estejam na mesma pasta que este script.")
        st.stop()

# 2. Carregar os arquivos CSV em DataFrames
df_atividades = pd.read_csv('Relatóriodedadosdeatividades.csv', delimiter=';')
df_empresas = pd.read_csv('Relatóriodedadosdeempresas.csv', delimiter=';')
df_socios = pd.read_csv('Relatóriodedadosdesócios.csv', delimiter=';')

# 3. Renomear colunas para consistência
df_atividades = df_atividades.rename(columns={'Identificador único empresa': 'id_empresa'})
df_socios = df_socios.rename(columns={'Identificador único empresa': 'id_empresa'})
df_empresas = df_empresas.rename(columns={'Identificador único': 'id_empresa'})

# 4. Nome do arquivo Excel único
excel_filename = "dados_empresas_exportadas.xlsx"

# 5. Aplicativo Streamlit
st.title('Detalhes de Empresas')

# 6. Lista de empresas para seleção
empresas_disponiveis = df_empresas['razao_social'].unique()
selected_empresa = st.selectbox('Selecione uma empresa:', empresas_disponiveis)

# 7. Exibir detalhes da empresa selecionada
if selected_empresa:
    id_empresa = df_empresas[df_empresas['razao_social'] == selected_empresa]['id_empresa'].values[0]

    detalhes_empresa = df_empresas[df_empresas['id_empresa'] == id_empresa]
    atividades_empresa = df_atividades[df_atividades['id_empresa'] == id_empresa]
    socios_empresa = df_socios[df_socios['id_empresa'] == id_empresa]

    st.subheader('Detalhes da Empresa')
    st.write(detalhes_empresa)

    st.subheader('Atividades da Empresa')
    st.write(atividades_empresa)

    st.subheader('Sócios da Empresa')
    st.write(socios_empresa)

    # 8. Botão para exportar para o Excel único e excluir dos CSVs
    if st.button("Exportar para Excel e Remover"):
        export_success = False
        try:
            # 1. Carregar dados existentes do Excel (se houver)
            if os.path.exists(excel_filename):
                df_empresas_exportadas = pd.read_excel(excel_filename, sheet_name=None)
            else:
                df_empresas_exportadas = {}

            # 2. Adicionar os novos dados ao dicionário
            df_empresas_exportadas['Empresa'] = pd.concat([df_empresas_exportadas.get('Empresa', pd.DataFrame()), detalhes_empresa], ignore_index=True)
            df_empresas_exportadas['Atividades'] = pd.concat([df_empresas_exportadas.get('Atividades', pd.DataFrame()), atividades_empresa], ignore_index=True)
            df_empresas_exportadas['Sócios'] = pd.concat([df_empresas_exportadas.get('Sócios', pd.DataFrame()), socios_empresa], ignore_index=True)

            # 3. Salvar todos os dados no Excel
            with pd.ExcelWriter(excel_filename) as writer:
                for sheet_name, df in df_empresas_exportadas.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            export_success = True
            st.success(f"Dados da empresa {id_empresa} exportados para {excel_filename} e removidos com sucesso!")
        except (PermissionError, Exception) as e:
            st.error(f"Erro ao exportar para Excel: {e}")

        # Remover a empresa dos DataFrames e salvar os CSVs APENAS se a exportação for bem-sucedida
        if export_success:
            df_empresas = df_empresas[df_empresas['id_empresa'] != id_empresa]
            df_atividades = df_atividades[df_atividades['id_empresa'] != id_empresa]
            df_socios = df_socios[df_socios['id_empresa'] != id_empresa]

            df_empresas.to_csv('Relatóriodedadosdeempresas.csv', sep=';', index=False)
            df_atividades.to_csv('Relatóriodedadosdeatividades.csv', sep=';', index=False)
            df_socios.to_csv('Relatóriodedadosdesócios.csv', sep=';', index=False)

            st.experimental_rerun()  # Recarrega o aplicativo para atualizar a lista de empresas