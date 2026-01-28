
from datetime import datetime
import pyvisa
import time
from itertools import count
from medidor import *
from Agilent import *

rm = pyvisa.ResourceManager()
print(rm.list_resources())

m_volt = NanoVolt('GPIB0::7::INSTR')
m_volt.conectar()
m_volt.configurar_para_pulsos(nplc=1)

# Conectar medidor Agilent 34401A
a_volt = Agilent34401A('GPIB0::8::INSTR')
a_volt.conectar()
a_volt.configurar_para_pulsos(nplc=1)

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
        m_volt.armar_leitura()
        a_volt.armar_leitura()
        
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
        a_volt.disparar_gatilho()
        time.sleep(0.1)

        leitura_volts = m_volt.coletar_resultado()
        leitura_volts_agilent = a_volt.coletar_resultado()
        corrente_lida_shunt = leitura_volts/0.00012
        print(f"Leitura NanoVolt: {leitura_volts:.6e} V")
        print(f"Leitura do NanoVolt: {corrente_lida_shunt} A.")

        print(f"Leitura Agilent: {leitura_volts_agilent:.6e} V")
        fim = time.perf_counter()
        tempo_ciclo = fim - inicio

        # ### NOVO: Salvar linha no CSV ###
        # Preparamos a lista de dados desta linha
        linha_dados = [
            i,                                          # Iteração
            datetime.now().strftime('%H:%M:%S.%f'),     # Hora exata
            atual,                                      # Corrente que enviamos
            leitura_volts,                              # Leitura crua Nano
            corrente_lida_shunt,                        # Corrente calculada
            leitura_volts_agilent,                      # Leitura Agilent
            f"{tempo_ciclo:.4f}"                        # Tempo que levou
        ]
        linha = '\t'.join(map(str, linha_dados)) + '\n'
        arquivo_txt.write(linha)

        # Flush força a gravação no disco imediatamente (bom se o programa travar, não perde dados)
        arquivo_txt.flush() 
        # ###############################

        # PULSO (ZERO)
        print("Zerando...")


        print(f"Tempo do ciclo: {tempo_ciclo:.4f} segundos\n")

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
    # 1. Tenta fechar o arquivo CSV
    try:
        arquivo_txt.close()
        print(f"Arquivo TXT '{nome_arquivo}' salvo com sucesso.")
    except:
        print("Erro ao fechar arquivo TXT (ou não foi criado).")
    # 2. Zera a fonte e desconecta instrumentos
    print("\n--- SAFETY: Zerando fonte ---")
    instrumento.write('OUTP OFF')
    print("Zerar valores no instrumento...")
    instrumento.write('VOLT 0')
    instrumento.write('CURR 0')
    instrumento.close()
    m_volt.desconectar()
    a_volt.desconectar()
    print("Fim.")
