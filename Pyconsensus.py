# requisitos: panda, xlrd, requests
#pd.set_option('display.max_columns', 15)
import pandas as pd
import subprocess
import requests 

# caminho do arquivo blomberg
ELEVEN_ARQ = 'eleven.pdf'

XP_ARQ = 'xp.xlsx'
XP_URL = "https://researchxp1.s3-sa-east-1.amazonaws.com/Guia+de+recomenda%C3%A7%C3%B5es+-+A%C3%A7oes+-+Research+XP+-+30.08.2019.xlsx"

NECTON_ARQ = "necton.xlsx"
NECTON_URL = "https://apibackoffice.necton.com.br/api/archive/24a55bad-13d2-4686-bbbc-daaa57c7aca9"

#cabeçalho da tabela de resultados
HEADER = ['TICKER ', 'ELEVEN ', 'UPSIDE', 'BLOOMBERG ', 'UPSIDE', 'XP', 'UPSIDE']

# nome das colunas do df final eleven
COLUMN_NAME_ELEVEN = ['ticker', 'atual', 'target', 'precoLimite', 'recomendacao', 'risco', 'qualidade', 'indice', 'upsideBack']
COLUMN_NAME_BLOOMBERG = ['ticker', 'target', 'consenso', 'qtdInst', 'qtdCompra', 'qtdNeutro', 'qtdVenda']
#COLUMN_NAME_XP = ['ticker', 'consenso', 'target']
COLUMN_NAME_XP = ['ticker', 'target']
COLUMN_NAME_NECTON = ['equity', 'nome', 'setor', 'ticker', 'atual', '∆% 2020', '∆% 12 meses', 'target', 'upside', 'qtdAcoes', 'freefloat', 'Beta 2Y', 'Volatil. 12m', 'Volume 1D (R$ m)',
                      'BTC ÷ Free Float', 'Taxa Aluguel', 'p/vpa', 'p/l', 'evebtda', 'ROL 12m', 'ebtda', 'Mg. EBITDA', 'lpa', 'Mg, Líquida', 'dl', 'dl/ebtda', 'Pat. Líquido',
                      'wacc', 'dy', 'payout', 'roe']


#cordenada data arquivo eleven
cord_date = '108.208,47.969,134.238,117.876'

cord_page1 = '105.977,35.326,131.263,132.007'
cord_page2 = '103.999,35.0,751.018,563.771' 
#cord_page3 = '43.001,27.0,801.575,567.67'
#cord_page4 = '43.001,27.0,801.575,567.6'7c


#cordenada resultados eleven
cord_result1 = '196.0,40.0,706.178,426.724'
cord_result_other = '56.149,104.49,697.219,491.958'



def baixar_arquivo(url, endereco):
    resposta = requests.get(url)
    if resposta.status_code == requests.codes.OK:
        with open(endereco, 'wb') as novo_arquivo:
                novo_arquivo.write(resposta.content)
        print("Download finalizado. Arquivo salvo em: {}".format(endereco))
    else:
        resposta.raise_for_status()


#######################
#VALUATION POR GORDON##
#######################

#cacula crescimento na perpetuidade
def calc_crescimento(roe, payout):
    g = roe * (1 - payout)
    return g

#calcula preço justo por Gordon
def calc_gordon(lpa, payout, wacc, g):
    dividendos = lpa * payout
    desconto = wacc - g
    gordon = dividendos / desconto
    
    
    return gordon


#######################
#VALUATION POR ev/ebtda#
#######################
#recebe o ebtda, a dívida liquida e o evEbda para fazer calculo
#do valor do mercado
def calc_ValorMercado(ebtda, dl, evEbtda):
    vm = evEbtda*ebtda
    vm = vm - dl
            
    return vm
	


#######################
#Parse dos arquivos##
#######################

def parse_xp2(excel_file):
    #carrega arquivo XP excel
    df = pd.read_excel(excel_file)
    #deleta as primeiras linhas
    df = df.drop(df.index[0:1])
    #define a primeira linha como titulo da coluna
    df.columns = df.loc[1]
    #guarda apenas as colunas Ticker e Preço alvo
    df = df[['Ticker', 'Preço-Alvo']]
    df.columns = COLUMN_NAME_XP
    return df

