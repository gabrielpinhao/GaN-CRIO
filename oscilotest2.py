import pyvisa
import time
from osciloscopio import *

osciloscopio = YokogawaDL850(ip_address="192.168.1.131")

osciloscopio.conectar()
osciloscopio.configurar_aquisicao(record_length=10000, sample_rate=10000, time_div=0.1, trigger="SINGLE")
osciloscopio.measure_start()
osciloscopio.measure_stop()
osciloscopio.salvar_csv(nome_arquivo="medicao_1s")

# rm = pyvisa.ResourceManager()
# print(rm.list_resources())

# scope = rm.open_resource("TCPIP0::192.168.1.131::INSTR")
# scope.timeout = 60000  # aquisições grandes



# scope.clear()
# scope.write("*CLS")

# # --- Configuração de aquisição ---
# scope.write(":TRIGger:MODE AUTO")
# scope.write(":ACQuire:RLENgth 100000")
# scope.write(":TIMebase:SRATe 100000")
# scope.write(":CHAN7:DISP ON")
# scope.write(":CHAN8:DISP ON")

# # --- Iniciar aquisição ---
# print("START")
# scope.write(":START")

# # --- Esperar aquisição terminar ---
# print("STOP")
# scope.write(":STOP")
# scope.query('*OPC?')  

# # --- Configuração de arquivo CSV ---
# scope.write(':FILE:DIRectory:DRIVe HD')
# scope.write(':FILE:DIRectory:MDIRectory "Gabriel"')
# scope.write(':FILE:DIRectory:CDIRectory "Gabriel"')

# scope.write(':FILE:SAVE:ASCii:EXTension CSV')
# scope.write(':FILE:SAVE:ASCii:TINFormation ON')
# scope.write(':FILE:SAVE:ASCii:TRACE 7,8')   # indicar quais canais salvar
# scope.write(':FILE:SAVE:NAME "teste_csv"')

# # --- Forçar DL850EV a “preparar os dados” ---
# scope.write(':FILE:SAVE:ASCii:PREPARE')  # step crítico: prepara header e dados
# scope.query('*OPC?')                     # aguarda terminar

# # --- Executar salvamento ---
# scope.write(':FILE:SAVE:ASCii:EXECute')
# scope.query('*OPC?')  # aguarda gravação completa

# print("Arquivo salvo com sucesso no equipamento.")