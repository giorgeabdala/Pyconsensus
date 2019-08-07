# requisitos: panda, xlrd,
import pandas as pd
import subprocess

# caminho do arquivo blomberg
BLOOMBERG_ARQ = 'consenso.xlsx'
ELEVEN_ARQ = 'eleven.pdf'

#cabeçalho ta tabela de resultados
HEADER = ['TICKER ', 'ELEVEN ', 'BLOOMBERG ', 'OUTRAS']


# retorna a data do consenso e um dataFrame com os dados tratados da Eleven.
# recebe o caminho do arquivo excel
def parse_bloomberg(excel_file):
    # define nome das colunas do DF final
    COLUMN_NAME = ['ticker', 'target', 'consenso', 'qtdInst', 'qtdCompra', 'qtdNeutro', 'qtdVenda']
    # carrega o arquivo excel pulando as primeiras 9 linhas
    df = pd.read_excel(excel_file)
    # pega a data do arquivo
    date = df.iloc[4, 1]
    # deleta as 9 priemiras linhas
    df = df.drop(df.index[0:9])
    # deleta as colunas 0,2 e 5 (Unamed, Empresa, preço e Upside/Downside)
    df = df.drop(df.columns[[0, 2, 3, 5]], axis=1)
    # renomeado colunas
    df.columns = COLUMN_NAME
    # faz um replace na coluna ticker e retira o ' BS'
    df['ticker'] = df['ticker'].str.replace(' BS', '')

    result = [date, df]
    return result

def parse_eleven(pdf_file):
    # nome das colunas do df final
    COLUMN_NAME = ["ticker", "target", "precoLimite", "recomendacao", "risco", "qualidade", "indice"]
    # chamada ao tabula-java
    subprocess.call(
        "java -jar ./tabula-1.0.3-jar-with-dependencies.jar -p 2 -a 82.923,35.0,738.122,560.052 -o saidaP2.csv eleven.pdf",
        shell=True)
    subprocess.call(
        "java -jar ./tabula-1.0.3-jar-with-dependencies.jar -p 3 -a 70.28,35.0,764.895,560.052 -o saidaP3.csv eleven.pdf",
        shell=True)
    subprocess.call(
        "java -jar ./tabula-1.0.3-jar-with-dependencies.jar -p 4 -a 70.28,35.0,764.895,560.052 -o saidaP4.csv eleven.pdf",
        shell=True)

    # lê pagina 2
    dfP2 = pd.read_csv("saidaP2.csv", sep=",", encoding='cp1252')
    # lê pagina 3
    dfP3 = pd.read_csv("saidaP3.csv", sep=",", encoding='cp1252')
    # lê pagina 4
    dfP4 = pd.read_csv("saidaP4.csv", sep=",", encoding='cp1252')

    # deleta as primeira linha das paginas
    dfP2 = dfP2.drop([0, 1, 2, 3, 4])
    dfP3 = dfP3.drop([0, 1, 2])
    dfP4 = dfP4.drop([0, 1, 2])

    # delete as colunas inuteis
    dfP2 = dfP2.drop(dfP2.columns[[0, 1, 3, 5, 8, 12]], axis=1)
    dfP3 = dfP3.drop(dfP3.columns[[0, 2, 4, 6, 8, 12]], axis=1)
    dfP4 = dfP4.drop(dfP4.columns[[0, 2, 4, 6, 8, 12]], axis=1)

    # renomeando as counas
    dfP2.columns = COLUMN_NAME
    dfP3.columns = COLUMN_NAME
    dfP4.columns = COLUMN_NAME

    # unindo os 3 dataFrame em um
    df = pd.concat([dfP2, dfP3, dfP4])

    # deleta linhas onde todos os valores são NaN
    df = df.dropna(how='all')

    return df

def print_table(ativo1_bloom, ativo2_bloom, ativo1_elev, ativo2_elev):
    #monta string das outras instituições
    outras1 = str(ativo1_bloom['qtdCompra'].values[0]) + '/' + str(ativo1_bloom['qtdNeutro'].values[0]) + '/'+ str(ativo1_bloom['qtdVenda'].values[0])
    outras2 = str(ativo2_bloom['qtdCompra'].values[0]) + '/' + str(ativo2_bloom['qtdNeutro'].values[0]) + '/'+ str(ativo2_bloom['qtdVenda'].values[0])

    linha1 = [ticker1, ativo1_elev['target'].values[0], ativo1_bloom['target'].values[0], outras1]
    linha2 = [ticker2, ativo2_elev['target'].values[0], ativo2_bloom['target'].values[0], outras2]

    #format e imprime o cabeçalho
    print('{:<16} {:<16} {:<19} {:<20}'.format(*HEADER))
    #imprime linha com 60 '-'
    print('-'*60)
    print('{:<16} {:<16} {:<19.2f} {:<20}'.format(*linha1))
    print('{:<16} {:<16} {:<19.2f} {:<20}'.format(*linha2))


bloomberg = parse_bloomberg(BLOOMBERG_ARQ)
bloom_date = bloomberg[0]
bloom_df = bloomberg[1]

eleven_df = parse_eleven(ELEVEN_ARQ)

ticker1 = input("Digite o ticker 1:")
ticker2 = input("Digite o ticker 2:")

bloom1 = bloom_df[bloom_df['ticker'] == ticker1]
bloom2 = bloom_df[bloom_df['ticker'] == ticker2]

elev1 = eleven_df[eleven_df['ticker'] == ticker1]
elev2 = eleven_df[eleven_df['ticker'] == ticker2]

print_table(bloom1, bloom2, elev1, elev2)