import subprocess
import pandas as pd

#nome das colunas do df final
COLUMN_NAME = ["ticker", "target", "precoLimite", "recomendacao", "risco", "qualidade", "indice"]

#chamada ao tabula-java
subprocess.call("java -jar ./tabula-1.0.3-jar-with-dependencies.jar -p 2 -a 82.923,35.0,738.122,560.052 -o saida.csv eleven.pdf", shell=True)
df = pd.read_csv("saida.csv", sep=",", encoding='cp1252')

#delete as colunas inuteis
df = df.drop(df.columns[[0,1,3,5,8,12]], axis=1)

#deleta primeira linha
df = df.drop([0,1,2,3,4])

df.columns = COLUMN_NAME

#deleta linhas onde todos os valores são NaN
df = df.dropna(how='all')

