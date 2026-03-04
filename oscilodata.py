import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calcular_dc(df,
                limiar_derivada_percentil=90,
                margem_nivel=0.7):
    """
    Calcula o valor DC removendo as bordas usando critério de derivada.

    Parâmetros:
    - df : DataFrame com tempo e tensão
    - limiar_derivada_percentil : percentil usado para detectar bordas
    - margem_nivel : fração para separar nível alto do baixo (0 a 1)

    Retorna:
    - Valor médio do patamar alto
    """

    col_tempo=df.columns[0]
    col_tensao=df.columns[1]
    t = df[col_tempo].values
    v = df[col_tensao].values

    # Derivada numérica
    dv_dt = np.gradient(v, t)

    # Detectar regiões estáveis (derivada pequena)
    limiar_derivada = np.percentile(np.abs(dv_dt), limiar_derivada_percentil)
    regiao_estavel = np.abs(dv_dt) < limiar_derivada

    # Estimar níveis alto e baixo robustamente
    v_low = np.percentile(v, 5)
    v_high = np.percentile(v, 95)

    # Separar apenas o nível alto dentro da região estável
    limiar_nivel_alto = v_low + margem_nivel * (v_high - v_low)
    mascara_alto = (v > limiar_nivel_alto) & regiao_estavel

    # Média do patamar alto
    if np.sum(mascara_alto) == 0:
        return np.nan  # evita erro se não detectar patamar

    return np.mean(v[mascara_alto])

def plot_osciloscopio(df):
    # Plotando o gráfico
    plt.figure(figsize=(10,5))
    plt.plot(df[df.columns[0]], df[df.columns[1]])

    plt.xlabel(df.columns[0])
    plt.ylabel(df.columns[1])
    plt.title(f'Valor DC: {calcular_dc(df):.4f}')
    plt.grid(True)

    plt.show()

file = r'C:\Users\nitee\Desktop\GaN-CRIO\GaN-CRIO\medicao_direta.csv'
df = pd.read_csv(file)

print(df.head())
plot_osciloscopio(df)
print(calcular_dc(df))