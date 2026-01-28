import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

print("Por favor, selecione o arquivo txt")
# 1. Carregar os dados
# Substitua 'seu_arquivo.txt' pelo nome real do arquivo gerado
arquivo = filedialog.askopenfilename(
    title="Selecione o arquivo de dados",
    filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
) 

if not arquivo:
    print("Nenhum arquivo selecionado. Encerrando.")
    exit()

print(f"Arquivo selecionado: {arquivo}")

df = pd.read_csv(arquivo, sep='\t')
# 2. Definir os eixos
# Eixo X = Corrente (Geralmente a variável independente)
eixo_x = df['NanoVolt (V)'] * -1

# Eixo Y = Tensão (Geralmente a variável dependente - Resposta)
eixo_y = df['Corrente_Set (A)']

# 3. Criar o gráfico
plt.figure(figsize=(10, 6))

# 'o-' cria uma linha com bolinhas marcando os pontos medidos
plt.plot(eixo_x, eixo_y, 'o-', color='blue', label='Dados Experimentais')

# 4. Formatação
plt.title('Curva IxV: Corrente vs Tensão')
plt.xlabel('Tensão (V)')
plt.ylabel('Corrente Setada (A)')
plt.grid(True, linestyle='--', alpha=0.6) # Grade para facilitar leitura
plt.legend()

# 5. Exibir
plt.show()