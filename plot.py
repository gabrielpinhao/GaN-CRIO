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