#------------- controle_tensao ---------------#

import csv
from datetime import datetime
import pyvisa
import time
from itertools import count

rm = pyvisa.ResourceManager()
print(rm.list_resources())

try:
    instrumento = rm.open_resource('GPIB0::1::INSTR')
    instrumento.timeout = 5000
    print("Conexao Sucedida")
except pyvisa.VisaIOError:
    print("Falha na Conexao")
    exit()

ident = instrumento.query('*IDN?')
print(f'Identificacao do instrumento: {ident}')
instrumento.write('*RST')
instrumento.write('VOLT 0')
instrumento.write('CURR 0')
instrumento.write('OUTP ON')
time.sleep(1)

# Entradas
try:
    valor_partida = 0
    #corrente_limite = float(input("Digite a corrente limite (A): "))
    #valor_maxima = float(input("Digite a tensao máxima (V): "))
    #acrescimo = float(input("Digite o acréscimo (V): "))
    #ton = float(input("Digite o tempo ON (s): "))
    #toff = float(input("Digite o tempo OFF (s): "))

    corrente_limite = 150
    valor_maxima = 3
    acrescimo = 0.2
    ton = 0.02
    toff = 1.78

except ValueError:
    print("Erro: Digite apenas números.")
    exit()

print("--- INICIANDO TESTE COM FOR INFINITO ---")

try:
    instrumento.write(f'CURR {corrente_limite}')
    # count(0) gera 0, 1, 2, 3... infinitamente (substitui o range limitado), for mais rapido que while (em C)
    for i in count(0):
        inicio = time.perf_counter()
        
        # Sua fórmula matemática original (Mais precisa para decimais!)
        atual = (i * acrescimo) + valor_partida
        
        # Arredonda por segurança de display/comando
        atual = round(atual, 4)

        if atual > valor_maxima or atual > 5.0:
            print(f"Limite {valor_maxima}V atingido. Encerrando rampagem.")
            break

        # APLICAR CORRENTE (LIGA)

        comando_tensao = f'VOLT {atual}' # controle TENSão
        print(f"Tensão atual: {atual}V")

        instrumento.write(comando_tensao)
        

        time.sleep(ton)  # Tempo ON

        fim = time.perf_counter()
        tempo_ciclo = fim - inicio

        # PULSO (ZERO)
        print("Zerando...")


        print(f"Tempo do ciclo: {tempo_ciclo:.4f} segundos\n")

         # APLICAR ZERO (DESLIGA)
        instrumento.write('VOLT 0')
        # hardware.set_current(0)     <--- SEU COMANDO AQUI
        
        time.sleep(toff) # Tempo OFF
    instrumento.write('CURR 0')

except KeyboardInterrupt: # Cancela o codigo com Ctrl+C
    print("\nPARADA MANUAL!")

except Exception as e:
    print(f"\nERRO: {e}")

finally:

    # 2. Zera a fonte e desconecta instrumentos
    print("\n--- SAFETY: Zerando fonte ---")
    instrumento.write('OUTP OFF')
    print("Zerar valores no instrumento...")
    instrumento.write('VOLT 0')
    instrumento.write('CURR 0')
    instrumento.close()
    print("Fim.")

#------------- fonteobjeto ---------------#

import pyvisa
import time
from itertools import count

#Criar a classe para importamos na interface depois
class Fonte:
    def __init__(self,endereco_gpib): #colocar endereco gpib
        self.rm = pyvisa.ResourceManager()
        self.endereco = endereco_gpib
        self.instrumento = None

    def conectar(self):
        try:
            self.instrumento = self.rm.open_resource(self.endereco)
            self.instrumento.timeout = 5000
            return True
        except pyvisa.VisaIOError:
            return False

