import pyvisa
import time

# --- NOME DIFERENTE PARA CADA ENSAIO, PARA EVITAR SOBRESCRITA DE ARQUIVOS
test_name = "scope_micro" 

# --- Configuração da Fonte de Corren

rm = pyvisa.ResourceManager()
print(rm.list_resources())


#--- Configuração do Servidor ---
remote_folder = "/HD-0/Gabriel"
local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"


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
scope.write(":CHAN8:DISP ON")

# --- Iniciar aquisição ---
try:
    scope.write(":START")
    scope.query('*OPC?')
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


except KeyboardInterrupt: # Cancela o codigo com Ctrl+C
    print("\nMANUAL STOP!")

except Exception as e:
    print(f"\nERROR: {e}")

finally: # Zera a fonte, desconecta instrumentos e encerra conexões
        print("THE END.")