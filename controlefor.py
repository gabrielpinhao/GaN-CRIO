import pyvisa
import time
from itertools import count
from medidor import *

rm = pyvisa.ResourceManager()
print(rm.list_resources())

m_volt = NanoVolt('GPIB0::7::INSTR')
m_volt.conectar()
m_volt.configurar_para_pulsos(nplc=1)

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
instrumento.write('VOLT 0.1')
instrumento.write('CURR 0')
instrumento.write('OUTP ON')
time.sleep(1)

# Entradas
try:
    valor_partida = float(input("Digite a corrente de partida (A): "))
    valor_maxima = float(input("Digite a corrente máxima (A): "))
    acrescimo = float(input("Digite o acréscimo (A): "))
except ValueError:
    print("Erro: Digite apenas números.")
    exit()

print("--- INICIANDO TESTE COM FOR INFINITO ---")

try:
    # count(0) gera 0, 1, 2, 3... infinitamente (substitui o range limitado), for mais rapido que while
    for i in count(0):
        inicio = time.perf_counter()
        m_volt.armar_leitura()
        
        # Sua fórmula matemática original (Mais precisa para decimais!)
        atual = (i * acrescimo) + valor_partida
        
        # Arredonda por segurança de display/comando
        atual = round(atual, 4)

        if atual > valor_maxima:
            print(f"Limite {valor_maxima}A atingido. Encerrando rampagem.")
            break

        # APLICAR CORRENTE (LIGA)

        comando_curr = f'CURR {atual}'
        print(f"Corrente atual: {atual}A")

        instrumento.write('VOLT 0.1')
        instrumento.write(comando_curr)
        time.sleep(0.1)  # Aguarda estabilização
        m_volt.disparar_gatilho()
        
        time.sleep(0.1)

        leitura_volts = m_volt.coletar_resultado()
        print(f"Leitura: {leitura_volts:.6e} V")
        # PULSO (ZERO)
        print("Zerando...")

        fim = time.perf_counter()
        print(f"Tempo do ciclo: {fim - inicio:.4f} segundos\n")

         # APLICAR ZERO (DESLIGA)
        instrumento.write('VOLT 0.01')
        instrumento.write('CURR 0.01')
        # hardware.set_current(0)     <--- SEU COMANDO AQUI
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\nPARADA MANUAL!")

except Exception as e:
    print(f"\nERRO: {e}")

finally:
    # SEGURANÇA FINAL (Roda sempre)
    print("\n--- SAFETY: Zerando fonte ---")
    instrumento.write('OUTP OFF')
    print("Zerar valores no instrumento...")
    instrumento.write('VOLT 0')
    instrumento.write('CURR 0')
    instrumento.close()
    m_volt.desconectar()
    print("Fim.")