# funçao de teste não funciona, verificar porque depois
    def teste(self):

        try:
            ident = self.instrumento.query('*IDN?')
            self.instrumento.write('*RST')
            self.instrumento.write('OUTP ON')
            self.instrumento.write('VOLT 0.1')
            self.instrumento.write('CURR 0')
            time.sleep(3)
            self.instrumento.write('VOLT 0.1')
            self.instrumento.write('CURR 1')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            time.sleep(3)

        finally:
            self.instrumento.write('OUTP OFF')
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')
            print("Zerar valores no instrumento...")
            # instrumento.close()
            print("Execução finalizada e instrumento zerado.")

    def controleCorrente(self, corrente_partida, corrente_maxima, acrescimo, ton,toff):

        tempo_on = float(ton)
        tempo_off = float(toff)

        try:

            ident = self.instrumento.query('*IDN?')
            self.instrumento.write('*RST')
            self.instrumento.write('VOLT 3.0')
            self.instrumento.write('CURR 0.01')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            self.instrumento.write('OUTP ON')
            time.sleep(1)


            for i in count(0):

                inicio = time.perf_counter()
        
                # Sua fórmula matemática original (Mais precisa para decimais!)
                atual = (i * acrescimo) + corrente_partida
                
                # Arredonda por segurança de display/comando
                atual = round(atual, 4)

                if atual > corrente_maxima:
                    print(f"Limite {corrente_maxima}A atingido. Encerrando rampagem.")
                    break

                # APLICAR CORRENTE (LIGA)

                comando_curr = f'CURR {atual}'
                print(f"Corrente atual: {atual}A")

                self.instrumento.write('VOLT 3.0')
                self.instrumento.write(comando_curr)
                
                time.sleep(ton)

                # PULSO (ZERO)
                print("Zerando...")

                fim = time.perf_counter()
                print(f"Tempo do ciclo: {fim - inicio:.4f} segundos\n")

                # APLICAR ZERO (DESLIGA)
                self.instrumento.write('VOLT 3.0')
                self.instrumento.write('CURR 0.01')
                # hardware.set_current(0)     <--- SEU COMANDO AQUI
                
                time.sleep(toff)

        except KeyboardInterrupt:
            print("\nInterrupção detectada. Prosseguindo para zerar os valores...")
        
        except Exception as e:
            print(f"\nERRO: {e}")

        finally:
            # Rotina de segurança
            # Desligar Saída
             # SEGURANÇA FINAL (Roda sempre)
            print("\n--- SAFETY: Zerando fonte ---")
            self.instrumento.write('OUTP OFF')
            print("Zerar valores no instrumento...")
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')
            self.instrumento.close()
            print("Fim.")
            print("Execução finalizada e instrumento zerado.")

    def controleTensao(self, tensao_partida, tensao_maxima, acrescimo, toff,ton, corrente_limite):

        tempo_on = float(ton)
        tempo_off = float(toff)

        try:
            ident = self.instrumento.query('*IDN?')
            self.instrumento.write('*RST')
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            self.instrumento.write('OUTP ON')
            time.sleep(1)

            self.instrumento.write(f'CURR {corrente_limite}')
            
            for i in count(0):
                inicio = time.perf_counter()
        
        # Sua fórmula matemática original (Mais precisa para decimais!)
                atual = (i * acrescimo) + tensao_partida
        
        # Arredonda por segurança de display/comando
                atual = round(atual, 4)

                if atual > tensao_maxima or atual > 5.0:
                    print(f"Limite {tensao_maxima}V atingido. Encerrando rampagem.")
                    break

                # APLICAR CORRENTE (LIGA)

                comando_tensao = f'VOLT {atual}' # controle Tensão
                print(f"Tensão atual: {atual}V")

                self.instrumento.write(comando_tensao)

                time.sleep(ton)  # Tempo ON

                fim = time.perf_counter()
                tempo_ciclo = fim - inicio

                # PULSO (ZERO)
                print("Zerando...")


                print(f"Tempo do ciclo: {tempo_ciclo:.4f} segundos\n")

                # APLICAR ZERO (DESLIGA)
                self.instrumento.write('VOLT 0')
                # hardware.set_current(0)     <--- SEU COMANDO AQUI
                
                time.sleep(toff) # Tempo OFF
                
            self.instrumento.write('CURR 0')



        except KeyboardInterrupt:
            print("\nInterrupção detectada. Prosseguindo para zerar os valores...")

        finally:
            # Rotina de segurança
            # Desligar Saída
            self.instrumento.write('OUTP OFF')
            print("Zerar valores no instrumento...")
            self.instrumento.write('VOLT 3.0')
            self.instrumento.write('CURR 0')

            # instrumento.close()
            print("Execução finalizada e instrumento zerado.")

    def seguranca(self):

        self.instrumento.write('OUTP OFF')
        self.instrumento.write('VOLT 0')
        self.instrumento.write('CURR 0')
        self.instrumento.close()

