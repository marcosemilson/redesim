import pandas as pd
import sys

# ... (Funções de processamento para os registros 01 a 10) ...

# Dicionário de mapeamento de tipos de registro para funções de processamento
record_processors = {
    '0A': processar_registro_01,
    '0B': processar_registro_02,
    '01': processar_registro_03,
    '02': processar_registro_04,
    '03': processar_registro_03,
    '04': processar_registro_04,
    '06': processar_registro_06,
    '07': processar_registro_07,
    '08': processar_registro_08,
    '09': processar_registro_09,
    '10': processar_registro_10,
    '11': processar_registro_11,
    '12': processar_registro_12,
    '13': processar_registro_13,
    '14': processar_registro_14,
    '15': processar_registro_15,
    '16': processar_registro_16,
    '17': processar_registro_17,
    '18': processar_registro_18,
    '19': processar_registro_19,
    '20': processar_registro_20,
    '25': processar_registro_25,
    '35': processar_registro_35,
    '40': processar_registro_40,
    '99': processar_registro_99
}

# Função para ler e processar o arquivo DAMEF (modificada para receber o nome do arquivo)
def processar_arquivo_damef(nome_arquivo):
    dados = []
    with open(nome_arquivo, 'r') as arquivo:
        arquivo_texto = arquivo.read().decode("utf-8").splitlines()
        for linha in arquivo_texto:
            tipo_registro = linha[0:2]
            processador = record_processors.get(tipo_registro)
            if processador:
                registro = processador(linha)
                registro["Tipo de Registro"] = tipo_registro  # Adicionar o tipo de registro
                dados.append(registro)
            else:
                print(f"Tipo de registro não reconhecido: {tipo_registro}")  # Imprimir aviso em vez de usar st.warning

    df = pd.DataFrame(dados)
    return df

# Interface de texto (modificada para receber o nome do arquivo como argumento)
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <caminho_do_arquivo_damef>")
        sys.exit(1)
    
    nome_arquivo = sys.argv[1]

    # Processar o arquivo
    df = processar_arquivo_damef(nome_arquivo)

    # Exibir o DataFrame
    print(df)

    # Perguntar ao usuário quais tipos de registro filtrar
    tipos_filtro = input("Digite os tipos de registro para filtrar (separados por vírgula, ou pressione Enter para mostrar todos): ")
    tipos_filtro = [tipo.strip() for tipo in tipos_filtro.split(",")] if tipos_filtro else df["Tipo de Registro"].unique()

    # Filtrar o DataFrame
    df_filtrado = df[df["Tipo de Registro"].isin(tipos_filtro)]

    # Exibir o DataFrame filtrado
    print(df_filtrado)

    # Perguntar se o usuário deseja exportar para CSV
    exportar_csv = input("Deseja exportar os dados filtrados para CSV? (s/n): ")
    if exportar_csv.lower() == 's':
        df_filtrado.to_csv("dados_damef_filtrados.csv", index=False)
        print("Arquivo CSV exportado com sucesso!")