# requisitos: panda, xlrd,
#pd.set_option('display.max_columns', 15)
import pandas as pd
import subprocess

#Recomendação XP
#https://researchxp1.s3-sa-east-1.amazonaws.com/Guia+de+recomenda%C3%A7%C3%B5es+-+A%C3%A7oes+-+Research+XP+-+30.08.2019.xlsx


# caminho do arquivo blomberg
BLOOMBERG_ARQ = 'consenso.xlsx'
ELEVEN_ARQ = 'eleven.pdf'
RESULTADO_ELEV_ARQ = 'resultadosEleven.pdf'
XP_ARQ = 'xp.xlsx'

#cabeçalho da tabela de resultados
HEADER = ['TICKER ', 'ELEVEN ', 'UPSIDE', 'BLOOMBERG ', 'UPSIDE', 'XP', 'UPSIDE', 'OUTRAS C/N/V']

# nome das colunas do df final eleven
COLUMN_NAME_ELEVEN = ['ticker', 'atual', 'target', 'precoLimite', 'recomendacao', 'risco', 'qualidade', 'indice', 'upsideBack']
COLUMN_NAME_BLOOMBERG = ['ticker', 'target', 'consenso', 'qtdInst', 'qtdCompra', 'qtdNeutro', 'qtdVenda']
COLUMN_NAME_XP = ['ticker', 'consenso', 'target']
COLUMN_NAME_RESULTADO_ELEVEN = ['ticker', 'resultado', 'teleconferencia']

#cordenada data arquivo eleven
cord_date = '108.208,47.969,134.238,117.876'

cord_page1 = '105.977,35.326,131.263,132.007'
cord_page2 = '103.999,35.0,751.018,563.771' 
#cord_page3 = '43.001,27.0,801.575,567.67'
#cord_page4 = '43.001,27.0,801.575,567.67'


#cordenada resultados eleven
cord_result1 = '196.0,40.0,706.178,426.724'
cord_result_other = '56.149,104.49,697.219,491.958'


def parse_xp(excel_file):
    #carrega arquivo XP excel
    df = pd.read_excel(excel_file)
    #deleta as 3 primeiras linhas
    df = df.drop(df.index[0:3])
    #deleta as colunas inuteis
    df = df.drop(df.columns[[0,2,3,4,6,8,9,10,11,12,13,14,15,16]], axis=1)
    #rename nas colunas do data frame
    df.columns = COLUMN_NAME_XP

    return df


# retorna a data do consenso e um dataFrame com os dados tratados da Eleven.
# recebe o caminho do arquivo excel
def parse_bloomberg(excel_file):
    # carrega o arquivo excel 
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
            "java -jar ./tabula-1.0.3-jar-with-dependencies.jar -p " + page + " -a " + cordenadas + " -o saida.csv " + ELEVEN_ARQ, shell=True)
    #Lê página do csv de saída
    df = pd.read_csv("saida.csv", sep=",", encoding='cp1252')

    if page == '1':
        return df

    # deleta linhas onde todos os valores são NaN
    df = df.dropna(how='all')

    #mantem apenas colunas com ao menos a metade(df.shape[0]/2) de linhas não-nan
    df = df.dropna(thresh=df.shape[0]/2, axis=1)

    #Deleta linhas onde a segunda coluna é nan
    df = df.dropna(subset=[df.columns[1]])

    #deleta coluna companhia
    df = df.drop(df.columns[0], axis=1)

    df.columns = COLUMN_NAME_ELEVEN

    # faz um replace na coluna target e retira o R$
    df['target'] = df['target'].apply(lambda x: str(x.replace('R$ ', '')))
    df['target'] = df['target'].apply(lambda x: str(x.replace(',', '.')))
	
    return df

def parse_eleven(pdf_file):

    #pega a data
    date = read_page_eleven(ELEVEN_ARQ, "1", cord_page1).columns[0]
    
    dfP2 = read_page_eleven(ELEVEN_ARQ, "2", cord_page2)
    dfP3 = read_page_eleven(ELEVEN_ARQ, "3", cord_page2)
    dfP4 = read_page_eleven(ELEVEN_ARQ, "4", cord_page2)

    # unindo os 3 dataFrame em um
    df = pd.concat([dfP2, dfP3, dfP4])

    result = [date, df]
    return result

def read_page_result_eleven(pdf_file, page, cord):
     # chamada ao tabula-java
    subprocess.call(
            "java -jar ./tabula-1.0.3-jar-with-dependencies.jar -p " + page + " -a " + cord + " -o saida.csv " + RESULTADO_ELEV_ARQ, shell=True)
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

    df.columns = COLUMN_NAME_RESULTADO_ELEVEN

    return df

def parse_result_eleven(pdf_file):
     dfP1 = read_page_result_eleven(pdf_file, "1", cord_result1)
     
     dfP2 = read_page_result_eleven(pdf_file, "2", cord_result_other)
     dfP3 = read_page_result_eleven(pdf_file, "3", cord_result_other)
     dfP4 = read_page_result_eleven(pdf_file, "4", cord_result_other)
     dfP5 = read_page_result_eleven(pdf_file, "5", cord_result_other)

     result = pd.concat([dfP1, dfP2, dfP3, dfP4, dfP5])

     return result




    

