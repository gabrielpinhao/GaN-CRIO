import pyvisa
import time
import csv

# 1. Configurações Iniciais
rm = pyvisa.ResourceManager()
ip_yokogawa = "192.168.1.131"  # Seu IP
endereco = f"TCPIP::{ip_yokogawa}::INSTR"
nome_arquivo_csv = "medicao_1s.csv"

scope = None 

try:
    print(f"Tentando conectar a: {endereco}")
    scope = rm.open_resource(endereco)
    
    # Aumentamos o timeout para dar tempo de baixar os dados se a amostragem for alta
    scope.timeout = 30000  
    scope.clear()
    
    print(f"Conectado: {scope.query('*IDN?').strip()}")
    time.sleep(1)

    # Prepara o equipamento
    scope.write(':COMMunicate:HEADer OFF')
    scope.query('*OPC?')

    scope.write(':ACQuire:RLENgth 1000') # Define o comprimento do registro (número de pontos)
    scope.write(':TIMebase:SRATe 1000') # Define a taxa de amostragem (1000 amostras por segundo)
    scope.write(':TRIGger:MODE SINGle')  # Opcional, mas garante que só captura uma vez
    
    # Configura medição de 1 segundo (10 divisões de 0.1s)
    scope.write(':TIMebase:TDIV 0.001')
    scope.query('*OPC?')

    scope.write(':STARt')
    scope.query('*OPC?')
    print("Iniciando aquisição de dados por 1 segundo...")

    scope.write(':STOP')

    scope.write(':COMMunicate:HEADer OFF')

    scope.write(':FILE:DIRectory:DRIVe HD')
    scope.write(':FILE:DIRectory:CDIRectory "Gabriel"')
    scope.write(':FILE:SAVE:ASCii:EXTension CSV')
    scope.write(':FILE:SAVE:ASCii:TINFormation ON')
# 2. (Opcional) Inclui os dados de tempo no arquivo
    scope.write(':FILE:SAVE:ASCii:TINFormation ON')
    scope.write(':FILE:SAVE:NAME "teste_csv"')
    scope.write(':FILE:SAVE:ASCii:EXECute')

    scope.query('*OPC?')
    
    
    

except pyvisa.errors.VisaIOError as e:
    print(f"Erro de comunicação VISA: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
finally:
    if scope is not None:
        scope.close()
        print("Conexão encerrada de forma segura.")
