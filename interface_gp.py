from tkinter import *

root = Tk()
root.title("Menu")


#|Função dos botoes menu

def chamar_tensao():
    interface_tensao = Toplevel(root)
    interface_tensao.geometry("220x230")
    interface_tensao.title("Controle de Tensão")

    # Labels janela tensão

    label_tensao = Label(interface_tensao, text="Tensão de partida (V):",font=("Times New Roman", 13)).grid(row=0, column=0, pady=2)
    label_tensao_max = Label(interface_tensao, text="Tensão Máxima (V):").grid(row=1, column=0, pady=2)
    label_acrescimo = Label(interface_tensao, text="Acréscimo (V):").grid(row=2, column=0, pady=2)
    label_corrente = Label(interface_tensao, text="Corrente (A):").grid(row=3, column=0, pady=2)
    label_tempo_on = Label(interface_tensao, text="Time ON (s):").grid(row=4, column=0, pady=2)
    label_tempo_off = Label(interface_tensao, text="Time OFF (s):").grid(row=5, column=0, pady=2)

    status_tensao = Label(interface_tensao, text="Status da fonte").grid(row=7, column=0, pady=5)

    # Botoes

    botao_enviar = Button(interface_tensao, text="ENVIAR").grid(row=8, column=0)
    botao_parar = Button(interface_tensao, text="PARAR", fg="Red").grid(row=8, column=1)

    # Funcoes dos botoes (a definir)

    # Entrada de dados

    tensao_partida = Entry(interface_tensao, width=10).grid(row=0, column=1, pady=2)
    tensao_max = Entry(interface_tensao, width=10).grid(row=1, column=1, pady=2)
    acrescimo = Entry(interface_tensao, width=10).grid(row=2, column=1, pady=2)
    corrente = Entry(interface_tensao, width=10).grid(row=3, column=1, pady=2)
    tempo_on = Entry(interface_tensao, width=10).grid(row=4, column=1, pady=2)
    tempo_off = Entry(interface_tensao, width=10).grid(row=5, column=1, pady=2)

    return chamar_tensao

def chamar_corrente():

    interface_corrente = Toplevel(root)
    interface_corrente.geometry("220x230")
    interface_corrente.title("Controle de Corrente")

    # Labels janela tensão

    label_tensao = Label(interface_corrente, text="Corrente de Partida (A):").grid(row=0, column=0, pady=2)
    label_tensao_max = Label(interface_corrente, text="Corrente Máxima (A):").grid(row=1, column=0, pady=2)
    label_acrescimo = Label(interface_corrente, text="Acréscimo (A):").grid(row=2, column=0, pady=2)
    label_corrente = Label(interface_corrente, text="Tensão (V):").grid(row=3, column=0, pady=2)
    label_tempo_on = Label(interface_corrente, text="Time ON (s):").grid(row=4, column=0, pady=2)
    label_tempo_off = Label(interface_corrente, text="Time OFF (s):").grid(row=5, column=0, pady=2)

    frame_status = Label(interface_corrente, text="Status da fonte",pady=5, padx=5).grid(row=6)


    # Botoes

    botao_enviar = Button(interface_corrente, text="ENVIAR").grid(row=8, column=0)
    botao_parar = Button(interface_corrente, text="PARAR", fg="Red").grid(row=8, column=1)

    # Funcoes dos botoes (a definir)

    # Entrada de dados

    corrente_partida = Entry(interface_corrente, width=10).grid(row=0, column=1, pady=2)
    corrente_max = Entry(interface_corrente, width=10).grid(row=1, column=1, pady=2)
    acrescimo = Entry(interface_corrente, width=10).grid(row=2, column=1, pady=2)
    tensao = Entry(interface_corrente, width=10).grid(row=3, column=1, pady=2)
    tempo_on = Entry(interface_corrente, width=10).grid(row=4, column=1, pady=2)
    tempo_off = Entry(interface_corrente, width=10).grid(row=5, column=1, pady=2)

    return chamar_corrente

# Labels Botoes menu

botao_tensao = Button(root, text="Controle de Tensão", command=chamar_tensao).pack(pady=20, padx=50)
botao_corrente = Button(root, text="Controle de Corrente", command=chamar_corrente).pack(pady=15, padx=50)


# Definir condicoes


root.mainloop()