def print_table(ativo1_bloom, ativo2_bloom, ativo1_elev, ativo2_elev, ativo1_xp, ativo2_xp, ticker1, ticker2, resultado1, resultado2):
    
    #monta string das outras instituições
    outras1 = str(ativo1_bloom['qtdCompra'].values[0]) + '/' + str(ativo1_bloom['qtdNeutro'].values[0]) + '/'+ str(ativo1_bloom['qtdVenda'].values[0])
    outras2 = str(ativo2_bloom['qtdCompra'].values[0]) + '/' + str(ativo2_bloom['qtdNeutro'].values[0]) + '/'+ str(ativo2_bloom['qtdVenda'].values[0])

    linha1 = [ticker1]
    linha2 = [ticker2]
    
    linha1.append(ativo1_elev['target'].values[0])
    linha1.append(ativo1_elev['upside'].values[0])
    linha1.append(ativo1_bloom['target'].values[0])
    linha1.append(ativo1_bloom['upside'].values[0])
    linha1.append(ativo1_xp['target'].values[0])
    linha1.append(ativo1_xp['upside'].values[0])
    linha1.append(outras1)
    linha1.append(resultado1)

    linha2.append(ativo2_elev['target'].values[0])
    linha2.append(ativo2_elev['upside'].values[0])
    linha2.append(ativo2_bloom['target'].values[0])
    linha2.append(ativo2_bloom['upside'].values[0])
    linha2.append(ativo2_xp['target'].values[0])
    linha2.append(ativo2_xp['upside'].values[0])
    linha2.append(outras2)
    linha2.append(resultado2)
	
    print_header()
    print_linha(linha1)
    print_linha(linha2)

	

def print_header():
	#formata e imprime o cabeçalho
    print('{:<16} {:<16} {:<16} {:<19} {:<16} {:<16} {:<16} {:<20}'.format(*HEADER))
    #imprime linha com 60 '-'
    print('-'*135)

def print_linha(linha):
        print('{:<16} {:<16} {:<16.2f} {:<19.2f} {:<16.2f} {:<16} {:<16.2f} {:<20} {:<100}'.format(*linha))
        print('\n')
	

def process_ticker(bloom_df, eleven_df, xp_df, resultado_df):
    
  #  try:
        ticker1 = input("Digite o ticker 1:")
        preco1 = input("Digite o preço atual:")
        print("\n")
        ticker2 = input("Digite o ticker 2:")
        preco2 = input("Digite o preço atual:")
        print("\n")


        resultado1 = busca_ticker(ticker2, resultado_df)
        resultado2 = busca_ticker(ticker2, resultado_df)

        bloom1 = busca_ticker(ticker1, bloom_df)
        bloom2 = busca_ticker(ticker2, bloom_df)      

        elev1 = busca_ticker(ticker1, eleven_df)
        elev2 = busca_ticker(ticker2, eleven_df)

        xp1 = busca_ticker(ticker1, xp_df)
        xp2 = busca_ticker(ticker2, xp_df)

        #add coluna com o upside atualizado
        bloom1 = add_upside_col(bloom1, preco1)
        bloom2 = add_upside_col(bloom2, preco2)

        elev1 = add_upside_col(elev1, preco1)
        elev2 = add_upside_col(elev2, preco2)

        xp1 = add_upside_col(xp1, preco1)
        xp2 = add_upside_col(xp2, preco2)

        print_table(bloom1, bloom2, elev1, elev2, xp1, xp2, ticker1, ticker2, resultado1, resultado2)
        process_ticker(bloom_df, eleven_df, xp_df, resultado_df)

  #  except:
        print ("Não foi possível encontrar os ticker solicitado. Por favor, tente novamente");
        process_ticker(bloom_df, eleven_df, xp_df, resultado_df)

def add_upside_col(df, preco):
    df.loc[df.index[0], 'upside'] = calcula_upside(preco, df.loc[df.index[0],'target'])
    return df
    

def busca_ticker(ticker, df):
        #maiúcuslo
        ticker = ticker.upper()
        df = df[df['ticker'] == ticker]

	#Adicona uma linha vazia caso a busca não encontre o ticker
        if df.shape[0] == 0:
                df = df.append({} , ignore_index=True)
        return df


#calcula o upside. Recebe preço atual e target
def calcula_upside(atual, target):
    if target == 'Sob Revisão':
        return 0
    
    atual = str(atual)
    target = str(target)
    
    atual = float(atual.replace(',', '.'))
    target = float(target.replace(',', '.'))

    upside = (target/atual) - 1 
        
    return upside * 100
    

def start():
        bloomberg = parse_bloomberg(BLOOMBERG_ARQ)
        bloom_date = bloomberg[0]
        bloom_df = bloomberg[1]
        
        eleven = parse_eleven(ELEVEN_ARQ)
        eleven_date = eleven[0]
        eleven_df = eleven[1]

        xp_df = parse_xp(XP_ARQ)

        resultado_df = parse_result_eleven(RESULTADO_ELEV_ARQ)    

        print('Data Bloomberg: ' + str(bloom_date))
        print('\n')
        print('Data Eleven: ' + str(eleven_date))
        print('\n')  
        
        process_ticker(bloom_df, eleven_df, xp_df, resultado_df)    
        
start()

#df = read_page_eleven(ELEVEN_ARQ, "1", cord_page1)

    