#------------- Interface+Controle ---------------#

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


#------------- os_notebook ---------------#

import pyvisa
import pandas as pd
import time
import re 
import os # Necessário para criar a pasta e manipular os caminhos
from DCestimator import *

def capturar_para_pc(canal=1, nome_arquivo="medicao_direta.csv"):
    """
    Puxa os dados da memória do osciloscópio Yokogawa DL850E via rede 
    e salva o CSV na pasta especificada.
    """
    rm = pyvisa.ResourceManager()
    ip_yokogawa = "192.168.1.131" 
    endereco = f"TCPIP::{ip_yokogawa}::INSTR"
    
    scope = None
    try:
        scope = rm.open_resource(endereco)
        scope.timeout = 60000  # Timeout alto para transferências ASCII longas
        
        # 1. Garante que o equipamento não envie cabeçalhos nas respostas
        scope.write(':COMMunicate:HEADer OFF')
        
        print(f"Transferindo dados do canal {canal}...")
        
        # 2. Seleciona o canal e o formato de transmissão
        scope.write(f':WAVeform:TRACe {canal}')
        scope.write(':WAVeform:FORMat ASCii')
        
        # 3. Coleta parâmetros reais do Yokogawa para reconstruir o Eixo X (Tempo)
        sample_rate = float(scope.query(':WAVeform:SRATe?'))
        x_incr = 1.0 / sample_rate
        
        trig_pos_points = int(scope.query(':WAVeform:TRIGger?'))
        x_start = -(trig_pos_points * x_incr)
        
        # 4. Solicita os dados brutos de tensão (Eixo Y)
        scope.write(':WAVeform:SEND?')
        
        dados_brutos = scope.read_raw()
        dados_texto = dados_brutos.decode('ascii', errors='ignore')
        
        pedacos = dados_texto.strip().split(',')
        valores_y = []
        
        for pedaco in pedacos:
            try:
                if pedaco.strip(): 
                    valores_y.append(float(pedaco))
            except ValueError:
                numeros = re.findall(r"[-+]?\d*\.\d+[eE]?[-+]?\d*|[-+]?\d+", pedaco)
                if numeros:
                    valores_y.append(float(numeros[-1]))
        
        # 5. Reconstrói matematicamente o eixo do tempo
        valores_x = [x_start + (i * x_incr) for i in range(len(valores_y))]
        
        # ==========================================================
        # 6. Prepara o caminho exato fornecido
        # Usamos o 'r' na frente da string para que o Python entenda as barras (\) corretamente
        # ==========================================================
        pasta_destino = r"C:\Users\nitee\Desktop\GaN-CRIO\Teste"
        
        # Cria a pasta caso ela ainda não exista no seu computador
        os.makedirs(pasta_destino, exist_ok=True)
        
        # Junta o caminho da pasta com o nome do arquivo (ex: medicao_direta.csv)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        
        # 7. Salva usando Pandas no caminho completo
        df = pd.DataFrame({'Tempo (s)': valores_x, 'Tensao (V)': valores_y})
        
        df.to_csv(caminho_completo, index=False)
        print(f"Sucesso! {len(valores_y)} pontos salvos em: {caminho_completo}")

    except Exception as e:
        print(f"Erro na captura: {e}")
    finally:
        if scope:
            scope.close()

# Executar a função
capturar_para_pc(canal=9)

#------------- os ---------------#

import pyvisa
import time
import csv

# 1. Configurações Iniciais
rm = pyvisa.ResourceManager()
ip_yokogawa = "192.168.1.131"  # Seu IP
endereco = f"TCPIP::{ip_yokogawa}::INSTR"
nome_arquivo_csv = "medicao_1s.csv"

scope = None 

