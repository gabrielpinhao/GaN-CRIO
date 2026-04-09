import sys
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

    def print_progress(self, i, total, prefix="Progress", bar_length=50):
        """Exibe uma barra de progresso no terminal.
        Parameters:
        - i: O número atual de iterações concluídas.
        - total: O número total de iterações.
        - prefix: Um texto opcional para mostrar antes da barra de progresso.
        - bar_length: O comprimento da barra de progresso em caracteres.
        """
        progress = i / total
        filled = round(bar_length * progress)
        bar = "█" * filled + "-" * (bar_length - filled)

        percent = round(progress * 100)

        print(f"\r{prefix}: |{bar}| {percent}% ({i}/{total})", end="")
        sys.stdout.flush()

        if i == total:
            print()  # quebra linha no final

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
        Estimates the DC values of Vg, Vds, and Ids by averaging the values
        in a stable window before the pulse ends.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame processed with Time, Vg, Vds, Ids columns.
        window_us : int, optional
            Measurement window in microseconds before the end of the pulse
            to consider for averaging.

        Returns
        -------
        ret_vg : float
            Estimated DC value of Vg.
        ret_vds : float
            Estimated DC value of Vds.
        ret_ids : float
            Estimated DC value of Ids.
        """

        vg_max = df['Vg'].max()
        threshold = vg_max * 0.5

        indices_pulso = df.index[df['Vg'] > threshold].tolist()
        
        if not indices_pulso:
            print("Error: Vg pulse not detected.")
            return 0, 0, 0

        idx_final_pulso = indices_pulso[-1]
        t_final_pulso = df.loc[idx_final_pulso, 'Time']
        
        # Definir a janela de medição (ex: 10us antes do final do pulso)
        t_inicio_janela = t_final_pulso - window_us

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
    
    def actual_plot(self, df_all, test_name, test='Output'):
        """
        Plot the output or transfer characteristic curve
        from a consolidated DataFrame.

        Parameters
        ----------
        df_all : pandas.DataFrame
            Consolidated dataset containing the electrical variables.
            Expected columns include 'Vg', 'Vds', and 'Ids'.
        test : str, optional
            Type of characteristic to plot. Supported values are
            'Output' and 'Transfer'. This parameter determines the
            variable used on the x-axis. Default is 'Output'.

        Returns
        -------
        None
            This function generates a plot and does not return a value.
        """

        if test == 'Output':
            x_axis, media, title = 'Vds', 'Vg', 'Output Characteristic'
        elif test == "Transfer":
            x_axis, media, title = 'Vg', 'Vds', 'Transfer Characteristic'
        else:
            print("Unknown test. Use 'Output' or 'Transfer'.")
            return

        plt.figure(figsize=(5, 4))
        plt.plot(df_all[x_axis], df_all['Ids'], 'o',
                 label=test_name, markersize=4)

        plt.title(f'{title} - {test_name}')
        plt.xlabel(f'{x_axis} (V)')
        plt.ylabel('Ids (A)')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend()

        v_medio = df_all[media].mean()
        plt.annotate(
            f'{media} ≈ {v_medio:.2f}V',
            xy=(1, 0),                 # canto inferior direito
            xycoords='axes fraction',
            xytext=(-10, 10),          # pequeno deslocamento pra dentro
            textcoords='offset points',
            ha='right',
            va='bottom'
            )

        plt.tight_layout()
        plt.show()
    
    def sweep_plot(self, local_folder, test_name, test='Output'):
        """
        Plot the output or transfer characteristic curve by processing
        all individual CSV files within a specified test directory.

        Parameters
        ----------
        local_folder : str
            Base directory where the test data is stored.
        test_name : str
            Name of the test (subdirectory) containing the CSV files.
        test : str, optional
            Type of characteristic to plot. Supported values are
            'Output' and 'Transfer'. Default is 'Output'.

        Returns
        -------
        None
            This function generates a plot and does not return a value.
        """

        target_dir = os.path.join(local_folder, test_name)
        
        if not os.path.exists(target_dir):
            print(f"Erro: A pasta {target_dir} não existe.")
            return

        files = [f for f in os.listdir(target_dir)
                if f.lower().endswith('.csv') and 'all' not in f.lower()
        ]
        
        if not files:
            print(f"Erro: Nenhum arquivo CSV encontrado em {target_dir}")
            return
        
        df_output = []
        i = 0

        for file in files:
            csv_path = os.path.join(target_dir, file)

            df = self.processar_dados(csv_path)
            vg, vds, ids = self.dc_estimator(df)

            df_output.append({
                'Arquivo': file,
                'Vg': vg,
                'Vds': vds,
                'Ids': ids
            })

            i += 1
            self.print_progress(i, len(files), prefix=f"Plotting {test_name}")

        df_final = pd.DataFrame(df_output)

        self.actual_plot(df_final, test='Transfer')
        
        print(f"Arquivo: {file}, Vg: {vg:.2f} V, Vds: {vds:.2f} V, Ids: {ids:.2f} A")

# ==========================
# EXECUÇÃO TESTE
# ==========================

if __name__ == "__main__":
    data = DATAclass()

    local_folder = "Ensaios"
    test_name = "MOS9_OUTPUT"

    file_final = f"{local_folder}/{test_name}/{test_name}_ALL.csv"

    data.actual_plot(pd.read_csv(file_final), test_name, test='Output')