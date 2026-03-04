import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calcular_dc(df,
                lim_diff_percent=90,
                level_margin=0.7):
    """
    Calcula o valor DC removendo as bordas usando critério de derivada.

    Parâmetros:
    - df : DataFrame com tempo, tensão e corrente
    - lim_diff_percent : percentil para definir o limite de estabilidade
    - level_margin : fração para separar nível alto do baixo (0 a 1)

    Retorna:
    - Valor médio da tensão, corrente
    """

    col_time=df.columns[0]
    col_volt=df.columns[1]
    col_curr=df.columns[2]

    t = df[col_time].values
    v = df[col_volt].values
    i = df[col_curr].values

    # Derivada numérica
    dv_dt = np.gradient(v, t)
    di_dt = np.gradient(i, t)

    # Detectar regiões estáveis (derivada pequena)
    lim_diff_v = np.percentile(np.abs(dv_dt), lim_diff_percent)
    stable_v = np.abs(dv_dt) < lim_diff_v

    lim_diff_i = np.percentile(np.abs(di_dt), lim_diff_percent)
    stable_i = np.abs(di_dt) < lim_diff_i

    # Estimar níveis alto e baixo robustamente
    v_low = np.percentile(v, 5)
    v_high = np.percentile(v, 95)

    i_low = np.percentile(i, 5)
    i_high = np.percentile(i, 95)

    # Separar apenas o nível alto dentro da região estável
    lim_level_v = v_low + level_margin * (v_high - v_low)
    mask_high_v = (v > lim_level_v) & stable_v

    lim_level_i = i_low + level_margin * (i_high - i_low)
    mask_high_i = (i > lim_level_i) & stable_i

    ret_v = np.mean(v[mask_high_v]) if np.sum(mask_high_v) > 0 else np.nan
    ret_i = np.mean(i[mask_high_i]) if np.sum(mask_high_i) > 0 else np.nan

    return ret_v, ret_i

def plot_osciloscopio(df):
    v_dc, i_dc = calcular_dc(df)

    plt.figure(figsize=(10,5))
    plt.plot(df[df.columns[0]], df[df.columns[1]], c='red', label='Tensão (V)')
    plt.plot(df[df.columns[0]], df[df.columns[2]], c='blue', label='Corrente (A)')

    plt.xlabel(df.columns[0])
    plt.ylabel(df.columns[1])
    plt.title(f"Valor DC estimado: V = {v_dc:.4f} V, I = {i_dc:.4f} A")
    plt.grid(True)
    plt.legend()

    plt.show()

file = r'medicao_direta.csv'
df = pd.read_csv(file)

#print(df.head())
plot_osciloscopio(df)

#v_dc, i_dc = calcular_dc(df)
#print(f"Valor DC estimado: V = {v_dc:.4f} V, I = {i_dc:.4f} A")