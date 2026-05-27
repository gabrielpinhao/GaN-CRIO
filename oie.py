import tkinter as tk
import serial
import time

# --- CONFIGURAÇÃO DA PORTA SERIAL ---
# Mude 'COM3' para a porta onde seu ESP32 está conectado!
PORTA_COM = 'COM6' 
VELOCIDADE = 115200

try:
    # Conecta ao ESP32
    esp32 = serial.Serial(PORTA_COM, VELOCIDADE)
    time.sleep(2) # Dá um tempinho para o ESP32 reiniciar após conectar
    print("Conectado ao ESP32 com sucesso!")
except Exception as e:
    print(f"Erro ao conectar na porta {PORTA_COM}. O cabo está ligado?")
    print(f"Erro detalhado: {e}")
    exit()

# --- FUNÇÕES DOS BOTÕES ---
def pulso():
    esp32.write(b'1') # Envia o caractere '1' em formato de byte
    print("Comando pulso enviado.")

def desligar():
    esp32.write(b'0') # Envia o caractere '0' em formato de byte
    print("Comando DESLIGAR esp32 enviado.")

def ligar_esp32():
    esp32.write(b'2') # Envia o caractere '2' para ligar o ESP32 estado alto
    print("Comando LIGAR ESP32 enviado.")

# --- INTERFACE GRÁFICA (TKINTER) ---
janela = tk.Tk()
janela.title("Controle do ESP32")
janela.geometry("300x200")
janela.eval('tk::PlaceWindow . center') # Centraliza a janela

# Título
label_titulo = tk.Label(janela, text="Controle esp32", font=("Arial", 14, "bold"))
label_titulo.pack(pady=15)


btn_ligar = tk.Button(janela, text="Ligar esp32", bg="black", fg="white", font=("Arial", 12), width=15, command=ligar_esp32)
btn_ligar.pack(pady=5)
# Botão Ligar - Adicionado command=ligar
btn_ligar = tk.Button(janela, text="pulso", bg="green", fg="white", font=("Arial", 12), width=15, command=pulso)
btn_ligar.pack(pady=5)

# Botão Desligar - Adicionado command=desligar
btn_desligar = tk.Button(janela, text="Parar LED", bg="red", fg="white", font=("Arial", 12), width=15, command=desligar)
btn_desligar.pack(pady=5)

# Inicia o programa
janela.mainloop()