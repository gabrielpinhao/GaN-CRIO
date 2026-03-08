import pyvisa
import time
from FTPDownloader import *
from DCestimator import *

# --- NOME DIFERENTE PARA CADA ENSAIO, PARA EVITAR SOBRESCRITA DE ARQUIVOS
test_name = "CARUSO_NOVO" 

# --- Configuração da Fonte de Corrente ---
corrente_limite = 250
ton = 0.02
toff = 5
amplitude = 0.25

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
    instrumento.write(f'CURR {corrente_limite}')
    print(f"Current limit of {corrente_limite} A.")
    time.sleep(1)# Pequena pausa para garantir que a fonte esteja pronta

except ValueError:
    print("INPUT ERROR.")
    exit()

# --- Configuração do Servidor ---
remote_folder = "/HD-0/Gabriel"
local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"

try:
    downloader = FTPDownloader()
    downloader.connect()
    create_local_folder(local_folder, test_name)
except Exception as e:
    print(f"Erro ao conectar via FTP: {e}")
    exit()

# --- Configuração do Osciloscópio ---
try:
    scope = rm.open_resource("TCPIP0::192.168.1.131::INSTR")
    scope.timeout = 60000  # aquisições grandes
    scope.clear()
    scope.write("*CLS")

except pyvisa.VisaIOError:
    print("Falha na Conexao com o Osciloscopio")
    exit()

scope.write(":TRIGger:MODE AUTO")
scope.write(":ACQuire:RLENgth 5000")   # 5000 pontos
scope.write(":TIMebase:SRATe 100000")  # 100 kSa/s
scope.write(f':TIMebase:TDIV 0.02')
scope.write(":CHAN7:DISP ON")
scope.write(":CHAN8:DISP ON")

# --- Iniciar aquisição ---
try:
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
    scope.write(f':FILE:SAVE:NAME "{test_name}"')

    scope.query('*OPC?')

    scope.write(':FILE:SAVE:ASCii:EXECute')
    scope.query('*OPC?')  # aguarda gravação completa

    latest_file = downloader.download_latest_file(test_name, remote_folder, local_folder)

    df = single_csv_to_df(f"{local_folder}/{test_name}/{latest_file}")
    time_plot(df)

    end_time = time.time()  # marca o tempo de fim
    if (end_time - start_time) < toff: time.sleep(toff - (end_time - start_time))

except KeyboardInterrupt: # Cancela o codigo com Ctrl+C
    print("\nMANUAL STOP!")

except Exception as e:
    print(f"\nERROR: {e}")

finally: # Zera a fonte, desconecta instrumentos e encerra conexões
        instrumento.write('OUTP OFF')
        instrumento.write('VOLT 0')
        instrumento.write('CURR 0')
        instrumento.close()
        downloader.close()
        print("THE END.")