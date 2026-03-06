import pyvisa
import time

# --- Configuração da Fonte de Corrente ---
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

try:
    corrente_limite = 250
    ton = 0.02
    toff = 5
    amplitude = 0.25

    instrumento.write(f'CURR {corrente_limite}')
    print(f"Current limit of {corrente_limite} A.")
    time.sleep(1)# Pequena pausa para garantir que a fonte esteja pronta

except ValueError:
    print("INPUT ERROR.")
    exit()

# --- Configuração do Osciloscópio ---
scope = rm.open_resource("TCPIP0::192.168.1.131::INSTR")
scope.timeout = 60000  # aquisições grandes
scope.clear()
scope.write("*CLS")

scope.write(":TRIGger:MODE AUTO")
scope.write(":ACQuire:RLENgth 5000")   # 5000 pontos
scope.write(":TIMebase:SRATe 100000")  # 100 kSa/s
scope.write(f':TIMebase:TDIV 0.02')
scope.write(":CHAN7:DISP ON")
scope.write(":CHAN8:DISP ON")

# --- Iniciar aquisição ---

scope.write(":START")
scope.query('*OPC?')
instrumento.write(f'VOLT {amplitude}')
time.sleep(ton)  # Tempo ON

instrumento.write('VOLT 0')
scope.write(":STOP")
scope.query('*OPC?')

start_time = time.time()

#--- Configuração de arquivo CSV ---
scope.write(':FILE:DIRectory:DRIVe HD')
scope.write(':FILE:DIRectory:CDIRectory "Gabriel"')

scope.write(':FILE:SAVE:ASCii:EXTension CSV')
scope.write(':FILE:SAVE:ASCii:TINFormation ON')
scope.write(':FILE:SAVE:NAME "caruso_csv"')

scope.query('*OPC?')

scope.write(':FILE:SAVE:ASCii:EXECute')
scope.query('*OPC?')  # aguarda gravação completa

end_time = time.time()  # marca o tempo de fim

if (end_time - start_time) < toff: time.sleep(toff - (end_time - start_time))

# --- Print do tempo total ---
print(f"Tempo total de execução: {end_time - start_time:.3f} segundos")
print("Arquivo salvo com sucesso no equipamento.")