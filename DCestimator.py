import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def dc_estimator(df, i_tolerance=0.98, v_tolerance=0.9):
    """Calcula o valor DC usando a média dos pontos mais altos.

    Parâmetros:
    - df : DataFrame com tempo, tensão e corrente
    - i_tolerance : tolerância para considerar os pontos mais altos da corrente (0 a 1)
    - v_tolerance : tolerância para considerar os pontos mais altos da tensão (0 a 1)

    Retorna:
    - Valor médio da tensão, corrente
    """

    v = df['Voltage'].values
    i = df['Current'].values

    v_max = np.max(v)
    i_max = np.max(i)

    mask_v = v > v_tolerance * v_max
    mask_i = i > i_tolerance * i_max

    ret_v = np.mean(v[mask_v])
    ret_i = np.mean(i[mask_i])

    return ret_v, ret_i

def time_plot(df):
    """
    Plotar os dados do osciloscópio e mostrar o valor DC estimado.

    Parâmetro:
    - df : DataFrame com tempo, tensão e corrente
    """

    v_dc, i_dc = dc_estimator(df)

    fig, ax1 = plt.subplots(figsize=(15,5))

    line1, = ax1.plot(df['Time'], df['Voltage'],
                      color='tomato', label='Voltage [V]')
    
    

    ax1.set_xlabel('Time [ms]')
    ax1.set_ylabel('Voltage [V]', color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    ax2 = ax1.twinx()

    line2, = ax2.plot(df['Time'], df['Current'],
                      color='deepskyblue', label='Current [A]')
    
    dc_v_line = ax1.axhline(v_dc, color='orangered', label='V_DC', linestyle='--')
    dc_i_line = ax2.axhline(i_dc, color='dodgerblue', label='I_DC', linestyle='--')

    ax2.set_ylabel('Current [A]', color='black')
    ax2.tick_params(axis='y', labelcolor='black')

    plt.title(f"Estimated DC Levels: {v_dc:.4f} V and {i_dc:.4f} A")

    lines = [line1, line2, dc_v_line, dc_i_line]
    labels = [l.get_label() for l in lines]

    ax1.legend(lines, labels, loc='upper right')
    ax1.grid(True)
    plt.show()

def single_csv_to_df(file_path):
    """Lê um arquivo CSV gerado pelo osciloscópio e converte para um DataFrame.

    Parametros:
    - file_path : caminho do arquivo CSV

    Retorna:
    - DataFrame com colunas: Time, Current, Voltage
    """

    columns = ['Time', 'Current', 'Voltage', 'Noise']
    df = pd.read_csv((file_path), skiprows=15, names=columns)

    df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S.%f")
    df["Time_ms"] = (df["Time"] - df["Time"].iloc[0]).dt.total_seconds() * 1000

    df = df.drop(columns=["Time"])
    df = df.rename(columns={"Time_ms": "Time"})

    df = df.drop(columns=["Noise"])

    return df

def post_test_trace(local_folder, test_name):
    path = os.path.join(local_folder, test_name)

    if not os.path.exists(path):
        print(f"Folder {path} not found.")
        return []

    items = os.listdir(path)

    csv_files = [f for f in items if f.lower().endswith(".csv")]

    v_list = []
    i_list = []

    for test in csv_files:
        test_path = f"{local_folder}/{test_name}/{test}"

        df = single_csv_to_df(test_path)
        ret_v, ret_i = dc_estimator(df)
        time_plot(df)

        v_list.append(ret_v)
        i_list.append(ret_i)

    return v_list, i_list

def main():
    """Função principal para estimar os valores DC a partir dos arquivos CSV gerados pelo osciloscópio.
    """

    local_folder = 'Ensaios'
    test_name = "CARUSO_NOVO"
    v_list, i_list = post_test_trace(local_folder, test_name)

    plt.plot(i_list, v_list, marker='o')
    plt.xlabel("Current [A]")
    plt.ylabel("Voltage [V]")
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    main()