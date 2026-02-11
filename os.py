import pyvisa
import csv
import time


# 1. Configurar o Gerenciador de Recursos
rm = pyvisa.ResourceManager()
ip_yokogawa = "192.168.1.131"  # Seu IP
endereco = f"TCPIP::{ip_yokogawa}::INSTR"

scope = None # Inicializa variável para segurança no finally

try:
    print(f"Tentando conectar a: {endereco}")
    scope = rm.open_resource(endereco)
    scope.timeout = 30000  # 30 segundos
    scope.clear()  # Limpa buffer
    print(f"Conectado: {scope.query('*IDN?').strip()}")

    # Medição
    scope.write(':COMMunicate:HEADer OFF')  # Desliga cabeçalhos
    scope.write(':STOP')  # Garante que está parado
    scope.query('*OPC?')  # Espera confirmação de parada
    scope.write(':WAVeform:TRACe 9')  # Canal 9
    time.sleep(1)  # Pequena pausa para garantir comando processado
    scope.write(':START')  # Inicia captura
    scope.query('*OPC?')  # Espera confirmação de início
    time.sleep(1)  # Espera física para encher a memória
    scope.write(':STOP')  # Para captura
    scope.query('*OPC?')  # Espera confirmação de parada


finally:
    if scope:
        scope.close()
        print("Conexão fechada.")
    rm.close()