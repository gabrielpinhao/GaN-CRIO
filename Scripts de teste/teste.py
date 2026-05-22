import pandas as pd

file = r'Dados\SiCCT_VD10_final.csv'

df = pd.read_csv(file)

dc = df['Ids'][:25].mean()

df['Ids'] = abs(df['Ids'] - 0.02)

print(df.head(100))
print(dc)

df.to_csv(r'Dados\SiCCT_VD10_final.csv', index=False)
