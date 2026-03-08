import csv
import pyvisa
import time
from YOKOclass import YokogawaDL850

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