def parse_necton(excel_file):
    #carrega arquivo XP excel
    df = pd.read_excel(excel_file, sheet_name='Planilha11')

    #pega a data 
    date = df.iloc[0,1]
    #Dá nome para as colunas. Usa o vetor definido no inicio do sript
    df.columns = COLUMN_NAME_NECTON
    #deleta as linhas vazias da tabela
    df = df.drop(df.index[0:13])
	
	#substitui todos os caracteres - por 0000
    df = df.replace('-', 0.00, regex=True)
    df = df.replace(' ', 0.00, regex=True)

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


#############################
#métodos para imprimir resultados na tela
#############################

#recebe uma linha necton
def print_indicadores(ativo):
     #pega os indicadores fundamentalistas
    vpa = ativo['p/vpa'].values[0]
    pl = ativo['p/l'].values[0]
    evebtatual = ativo['evebtda'].values[0]
    mgebtda = ativo['Mg. EBITDA'].values[0]
    lpa = ativo['lpa'].values[0]
    dlebtda = ativo['dl/ebtda'].values[0]
    dy = ativo['dy'].values[0] * 100
    roe = ativo['roe'].values[0] * 100

    print('\n')  
    print("INDICADORES FUNDAMENTALISTAS")
    print('P/VPA: ' + "{:12.2f}".format(vpa))
    print('P/L: ' + "      {:12.2f}".format(pl))
    print('EV/EBTDA:' + "  {:12.2f}".format(evebtatual))
    print('Mg. EBITDA:' + "{:12.2f}".format(mgebtda))
    print('LPA:' + "{:12.2f}".format(lpa))
    print('DL/EBTDA:' + "  {:12.2f}".format(dlebtda))
    print('DY:' + "        {:12.2f}%".format(dy))
    print('ROE:' + "       {:12.2f}%".format(roe))
    
    print('\n \n')

#imprime a tabela do consenso de mercado
def print_table(ativo1_bloom, ativo2_bloom, ativo1_elev, ativo2_elev, ativo1_xp, ativo2_xp, ticker1, ticker2):
    
    #monta string das outras instituições
    #outras1 = str(ativo1_bloom['qtdCompra'].values[0]) + '/' + str(ativo1_bloom['qtdNeutro'].values[0]) + '/'+ str(ativo1_bloom['qtdVenda'].values[0])
   # outras2 = str(ativo2_bloom['qtdCompra'].values[0]) + '/' + str(ativo2_bloom['qtdNeutro'].values[0]) + '/'+ str(ativo2_bloom['qtdVenda'].values[0])

    linha1 = [ticker1]
    linha2 = [ticker2]
    
    linha1.append(ativo1_elev['target'].values[0])
    linha1.append(ativo1_elev['upside'].values[0])
    linha1.append(ativo1_bloom['target'].values[0])
    linha1.append(ativo1_bloom['upside'].values[0])
    linha1.append(ativo1_xp['target'].values[0])
    linha1.append(ativo1_xp['upside'].values[0])

    linha2.append(ativo2_elev['target'].values[0])
    linha2.append(ativo2_elev['upside'].values[0])
    linha2.append(ativo2_bloom['target'].values[0])
    linha2.append(ativo2_bloom['upside'].values[0])
    linha2.append(ativo2_xp['target'].values[0])
    linha2.append(ativo2_xp['upside'].values[0])
	
    print_header()
    print_linha(linha1)
    print_linha(linha2)

	

def print_header():
	#formata e imprime o cabeçalho
    print('{:<16} {:<16} {:<16} {:<19} {:<16} {:<16} {:<16}'.format(*HEADER))
    #imprime linha com 60 '-'
    print('-'*135)

def print_linha(linha):
        print('{:<16} {:<16} {:<16.2f} {:<19.2f} {:<16.2f} {:<16} {:<16.2f}'.format(*linha))
        print('\n')
	

def process_ticker(bloom_df, eleven_df, xp_df):
    
    try:
        ticker1 = input("Digite o ticker 1:")
        preco1 = input("Digite o preço atual:")
        print("\n")
        ticker2 = input("Digite o ticker 2:")
        preco2 = input("Digite o preço atual:")
        print("\n")


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

        print_table(bloom1, bloom2, elev1, elev2, xp1, xp2, ticker1, ticker2)
        process_ticker(bloom_df, eleven_df, xp_df)
    except:
        print ("Não foi possível encontrar os ticker solicitado. Por favor, tente novamente")
        process_ticker(bloom_df, eleven_df, xp_df)

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
    

