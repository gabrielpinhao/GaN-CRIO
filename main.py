import tkinter as tk
from tkinter import ttk


def submit_values():
    """
    Função chamada quando o botão é pressionado.
    Ela obtém os valores dos campos de entrada.
    """
    try:
        # Pega os valores das variáveis e converte para float
        tensao = float(tensao_var.get())
        corrente = float(corrente_var.get())
        tempo_on = float(tempo_on_var.get())
        tempo_off = float(tempo_off_var.get())
        tensao_min = float(tensao_min_var.get())
        tensao_max = float(tensao_max_var.get())
        acresimo = float(acresimo_var.get())

        # Limpa a mensagem de status e exibe os valores no console
        status_var.set("Valores enviados com sucesso!")
        status_label.config(foreground="green")

        print("--- Valores Recebidos ---")
        print(f"Tensão: {tensao} V")
        print(f"Corrente: {corrente} A")
        print(f"Tempo ON: {tempo_on} s")
        print(f"Tempo OFF: {tempo_off} s")
        print(f"Tensão Mínima: {tensao_min} V")
        print(f"Tensão Máxima: {tensao_max} V")
        print(f"Acréscimo: {acresimo} V")
        print("-------------------------")

    except ValueError:
        # Exibe uma mensagem de erro se a conversão para float falhar
        status_var.set("Erro: Por favor, insira apenas números válidos.")
        status_label.config(foreground="red")


# --- Configuração da Janela Principal ---
root = tk.Tk()
root.title("Interface de Controle de Parâmetros")
root.geometry("350x330")  # Define um tamanho inicial

# --- Frame Principal ---
# Usar um frame com padding ajuda a organizar
main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.pack(expand=True, fill=tk.BOTH)

# --- Variáveis para armazenar os inputs ---
# Usar StringVars facilita o acesso aos valores dos campos
tensao_var = tk.StringVar()
corrente_var = tk.StringVar()
tempo_on_var = tk.StringVar()
tempo_off_var = tk.StringVar()
tensao_min_var = tk.StringVar()
tensao_max_var = tk.StringVar()
acresimo_var = tk.StringVar()

# --- Lista de Rótulos e Variáveis para criar os campos ---
# Isso evita repetir o código de criação de label/entry 7 vezes
input_fields = [
    ("Tensão (V):", tensao_var),
    ("Corrente (A):", corrente_var),
    ("Tempo ON (s):", tempo_on_var),
    ("Tempo OFF (s):", tempo_off_var),
    ("Tensão Mínima (V):", tensao_min_var),
    ("Tensão Máxima (V):", tensao_max_var),
    ("Acréscimo (V):", acresimo_var)
]

# --- Criação dos Widgets (Rótulos e Campos de Entrada) ---
# O loop 'for' cria um rótulo e um campo de entrada para cada item da lista
for i, (label_text, var) in enumerate(input_fields):
    # Rótulo (ex: "Tensão (V):")
    label = ttk.Label(main_frame, text=label_text)
    label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)

    # Campo de Entrada (Entry)
    entry = ttk.Entry(main_frame, width=20, textvariable=var)
    entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

# --- Botão de Envio ---
submit_button = ttk.Button(main_frame, text="Enviar Valores", command=submit_values)
submit_button.grid(row=len(input_fields), column=0, columnspan=2, pady=10)

# --- Rótulo de Status ---
# Usado para exibir mensagens de sucesso ou erro
status_var = tk.StringVar()
status_label = ttk.Label(main_frame, textvariable=status_var, font=("Arial", 9, "italic"))
status_label.grid(row=len(input_fields) + 1, column=0, columnspan=2)

# --- Iniciar a Interface ---
root.mainloop()
