import csv
import pyvisa
import time
from osciloscopio import YokogawaDL850



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
    ton = 0.02
    toff = 1.78
    amplitude = 0.2

except ValueError:
    print("Erro: Digite apenas números.")
    exit()

print("--- INICIANDO TESTE COM FOR INFINITO ---")

try:
    #tirei aplicção de corrente
    instrumento.write(f'CURR {corrente_limite}')

    print(f"Aplicando tensão crescente com limite de {amplitude}V...")
    time.sleep(2)  # Pequena pausa para garantir que a fonte esteja pronta
    comando_tensao = f'VOLT {amplitude}' # controle TENSão
    print(f"Tensão atual: {amplitude}V")

    instrumento.write(comando_tensao)
        

    time.sleep(ton)  # Tempo ON


    # PULSO (ZERO)
    print("Zerando...")



         # APLICAR ZERO (DESLIGA)
    instrumento.write('VOLT 0')
    # hardware.set_current(0)     <--- SEU COMANDO AQUI
        
    time.sleep(toff/2) # Tempo OFF




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