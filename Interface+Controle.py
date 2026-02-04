from tkinter import *
import threading
from fonteobjeto import *

minha_fonte = Fonte('GPIB0::1::INSTR')

root = Tk()
root.title("Menu Agilent 6680A")
root.iconbitmap(r'C:\Users\nitee\Desktop\GaN-CRIO\GaN-CRIO\figura.ico')

def centralizar_janela(janela, largura, altura):
    """
    Calcula e define a posição da janela para centralizá-la na tela.
    """
    # 1. Obter as dimensões da tela
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    # 2. Calcular a posição (x e y) para centralizar
    pos_x = int((largura_tela / 2) - (largura / 2))
    pos_y = int((altura_tela / 2) - (altura / 2))

    # 3. Aplicar a geometria com a posição calculada
    # Formato: "LarguraxAltura+PosicaoX+PosicaoY"
    janela.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')

largura = 400
comprimento = 150

centralizar_janela(root, largura, comprimento)

#|Função dos botoes menu

def chamar_tensao():
    interface_tensao = Toplevel(root)
    interface_tensao.geometry("330x390")
    interface_tensao.title("Controle de Tensão")
    interface_tensao['bg'] = 'lightblue'
    interface_tensao.iconbitmap(r'C:\Users\nitee\Desktop\GaN-CRIO\GaN-CRIO\figura.ico')

    conexaoT = minha_fonte.conectar()

    if conexaoT:
        mensagem = "Instrumento Conectado"
    else:
        mensagem = "Erro ao conectar"


    # Labels janela tensão

    label_tensao = Label(interface_tensao, text="Tensão de Partida (V):",font=("Times New Roman", 13), bg='lightblue').grid(row=0, column=0, pady=2)
    label_tensao_max = Label(interface_tensao, text="Tensão Máxima (V):",font=("Times New Roman", 13), bg='lightblue').grid(row=1, column=0, pady=2)
    label_acrescimo = Label(interface_tensao, text="Acréscimo (V):",font=("Times New Roman", 13), bg='lightblue').grid(row=2, column=0, pady=2)
    label_tempo_on = Label(interface_tensao, text="Time ON (s):",font=("Times New Roman", 13), bg='lightblue').grid(row=3, column=0, pady=2)
    label_tempo_off = Label(interface_tensao, text="Time OFF (s):",font=("Times New Roman", 13), bg='lightblue').grid(row=4, column=0, pady=2)
    label_corrente_limite = Label(interface_tensao, text="Corrente Limite (A):",font=("Times New Roman", 13), bg='lightblue').grid(row=5, column=0, pady=2)

    status_tensao = Label(interface_tensao, text="Status da fonte",font=("Times New Roman", 13), bg='lightblue').grid(row=6, column=0, pady=5)
    output_status = Label(interface_tensao, text=mensagem,font=("Times New Roman", 13), bg='lightblue')
    output_status.grid(row=6, column=1, pady=5)

    # Entrada de dados

    tensao_partida = Entry(interface_tensao,font=("Times New Roman", 18), width=10)
    tensao_partida.grid(row=0, column=1, pady=2,ipady=8)
    tensao_max = Entry(interface_tensao,font=("Times New Roman", 18), width=10)
    tensao_max.grid(row=1, column=1, pady=2,ipady=8)
    acrescimo = Entry(interface_tensao,font=("Times New Roman", 18), width=10)
    acrescimo.grid(row=2, column=1, pady=2,ipady=8)
    tempo_on = Entry(interface_tensao,font=("Times New Roman", 18), width=10)
    tempo_on.grid(row=3, column=1, pady=2,ipady=8)
    tempo_off = Entry(interface_tensao,font=("Times New Roman", 18), width=10)
    tempo_off.grid(row=4, column=1, pady=2,ipady=8)
    corrente_limite = Entry(interface_tensao,font=("Times New Roman", 18), width=10)
    corrente_limite.grid(row=5, column=1, pady=2,ipady=8)

    def enviar():
        try:
            tp = float(tensao_partida.get())
            tm = float(tensao_max.get())
            inc = float(acrescimo.get())
            ton = float(tempo_on.get())
            toff = float(tempo_off.get())
            cl = float(corrente_limite.get())

            output_status.config(text="Enviando...", fg="blue")
            root.update()  # Força atualização da tela  
            minha_fonte.controleTensao(tp, tm, inc, toff, ton, cl)
            output_status.config(text="Concluído!", fg="green")

        except ValueError:
            output_status.config(text="Erro: Use apenas números!", fg="red")
        except Exception as e:
            output_status.config(text=f"Erro: {str(e)}", fg="red")

    def parar():
        minha_fonte.seguranca()
        output_status.config(text="Saida Desligada!", fg="red")

    # Botoes

    botao_enviar = Button(interface_tensao, text="ENVIAR",font=("Times New Roman", 13),command=lambda: threading.Thread(target=enviar).start(), bg="Green", fg="White")
    botao_enviar.grid(row=7, column=0)
    botao_parar = Button(interface_tensao, text="PARAR",font=("Times New Roman", 13),command=parar, bg="Red", fg="White")
    botao_parar.grid(row=7, column=1)

    # Funcoes dos botoes (a definir)

    return chamar_tensao

# Labels Botoes menu

botao_tensao = Button(root, text="Controle de Tensão",font=("Times New Roman", 13),  command=chamar_tensao).pack(expand=True)

root.mainloop()
# Definir condicoes

try:
    minha_fonte.seguranca()
except:
    pass


