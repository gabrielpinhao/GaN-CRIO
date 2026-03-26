import pyvisa
import time

# --- NOME DIFERENTE PARA CADA ENSAIO, PARA EVITAR SOBRESCRITA DE ARQUIVOS
test_name = "scope_micro_100MS" 

rm = pyvisa.ResourceManager()

# --- Configuração do Osciloscópio ---
try:
    # Ajuste o endereço IP se necessário
    scope = rm.open_resource("TCPIP0::192.168.1.131::INSTR")
    scope.timeout = 60000  
    scope.clear()
    scope.write("*CLS")
    
    # Desativa cabeçalhos para facilitar leituras de consulta
    scope.write(':COMMunicate:HEADer OFF') 

except pyvisa.VisaIOError:
    print("Falha na Conexao com o Osciloscopio")
    exit()

# --- Configurações de Aquisição solicitadas ---
# 1. Modo de Trigger: Single
scope.write(":TRIGger:MODE SINGle") 
# 2. Taxa de Amostragem: 100 Mega Samples por segundo (100MA ou 100E+06)
scope.write(":TIMebase:SRATe 100MA") 

# 3. Tempo por Divisão: 5 microsegundos (5US ou 5E-06)
scope.write(":TIMebase:TDIV 5US") 

# 4. Record Length: 
# Com 100 MS/s e 5us/div (total de 50us na tela), 5000 pontos capturam exatamente a tela cheia.
scope.write(":ACQuire:RLENgth 5000") 

scope.write(":CHAN7:DISP ON") 
scope.query('*OPC?')

# --- Iniciar aquisição ---
try:
    print("Aguardando trigger (Modo Single)...")
    scope.write(":STARt") 

    # Sincronização: Aguarda o Bit 0 (Capture) do registro de condição se tornar 0
    # Isso garante que o equipamento só avance quando a captura Single terminar
    capturando = True
    while capturando:
        status = int(scope.query(':STATus:CONDition?')) 
        if not (status & 1): # Bit 0 é 'Capture'
            capturando = False
        time.sleep(0.01)

    print("Captura finalizada. Salvando arquivo...")

    #--- Configuração de arquivo CSV no instrumento ---
    scope.write(':FILE:DIRectory:DRIVe HD') 
    scope.write(':FILE:DIRectory:CDIRectory "Gabriel"') 

    scope.write(':FILE:SAVE:ASCii:EXTension CSV') 
    scope.write(':FILE:SAVE:ASCii:TINFormation ON') 
    scope.write(f':FILE:SAVE:NAME "{test_name}"') 

    # Comando crucial para executar o salvamento em ASCII/CSV
    scope.write(':FILE:SAVE:ASCii:EXECute') 
    scope.query('*OPC?')  # Aguarda a gravação física no HD terminar

    print(f"Sucesso! Arquivo '{test_name}.csv' salvo no HD do osciloscópio.")

except KeyboardInterrupt:
    print("\nPARADA MANUAL!")
    scope.write(":STOP") 

except Exception as e:
    print(f"\nERRO: {e}")

finally:
    if 'scope' in locals():
        scope.close()
    print("Conexão encerrada. FIM.")