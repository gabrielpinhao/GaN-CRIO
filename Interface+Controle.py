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
    interface_tensao.geometry("330x350")
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

    status_tensao = Label(interface_tensao, text="Status da fonte",font=("Times New Roman", 13), bg='lightblue').grid(row=5, column=0, pady=5)
    output_status = Label(interface_tensao, text=mensagem,font=("Times New Roman", 13), bg='lightblue')
    output_status.grid(row=5, column=1, pady=5)

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

    def enviar():
        try:
            tp = float(tensao_partida.get())
            tm = float(tensao_max.get())
            inc = float(acrescimo.get())
            ton = float(tempo_on.get())
            toff = float(tempo_off.get())

        except ValueError:
            output_status.config(text="Erro: Use apenas números!", fg="red")
        except Exception as e:
            output_status.config(text=f"Erro: {str(e)}", fg="red")

    def parar():
        minha_fonte.seguranca()
        output_status.config(text="Saida Desligada!", fg="red")

    # Botoes

    botao_enviar = Button(interface_tensao, text="ENVIAR",font=("Times New Roman", 13),command=lambda: threading.Thread(target=enviar).start(), bg="Green", fg="White")
    botao_enviar.grid(row=6, column=0)
    botao_parar = Button(interface_tensao, text="PARAR",font=("Times New Roman", 13),command=parar, bg="Red", fg="White")
    botao_parar.grid(row=6, column=1)

    # Funcoes dos botoes (a definir)

    return chamar_tensao

def chamar_corrente():

    interface_corrente = Toplevel(root)
    interface_corrente.geometry("330x350")
    interface_corrente.title("Controle de Corrente")
    interface_corrente['bg'] = 'lightblue'
    interface_corrente.iconbitmap(r'C:\Users\nitee\Desktop\GaN-CRIO\GaN-CRIO\figura.ico')

    conexaoT = minha_fonte.conectar()

    if conexaoT:
        mensagem = "Instrumento Conectado!"
    else:
        mensagem = "Erro ao conectar"

    # Labels janela corrente

    label_partida = Label(interface_corrente, text="Corrente de Partida (A):",font=("Times New Roman", 13), bg='lightblue').grid(row=0, column=0, pady=2)
    label_corrente_max = Label(interface_corrente, text="Corrente Máxima (A):",font=("Times New Roman", 13), bg='lightblue').grid(row=1, column=0, pady=2)
    label_acrescimo = Label(interface_corrente, text="Acréscimo (A):",font=("Times New Roman", 13), bg='lightblue').grid(row=2, column=0, pady=2)
    label_tempo_on = Label(interface_corrente, text="Time ON (s):",font=("Times New Roman", 13), bg='lightblue').grid(row=3, column=0, pady=2)
    label_tempo_off = Label(interface_corrente, text="Time OFF (s):",font=("Times New Roman", 13), bg='lightblue').grid(row=4, column=0, pady=2)

    frame_status = Label(interface_corrente, text="Status da fonte:",font=("Times New Roman", 13),pady=5, padx=5, bg='lightblue').grid(row=5, column=0)
    output_status = Label(interface_corrente, text=mensagem,font=("Times New Roman", 13), bg='lightblue')
    output_status.grid(row=5, column=1, pady=5)

    # Entrada de dados

    a_partida = Entry(interface_corrente,font=("Times New Roman", 18), width=10)
    a_partida.grid(row=0, column=1, pady=2,ipady=8)
    a_max = Entry(interface_corrente,font=("Times New Roman", 18), width=10)
    a_max.grid(row=1, column=1, pady=2,ipady=8)
    acrescimo = Entry(interface_corrente,font=("Times New Roman", 18), width=10)
    acrescimo.grid(row=2, column=1, pady=2,ipady=8)
    tempo_on = Entry(interface_corrente,font=("Times New Roman", 18), width=10)
    tempo_on.grid(row=3, column=1, pady=2,ipady=8)
    tempo_off = Entry(interface_corrente,font=("Times New Roman", 18), width=10)
    tempo_off.grid(row=4, column=1, pady=2,ipady=8)

    def enviar():
        try:
            valor_a_partida = float(a_partida.get())
            valor_a_max = float(a_max.get())
            valor_acrescimo = float(acrescimo.get())
            valor_tempo_on = float(tempo_on.get())
            valor_tempo_off = float(tempo_off.get())

            # 2. Atualiza status visual
            output_status.config(text="Enviando...", fg="blue")
            root.update()  # Força atualização da tela

            # 3. Manda para a classe da fonte
            # (Adicionei v_tensao aqui pois você tinha capturado mas não enviado no seu código original)
            minha_fonte.controleCorrente(valor_a_partida, valor_a_max, valor_acrescimo, valor_tempo_on, valor_tempo_off)

            output_status.config(text="Concluído!", fg="green")

        except ValueError:
            output_status.config(text="Erro: Use apenas números!", fg="red")
        except Exception as e:
            output_status.config(text=f"Erro: {str(e)}", fg="red")

    def parar():
        minha_fonte.seguranca()
        output_status.config(text="Saida Desligada!", fg="red")

    # Botoes

    botao_enviar = Button(interface_corrente, text="ENVIAR",font=("Times New Roman", 13),bg="Green", fg="White",command=lambda: threading.Thread(target=enviar).start())
    botao_enviar.grid(row=6, column=0)
    botao_parar = Button(interface_corrente, text="PARAR",font=("Times New Roman", 13), bg="Red", fg="White",command=parar)
    botao_parar.grid(row=6, column=1)

    # Funcoes dos botoes (a definir)
    return chamar_corrente

# Labels Botoes menu

botao_tensao = Button(root, text="Controle de Tensão",font=("Times New Roman", 13),  command=chamar_tensao).pack(pady=20, padx=50)
botao_corrente = Button(root, text="Controle de Corrente",font=("Times New Roman", 13), command=chamar_corrente).pack(pady=15, padx=50)

root.mainloop()
# Definir condicoes

try:
    minha_fonte.seguranca()
except:
    pass


