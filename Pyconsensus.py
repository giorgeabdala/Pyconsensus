# requisitos: panda, xlrd,
#pd.set_option('display.max_columns', 15)
import pandas as pd
import subprocess


# caminho do arquivo blomberg
BLOOMBERG_ARQ = 'consenso.xlsx'
ELEVEN_ARQ = 'eleven.pdf'

#cabeçalho da tabela de resultados
HEADER = ['TICKER ', 'ELEVEN ', 'BLOOMBERG ', 'OUTRAS']

# nome das colunas do df final eleven
COLUMN_NAME_ELEVEN = ['ticker', 'atual', 'target', 'precoLimite', 'recomendacao', 'risco', 'qualidade', 'indice', 'upside']
COLUMN_NAME_BLOOMBERG = ['ticker', 'target', 'consenso', 'qtdInst', 'qtdCompra', 'qtdNeutro', 'qtdVenda']

#cordenada data arquivo eleven
cord_date = '108.208,47.969,134.238,117.876'

cord_page2 = '103.999,35.0,751.018,563.771' 
cord_page3 = '43.001,27.0,801.575,567.67'
cord_page4 = '43.001,27.0,801.575,567.67'



# retorna a data do consenso e um dataFrame com os dados tratados da Eleven.
# recebe o caminho do arquivo excel
def parse_bloomberg(excel_file):
    # carrega o arquivo excel pulando as primeiras 9 linhas
    df = pd.read_excel(excel_file)
    # pega a data do arquivo
    date = df.iloc[4, 1]
    # deleta as 9 priemiras linhas
    df = df.drop(df.index[0:9])
    # deleta as colunas 0,2 e 5 (Unamed, Empresa, preço e Upside/Downside)
    df = df.drop(df.columns[[0, 2, 3, 5]], axis=1)
    # renomeado colunas
    df.columns = COLUMN_NAME_BLOOMBERG
    # faz um replace na coluna ticker e retira o ' BS'
    df['ticker'] = df['ticker'].str.replace(' BS', '')

    result = [date, df]
    return result


def read_page_eleven(pdf_file, page, cordenadas):
	# chamada ao tabula-java
	subprocess.call(
            "java -jar ./tabula-1.0.3-jar-with-dependencies.jar -p " + page + " -a " + cordenadas + " -o saida.csv eleven.pdf", shell=True)
        #Lê página do csv de saída
	df = pd.read_csv("saida.csv", sep=",", encoding='cp1252')

	# deleta linhas onde todos os valores são NaN
	df = df.dropna(how='all')

	#mantem apenas colunas com ao menos a metade(df.shape[0]/2) de linhas não-nan
	df = df.dropna(thresh=df.shape[0]/2, axis=1)

        #Deleta linhas onde a segunda coluna é nan
	df = df.dropna(subset=[df.columns[1]])

        #deleta coluna companhia
	df = df.drop(df.columns[0], axis=1)


	df.columns = COLUMN_NAME_ELEVEN
	
	return df

def parse_eleven(pdf_file):

    dfP2 = read_page_eleven(ELEVEN_ARQ, "2", cord_page2)
    dfP3 = read_page_eleven(ELEVEN_ARQ, "3", cord_page2)
    dfP4 = read_page_eleven(ELEVEN_ARQ, "4", cord_page2)

    # unindo os 3 dataFrame em um
    df = pd.concat([dfP2, dfP3, dfP4])
    
    return df

def print_table(ativo1_bloom, ativo2_bloom, ativo1_elev, ativo2_elev, ticker1, ticker2):
    
    #monta string das outras instituições
    outras1 = str(ativo1_bloom['qtdCompra'].values[0]) + '/' + str(ativo1_bloom['qtdNeutro'].values[0]) + '/'+ str(ativo1_bloom['qtdVenda'].values[0])
    outras2 = str(ativo2_bloom['qtdCompra'].values[0]) + '/' + str(ativo2_bloom['qtdNeutro'].values[0]) + '/'+ str(ativo2_bloom['qtdVenda'].values[0])

    linha1 = [ticker1, ativo1_elev['target'].values[0], ativo1_bloom['target'].values[0], outras1]
    linha2 = [ticker2, ativo2_elev['target'].values[0], ativo2_bloom['target'].values[0], outras2]
	
    print_header()
    print_linha(linha1)
    print_linha(linha2)

	

def print_header():
	#formata e imprime o cabeçalho
    print('{:<16} {:<16} {:<19} {:<20}'.format(*HEADER))
    #imprime linha com 60 '-'
    print('-'*60)

def print_linha(linha):
        print('{:<16} {:<16} {:<19.2f} {:<20}'.format(*linha))
	

def process_ticker(bloom_df, eleven_df):
    
   # try:
        ticker1 = input("Digite o ticker 1:")
        ticker2 = input("Digite o ticker 2:")

        #maiúcuslo
        ticker1 = ticker1.upper()
        ticker2 = ticker2.upper()

        bloom1 = busca_ticker(ticker1, bloom_df)
        bloom2 = busca_ticker(ticker2, bloom_df)

        elev1 = busca_ticker(ticker1, eleven_df)
        elev2 = busca_ticker(ticker2, eleven_df)

        print_table(bloom1, bloom2, elev1, elev2, ticker1, ticker2)
        process_ticker(bloom_df, eleven_df)

    #except:
            #print ("Não foi possível encontrar os ticker solicitado. Por favor, tente novamente");
   #         process_ticker(bloom_df, eleven_df)

def busca_ticker(ticker, df):
        df = df[df['ticker'] == ticker]

	#Adicona uma linha vazia caso a busca não encontre o ticker
        if df.shape[0] == 0:
                df = df.append({} , ignore_index=True)
        return df

def start():
        bloomberg = parse_bloomberg(BLOOMBERG_ARQ)
        bloom_date = bloomberg[0]
        bloom_df = bloomberg[1]
        eleven_df = parse_eleven(ELEVEN_ARQ)
        process_ticker(bloom_df, eleven_df)
     
        
start()

#df = parse_eleven(ELEVEN_ARQ)

#df = read_page_eleven(ELEVEN_ARQ, "3", cord_page3)




    

    
        
    