try:
    print(f"Tentando conectar a: {endereco}")
    scope = rm.open_resource(endereco)
    
    # Aumentamos o timeout para dar tempo de baixar os dados se a amostragem for alta
    scope.timeout = 30000  
    scope.clear()
    
    print(f"Conectado: {scope.query('*IDN?').strip()}")
    time.sleep(1)

    # Prepara o equipamento
    scope.write(':COMMunicate:HEADer OFF')
    scope.query('*OPC?')

    scope.write(':ACQuire:RLENgth 1000') # Define o comprimento do registro (número de pontos)
    scope.write(':TIMebase:SRATe 1000') # Define a taxa de amostragem (1000 amostras por segundo)
    scope.write(':TRIGger:MODE SINGle')  # Opcional, mas garante que só captura uma vez
    
    # Configura medição de 1 segundo (10 divisões de 0.1s)
    scope.write(':TIMebase:TDIV 0.001')
    scope.query('*OPC?')

    scope.write(':STARt')
    scope.query('*OPC?')
    print("Iniciando aquisição de dados por 1 segundo...")

    scope.write(':STOP')

    scope.write(':COMMunicate:HEADer OFF')

    scope.write(':FILE:DIRectory:DRIVe HD')
    scope.write(':FILE:DIRectory:CDIRectory "Gabriel"')
    scope.write(':FILE:SAVE:ASCii:EXTension CSV')
    scope.write(':FILE:SAVE:ASCii:TINFormation ON')
# 2. (Opcional) Inclui os dados de tempo no arquivo
    scope.write(':FILE:SAVE:ASCii:TINFormation ON')
    scope.write(':FILE:SAVE:NAME "teste_csv"')
    scope.write(':FILE:SAVE:ASCii:EXECute')

    scope.query('*OPC?')
    
    
    

except pyvisa.errors.VisaIOError as e:
    print(f"Erro de comunicação VISA: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
finally:
    if scope is not None:
        scope.close()
        print("Conexão encerrada de forma segura.")

#------------- plot ---------------#

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

#------------- pulso_simples ---------------#

import csv
import pyvisa
import time
from ClassYOKO import YokogawaDL850

rm = pyvisa.ResourceManager()
print(rm.list_resources())

try:
    instrumento = rm.open_resource('GPIB0::1::INSTR')
    instrumento.timeout = 5000
    print("Conexao Sucedida")
except pyvisa.VisaIOError:
    print("Falha na Conexao")
    exit()

ident = instrumento.query('*IDN?')
print(f'Identificacao do instrumento: {ident}')
instrumento.write('*RST')
instrumento.write('VOLT 0')
instrumento.write('CURR 0')
instrumento.write('OUTP ON')
time.sleep(1)

# Entradas
try:
    corrente_limite = 150
    ton = 0.02
    toff = 1.78
    amplitude = 0.2

    instrumento.write(f'CURR {corrente_limite}')
    print(f"Current limit of {corrente_limite} A.")
    time.sleep(1)# Pequena pausa para garantir que a fonte esteja pronta

except ValueError:
    print("INPUT ERROR.")
    exit()

try:
    print(f"Measurement Started!")

    instrumento.write(f'VOLT {amplitude}')
    print(f"Applying {amplitude}V.")
    
    time.sleep(ton)  # Tempo ON

    instrumento.write('VOLT 0')
    print(f"Applying 0V.")

  
    time.sleep(toff) # Tempo OFF

    print(f"Measurement Stopped!")  # Para a captura no osciloscópio

    #scope_pulso.salvar_csv(nome_arquivo="pulso_simples")
    instrumento.write('CURR 0')

except KeyboardInterrupt: # Cancela o codigo com Ctrl+C
    print("\nPARADA MANUAL!")

except Exception as e:
    print(f"\nERRO: {e}")

finally: # 2. Zera a fonte e desconecta instrumentos
    print("\n--- SAFETY: Zerando fonte ---")
    instrumento.write('OUTP OFF')
    print("Zerar valores no instrumento...")
    instrumento.write('VOLT 0')
    instrumento.write('CURR 0')
    #scope_pulso.desconectar()
    instrumento.close()
    print("Fim.")

#------------- main ---------------#

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