####################
#MÉTODOS PARA START NAS ESTRATÉGIAS
#####################


def start_consenso():
        #pega os daframe com os dados
        bloomberg = parse_necton(NECTON_ARQ)
        eleven = parse_eleven(ELEVEN_ARQ)

        eleven_df = eleven[1]
        bloom_df = bloomberg[1]
        xp_df = parse_xp2(XP_ARQ)


        #pega a data dos arquivos
        bloom_date = bloomberg[0]
        eleven_date = eleven[0]

        print('Data Bloomberg: ' + str(bloom_date))
        print('\n')
        print('Data Eleven: ' + str(eleven_date))
        print('\n')  
        
        process_ticker(bloom_df, eleven_df, xp_df)


def start_ev_ebtda():
    try:
        print('\n')
        ticker = input("ticker: ")
        evebtda = float(input("ev/ebtda projetado: "))
        ebtda_upside = int(input("Crescimento projetado do ebtda(em %): "))
        margem = int(input("Margem de segurança(em %): "))

        df_necton = parse_necton(NECTON_ARQ)
        df_necton = df_necton[1]
        ativo = busca_ticker(ticker, df_necton)

        ebtda = ativo['ebtda'].values[0]
        dl = ativo['dl'].values[0]
        qtde_acoes = ativo['qtdAcoes'].values[0]

        #calcula o ebtda com crescimento
        ebtda = ebtda + (ebtda_upside/100 * ebtda)
        #pega o valor de mercado projetado
        vm = calc_ValorMercado(ebtda, dl, evebtda)

        #preço justo da ação
        preco_justo = vm/qtde_acoes

        #preço com margem de segurança
        preco_margem = preco_justo - (margem/100 * preco_justo)

        print('\n')  
        print('Preço Justo: ' + "     {:12.2f}".format(preco_justo))
        print('Preço com Margem: ' + "{:12.2f}".format(preco_margem))
       
        print_indicadores(ativo)

    except:
        print("Ocorreu um erro...Reiniciando")
        start_ev_ebtda()
        
    start_ev_ebtda()


def start_gordon():
	try:
	    print('\n')
	    ticker = input("ticker: ")
	    margem = int(input("Margem de segurança(em %): "))
	
	    df_necton = parse_necton(NECTON_ARQ)
	    df_necton = df_necton[1]
	
	    #busca o ativo na tabela necton
	    ativo = busca_ticker(ticker, df_necton)
	
	    lpa = ativo['lpa'].values[0]
	    roe = ativo['roe'].values[0]
	    payout = ativo['payout'].values[0]
	    wacc = ativo['wacc'].values[0]
	
	    g = calc_crescimento(roe, payout)
	
	    preco_justo = calc_gordon(lpa, payout, wacc, g)
	    #preço com margem de segurança
	    preco_margem = preco_justo - (margem/100 * preco_justo)
	
	    print('\n')  
	    print('Preço Justo: ' + "     {:12.2f}".format(preco_justo))
	    print('Preço com Margem: ' + "{:12.2f}".format(preco_margem))
       
	    print_indicadores(ativo)
	
	except:
	    print("Ocorreu um erro...Reiniciando")
	    start_gordon()

	start_gordon()
            
def start():
    #baixa planilha necton
    baixar_arquivo(NECTON_URL, NECTON_ARQ)

    #baixa planilha XP
    baixar_arquivo(XP_URL, XP_ARQ)
    
    print('\n')  
    print("1 - Consenso de Mercado")
    print("2 - Calculo do Preço Justo (ev/ebtda)")
    print("3 - Calculo do Preço Justo Modelo Gordon")
    print('\n')  
    menu = input("Escolha um número de menu: ")

    if menu == '1':
        start_consenso()
    elif menu == '2':
        start_ev_ebtda()
    else:
        start_gordon()
    
    
        
start()

#df = read_page_eleven(ELEVEN_ARQ, "1", cord_page1)

    











