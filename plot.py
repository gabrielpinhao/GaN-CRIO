import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

print("Por favor, selecione o arquivo csv")

# 1. Carregar os dados via Janela
arquivo = filedialog.askopenfilename(
    title="Selecione o arquivo de dados",
    filetypes=[("Arquivos CSV", "*.CSV"), ("Todos os arquivos", "*.*")]
) 

if not arquivo:
    print("Nenhum arquivo selecionado. Encerrando.")
    exit()

print(f"Arquivo selecionado: {arquivo}")

# CORREÇÃO AQUI: Lendo separado por vírgula (sep=','), pulando 16 linhas e sem cabeçalho
df = pd.read_csv(arquivo, sep=',', skiprows=16, header=None)

choice = input("Deseja visualizar os dados? (1/2): ")

if choice == '1': #Le arquivo salvo no oscioloscópio e baixado para o PC
    # 2. Organizar as colunas
# O Yokogawa coloca uma vírgula no final da linha, criando uma 3ª coluna vazia
    df.columns = ['Tempo', 'Tensao', 'Vazia'] 

# Converter a coluna de tempo (string) para o formato de data/hora do Pandas
    df['Tempo'] = pd.to_datetime(df['Tempo'])

# 3. Criar o gráfico com Matplotlib
    plt.figure(figsize=(12, 6))
    plt.plot(df['Tempo'], df['Tensao'], color='#1f77b4', linewidth=1.5, label='Trace: Vf')

# 4. Customizar o visual do gráfico
    plt.title('Forma de Onda - Yokogawa DL850EV', fontsize=14, fontweight='bold')
    plt.xlabel('Tempo', fontsize=12)
    plt.ylabel('Tensão (V)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper right')

# Rotacionar os rótulos do eixo X caso fiquem sobrepostos
    plt.xticks(rotation=45)

# Ajustar o layout para não cortar nada
    plt.tight_layout()

# 5. Exibir o gráfico
    plt.show()

elif choice == '2': #Le arquivo ja salvo dentro da memoria notebook
    # LEITURA TIPO 2: Arquivo limpo, leitura direta do Pandas
    df = pd.read_csv(arquivo)

    # Criar o gráfico
    plt.figure(figsize=(12, 6))

    # Plota usando os nomes das colunas que já vêm perfeitas no arquivo direto
    plt.plot(df['Tempo (s)'], df['Tensao (V)'], color='#d62728', linewidth=1.5, label='Canal 9')

    plt.title('Forma de Onda - Captura Direta via Rede', fontsize=14, fontweight='bold')
    plt.xlabel('Tempo (s)', fontsize=12)
    plt.ylabel('Tensão (V)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

else:
    print("Opção inválida. Encerrando.")