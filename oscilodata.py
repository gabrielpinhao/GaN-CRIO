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
    """
    Plotar os dados do osciloscópio e mostrar o valor DC estimado.

    Parâmetro:
    - df : DataFrame com tempo, tensão e corrente
    """
    
    v_dc, i_dc = calcular_dc(df)

    fig, ax1 = plt.subplots(figsize=(8,5))

    # Tensão (eixo esquerdo)
    line1, = ax1.plot(df[df.columns[0]]*1000, df[df.columns[1]],
                      color='red', label='Voltage [V]')
    ax1.set_xlabel('Time [ms]')
    ax1.set_ylabel('Voltage [V]', color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # Segundo eixo
    ax2 = ax1.twinx()

    # Corrente (eixo direito)
    line2, = ax2.plot(df[df.columns[0]]*1000, df[df.columns[2]],
                      color='blue', label='Current [A]')
    ax2.set_ylabel('Current [A]', color='black')
    ax2.tick_params(axis='y', labelcolor='black')

    plt.title(f"Estimated DC Levels: {v_dc:.4f} V and {i_dc:.4f} A")

    # Combinar legendas
    lines = [line1, line2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right')

    ax1.grid(True)

    plt.show()

file = r'medicao_teste.csv'
df = pd.read_csv(file)

#print(df.head())
plot_osciloscopio(df)

#v_dc, i_dc = calcular_dc(df)
#print(f"Valor DC estimado: V = {v_dc:.4f} V, I = {i_dc:.4f} A")