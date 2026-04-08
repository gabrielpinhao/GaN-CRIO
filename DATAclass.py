from matplotlib import ticker
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

class DATAclass:
    def __init__(self):
        # Centralizar colunas fixas se o formato for sempre o mesmo
        self.column_headers = ['Time_Raw', "Vg", "Vds", "Ids", "Extra"]

    def selecionar_arquivo(self):
        root = tk.Tk()
        root.withdraw()
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo de dados",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
        return caminho if caminho else None

    def processar_dados(self, caminho):
        # Uso do usecols para evitar erro se houver mais colunas que o esperado
        df = pd.read_csv(caminho, skiprows=15, header=None)
        
        # Ajuste dinâmico de colunas para não quebrar se o CSV mudar
        n_cols = df.shape[1]
        cols = self.column_headers[:n_cols] if n_cols <= len(self.column_headers) else [f"Col_{i}" for i in range(n_cols)]
        df.columns = cols

        # Conversão de tempo
        time_series = pd.to_datetime(df['Time_Raw'], format='%H:%M:%S.%f')
        
        # Lógica do degrau (Trigger)
        limiar = df['Vg'].max() * 0.5 
        indices_acima = df.index[df['Vg'] > limiar].tolist()
        t_ref = time_series.iloc[indices_acima[0]] if indices_acima else time_series.iloc[0]

        df['Time'] = (time_series - t_ref).dt.total_seconds() * 1e6
        
        # Dropar colunas desnecessárias com segurança
        cols_to_drop = [c for c in ['Time_Raw', 'Extra'] if c in df.columns]
        df.drop(columns=cols_to_drop, inplace=True)

        return df

    def plot_separated(self, df):
        fig, (ax_v, ax_i) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Itera sobre colunas que não são o tempo
        data_cols = [c for c in df.columns if c != 'Time']
        
        for trace in data_cols:
            if 'V' in trace:
                ax_v.plot(df['Time'], df[trace], label=trace)
            elif 'I' in trace:
                ax_i.plot(df['Time'], df[trace], label=trace)
            else:
                ax_v.plot(df['Time'], df[trace], label=f"{trace} (Outro)")

        for ax in [ax_v, ax_i]:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(loc='upper right')

        ax_v.set_title('Dados do Registrador DL850')
        ax_v.set_ylabel('Tensão (V)')
        ax_i.set_ylabel('Corrente (A)')
        ax_i.set_xlabel('Tempo (us)')

        plt.tight_layout()
        plt.show()

    def dc_estimator(self, df, window_us=10):
        """
        Calcula o valor DC pegando a média dos valores estáveis antes da queda do pulso Vg.
        
        Parâmetros:
        - df : DataFrame processado (com a coluna 'Time' em us)
        - window_us : Tamanho da janela (em microssegundos) para calcular a média antes da queda.
        """
        
        # 1. Encontrar o ponto onde o pulso Vg termina (queda)
        # Consideramos que o pulso terminou quando Vg cai abaixo de 50% do máximo
        vg_max = df['Vg'].max()
        threshold = vg_max * 0.5
        
        # Procuramos o último índice onde Vg ainda é maior que o threshold
        # (Considerando que o pulso começa em t=0)
        indices_pulso = df.index[df['Vg'] > threshold].tolist()
        
        if not indices_pulso:
            print("Erro: Pulso Vg não detectado.")
            return 0, 0, 0
            
        idx_final_pulso = indices_pulso[-1]
        t_final_pulso = df.loc[idx_final_pulso, 'Time']
        
        # 2. Definir a janela de medição (ex: 10us antes do final do pulso)
        t_inicio_janela = t_final_pulso - window_us
        
        # Filtramos o dataframe para pegar apenas essa janela estável
        # Garantimos que não pegamos valores antes de t=0 (início do pulso)
        janela_estavel = df[(df['Time'] >= max(0, t_inicio_janela)) & 
                            (df['Time'] <= t_final_pulso)]
        
        if janela_estavel.empty:
            print("Erro: Janela de medição vazia.")
            return 0, 0, 0

        # 3. Calcular as médias na janela
        ret_vg = janela_estavel['Vg'].mean()
        ret_vds = janela_estavel['Vds'].mean()
        ret_ids = janela_estavel['Ids'].mean()
        
        return ret_vg, ret_vds, ret_ids
    
    def plot_output_characteristic(self, local_folder, test_name):
        # 1. Construir o caminho da pasta e procurar o arquivo que termina com 'ALL.csv'
        target_dir = os.path.join(local_folder, test_name)
        
        if not os.path.exists(target_dir):
            print(f"Erro: A pasta {target_dir} não existe.")
            return

        # Procura por qualquer arquivo que termine com 'ALL.csv' dentro da pasta
        files = [f for f in os.listdir(target_dir) if f.endswith('ALL.csv')]
        
        if not files:
            print(f"Erro: Nenhum arquivo 'ALL.csv' encontrado em {target_dir}")
            return
        
        # Pega o primeiro arquivo encontrado
        csv_path = os.path.join(target_dir, files[0])
        print(f"Lendo resumo: {csv_path}")

        # 2. Ler o CSV
        # Como o arquivo tem cabeçalho (Arquivo, Vg, Vds, Ids), o pandas lê automaticamente
        df_all = pd.read_csv(csv_path)

        # 3. Plotar Ids (Y) por Vds (X)
        plt.figure(figsize=(10, 6))
        
        # Plotamos como pontos e linha para ver a curva característica
        plt.plot(df_all['Vds'], df_all['Ids'], 'o-', label=test_name, markersize=4)

        plt.title(f'Curva de Saída (Output Characteristic) - {test_name}')
        plt.xlabel('Vds (V)')
        plt.ylabel('Ids (A)')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend()
        
        # 4. Estética opcional: Mostrar o valor de Vg médio se for constante
        vg_medio = df_all['Vg'].mean()
        plt.annotate(f'Vg ≈ {vg_medio:.2f}V', 
                    xy=(df_all['Vds'].iloc[-1], df_all['Ids'].iloc[-1]),
                    xytext=(10, 0), textcoords='offset points')

        plt.tight_layout()
        plt.show()
    
# ==========================
# EXECUÇÃO CORRIGIDA
# ==========================

local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"
test_name = "MOS6_OUTPUT"

if __name__ == "__main__":
    data = DATAclass()
    #last_file = data.selecionar_arquivo()
    last_file = r'C:\Users\nitee\Desktop\GaN-CRIO\GaN-CRIO\Ensaios\OUTPUT_TEST\OUTPUT_TEST0022.CSV'

    # if last_file:
    #     df = data.processar_dados(last_file)
    #     vg, vds, ids = data.dc_estimator(df)
    #     print(f"Valor DC estimado - Vg: {vg:.2f} V, Vds: {vds:.2f} V, Ids: {ids:.2f} A")
    #     data.plot_separated(df)
    # else:
    #     print("Nenhum arquivo selecionado.")

    data.plot_output_characteristic(local_folder, test_name)

    