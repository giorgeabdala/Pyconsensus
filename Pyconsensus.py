#requisitos: panda, xlrd, 


import pandas as pd
excel_file = 'consenso.xlsx'

#define nome das colunas do DF final
COLUMN_NAME = ['ticker', 'target', 'consenso', 'qtdInst', 'qtdCompra', 'qtdNeutro', 'qtdVenda']

#carrega o arquivo excel pulando as primeiras 9 linhas
df = pd.read_excel(excel_file)

#pega a data do arquivo
date = df.iloc[4,1]

#deleta as 9 priemiras linhas
df = df.drop(df.index[0:9])

#deleta as colunas 0,2 e 5 (Unamed, Empresa, preço e Upside/Downside)
df = df.drop(df.columns[[0,2,3,5]], axis=1)

#renomeado colunas
df.columns = COLUMN_NAME

#faz um replace na coluna ticker e retira o ' BS'
df['ticker'] = df['ticker'].str.replace(' BS', '')








