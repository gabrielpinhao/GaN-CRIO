import pyvisa
import time

class YokogawaDL850:
    def __init__(self, ip_address, timeout=60000): # Timeout aumentado para operações de disco
        """
        Inicializa as configurações básicas de conexão com o equipamento.
        """
        self.ip_address = ip_address
        self.endereco = f"TCPIP0::192.168.1.131::INSTR"
        self.timeout = timeout
        self.rm = pyvisa.ResourceManager()
        self.scope = None

    def conectar(self):
        """Estabelece a conexão VISA com o Yokogawa."""
        print(f"Trying to connect to: {self.endereco}")
        try:
            self.scope = self.rm.open_resource(self.endereco)
            self.scope.timeout = self.timeout
            self.scope.clear()
            self.scope.write("*CLS") # Limpa o status e erros pendentes
        
        # Identifica o equipamento
            idn = self.scope.query('*IDN?').strip()
            print(f"Connected to: {idn}")

        # Desliga os cabeçalhos das respostas para facilitar o processamento de dados [1]
            self.scope.write(':COMMunicate:HEADer OFF')
            self.scope.query('*OPC?')
        except pyvisa.VisaIOError as e:
            print(f"Connection failed: {e}")
            exit()
            

    def configurar_aquisicao(self):
        """Configura os parâmetros de tempo e amostragem."""
        print("Configurando parâmetros de aquisição...")
        self.scope.write(":TRIGger:MODE SINGle") 
# 2. Taxa de Amostragem: 100 Mega Samples por segundo (100MA ou 100E+06)
        self.scope.write(":TIMebase:SRATe 100MA") 

        # 3. Tempo por Divisão: 5 microsegundos (5US ou 5E-06)
        self.scope.write(":TIMebase:TDIV 5US") 

        # 4. Record Length: 
        # Com 100 MS/s e 5us/div (total de 50us na tela), 5000 pontos capturam exatamente a tela cheia.
        self.scope.write(":ACQuire:RLENgth 5000") 

        self.scope.write(":CHAN7:DISP ON") 
        self.scope.query('*OPC?')
        

    def measure_start(self):

        try:
            print("Aguardando trigger (Modo Single)...")
            self.scope.write(":STARt") 

            # Sincronização: Aguarda o Bit 0 (Capture) do registro de condição se tornar 0
            # Isso garante que o equipamento só avance quando a captura Single terminar
            capturando = True
            while capturando:
                status = int(self.scope.query(':STATus:CONDition?')) 
                if not (status & 1): # Bit 0 é 'Capture'
                    capturando = False
                time.sleep(0.01)

            print("Captura finalizada. Salvando arquivo...")

            #--- Configuração de arquivo CSV no instrumento ---
            self.scope.write(':FILE:DIRectory:DRIVe HD') 
            self.scope.write(':FILE:DIRectory:CDIRectory "Gabriel"') 

            self.scope.write(':FILE:SAVE:ASCii:EXTension CSV') 
            self.scope.write(':FILE:SAVE:ASCii:TINFormation ON') 
            self.scope.write(f':FILE:SAVE:NAME scope_micro_100MS') 

            # Comando crucial para executar o salvamento em ASCII/CSV
            self.scope.write(':FILE:SAVE:ASCii:EXECute') 
            self.scope.query('*OPC?')  # Aguarda a gravação física no HD terminar

            print(f"Sucesso! Arquivo scope_micro_100MS.csv' salvo no HD do osciloscópio.")
        except KeyboardInterrupt:
            print("\nPARADA MANUAL!")
            self.scope.write(":STOP") 

        except Exception as e:
            print(f"\nERRO: {e}")
            

    def salvar_csv(self, drive="HD", diretorio="Gabriel", nome_arquivo="teste_csv"):
        pass

    def desconectar(self):
        if 'scope' in locals():
            self.scope.close()
    print("Conexão encerrada. FIM.")


if __name__ == "__main__":
    
    # Instancia o objeto do osciloscópio
    osciloscopio = YokogawaDL850(ip_address="TCPIP0::192.168.1.131::INSTR")

    try:
        # Chama os métodos na ordem necessária
        osciloscopio.conectar()
        time.sleep(0.5) # Pequena pausa para garantir que a conexão esteja estável
        osciloscopio.configurar_aquisicao()
        time.sleep(0.5) # Pequena pausa para garantir que as configurações sejam aplicadas
        osciloscopio.measure_start()
        time.sleep(0.5)



    finally:
        # O finally garante que, mesmo que dê erro no meio do processo, 
        # a conexão sempre será fechada, evitando travar a porta do equipamento.
        osciloscopio.desconectar()