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
