import pyvisa
import time

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
instrumento.write('VOLT 0.1')
instrumento.write('CURR 0')
set_curr = instrumento.query('CURR?')
set_volt = instrumento.query('VOLT?')
instrumento.write('OUTP ON')
time.sleep(1)

#Variáveis de Controle
corrente_inicial = 0.0
incremento = 1.0
corrente_maxima = 20.0
corrente_atual = corrente_inicial

try:
    while True:
        #Ponto de Parada (Break Condition)
        if corrente_atual > corrente_maxima:
            print(f"Corrente máxima de {corrente_maxima}A atingida. Encerrando o ciclo de testes.")
            break
            
        #Conversão para String
        comando_curr = f'CURR {corrente_atual}'

        print(f"Configurando Tensão: 1V | Corrente: {corrente_atual}A")

        instrumento.write('VOLT 1')
        instrumento.write(comando_curr)  # Usa o valor incrementado
        time.sleep(0.3)

        #Incremento para a próxima iteração
        corrente_atual += incremento

        #Bloco de Reset (Zera dentro do ciclo) ---
        instrumento.write('VOLT 0.01')
        instrumento.write('CURR 0.01')
        time.sleep(0.3)

except KeyboardInterrupt:
    print("\nInterrupção detectada. Prosseguindo para zerar os valores...")

finally:
    #Rotina de segurança
    #Desligar Saída
    instrumento.write('OUTP OFF')
    print("Zerar valores no instrumento...")
    instrumento.write('VOLT 0')
    instrumento.write('CURR 0')

    #instrumento.close()
    print("Execução finalizada e instrumento zerado.")
