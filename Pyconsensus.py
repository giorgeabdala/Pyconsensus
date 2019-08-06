# requisitos: panda, xlrd,
import pandas as pd
import subprocess

# caminho do arquivo blomberg
BLOOMBERG_ARQ = 'consenso.xlsx'
ELEVEN_ARQ = 'eleven.pdf'


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
        "java -jar ./tabula-1.0.3-jar-with-dependencies.jar -p 2 -a 82.923,35.0,738.122,560.052 -o saida.csv eleven.pdf",
        shell=True)
    df = pd.read_csv("saida.csv", sep=",", encoding='cp1252')
    # delete as colunas inuteis
    df = df.drop(df.columns[[0, 1, 3, 5, 8, 12]], axis=1)
    # deleta primeira linha
    df = df.drop([0, 1, 2, 3, 4])
    df.columns = COLUMN_NAME
    # deleta linhas onde todos os valores são NaN
    df = df.dropna(how='all')

    return df


bloomberg = parse_bloomberg(BLOOMBERG_ARQ)
bloom_date = bloomberg[0]
bloom_df = bloomberg[1]

eleven_df = parse_eleven(ELEVEN_ARQ)

ticker1 = 'CIEL3'
ticker2 = 'BBDC4'
space = "     "

ativo1_bloom = bloom_df[bloom_df['ticker'] == ticker1]
ativo1_elev = eleven_df[eleven_df['ticker'] == ticker1]

ativo2_bloom = bloom_df[bloom_df['ticker'] == ticker2]
ativo2_elev = eleven_df[eleven_df['ticker'] == ticker2]

print('ticker', space, 'target EL', space, 'target Bloomberg', space, 'Outras')
print(ticker1, space, ativo1_elev['target'].values[0], space, ativo1_bloom['target'].values[0], space)

print (ativo1_bloom)

https://pt.stackoverflow.com/questions/308346/como-imprimir-as-informa%C3%A7%C3%B5es-no-formato-de-tabela-em-python