from tkinter import *

root = Tk()
root.title("Controle por Tensão")
root.geometry("220x230")
root.iconbitmap('C:/Users/Gabriel/OneDrive/UFF/IC/python/uffazul.ico')

# Labels

label_tensao = Label(root, text="Tensão de partida (V):").grid(row=0, column=0, pady= 2)
label_tensao_max = Label(root, text="Tensão Máxima (V):").grid(row=1, column=0,pady= 2)
label_acrescimo = Label(root, text="Acréscimo (V):").grid(row=2, column=0,pady= 2)
label_corrente = Label(root, text="Corrente (A):").grid(row=3, column=0,pady= 2)
label_tempo_on = Label(root, text="Time ON (s):").grid(row=4, column=0,pady= 2)
label_tempo_off = Label(root, text="Time OFF (s):").grid(row=5, column=0,pady= 2)


status = Label(root, text="Status da fonte").grid(row=7, column=0, pady= 5)

# Botoes

botao_enviar = Button(root, text="ENVIAR").grid(row=8, column=0)
botao_parar = Button(root, text="PARAR", fg="Red").grid(row=8, column=1)

# Funcoes dos botoes (a definir)

# Entrada de dados

tensao_partida = Entry(root, width=10).grid(row=0, column=1,pady= 2)
tensao_max = Entry(root, width=10).grid(row=1, column=1,pady= 2)
acrescimo = Entry(root, width=10).grid(row=2, column=1,pady= 2)
corrente = Entry(root, width=10).grid(row=3, column=1,pady= 2)
tempo_on = Entry(root, width=10).grid(row=4, column=1,pady= 2)
tempo_off = Entry(root, width=10).grid(row=5, column=1,pady= 2)


# Definir condicoes


root.mainloop()