
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
instrumento.write('VOLT 5.0')
instrumento.write('CURR 0')
instrumento.write('OUTP ON')
time.sleep(1)

# Entradas
try:
    valor_partida = 0
    valor_maxima = float(input("Digite a corrente máxima (A): "))
    acrescimo = float(input("Digite o acréscimo (A): "))
except ValueError:
    print("Erro: Digite apenas números.")
    exit()


# ### NOVO: Configuração do Arquivo TXT ###
# Gera nome único com data e hora para não sobrescrever testes anteriores
nome_arquivo = f"teste_pulso_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
print(f"Salvando dados em: {nome_arquivo}")

# Abrimos o arquivo aqui. 'newline=''' é importante no Windows para não pular linhas extras
arquivo_txt = open(nome_arquivo, mode='w', newline='') 
arquivo_txt.write('Iteracao\tTimestamp\tCorrente_Set (A)\tNanoVolt (V)\tCorrente_Calculada (A)\tAgilent (V)\tTempo_Ciclo (s)\n')

# #######################################

print("--- INICIANDO TESTE COM FOR INFINITO ---")

try:
    # count(0) gera 0, 1, 2, 3... infinitamente (substitui o range limitado), for mais rapido que while (em C)
    for i in count(0):
        inicio = time.perf_counter()
        
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

        instrumento.write('VOLT 5.0')
        instrumento.write(comando_curr)
        time.sleep(1.5)  # ton

        fim = time.perf_counter()
        tempo_ciclo = fim - inicio

        # PULSO (ZERO)
        print("Zerando...")

        print(f"Tempo do ciclo: {tempo_ciclo:.4f} segundos\n")

         # APLICAR ZERO (DESLIGA)
        instrumento.write('VOLT 5.0')
        instrumento.write('CURR 0.01')
        # hardware.set_current(0)     <--- SEU COMANDO AQUI
        
        time.sleep(18.2) #off

except KeyboardInterrupt:
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
