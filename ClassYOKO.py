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
        self.scope.write(":TRIGger:MODE SINGle") # 1. Modo de Trigger: Single (captura única)
        self.scope.write(":TIMebase:SRATe 50MA") # 2. Taxa de Amostragem: 100 Mega Samples por segundo (100MA ou 100E+06)
        self.scope.write(":TIMebase:TDIV 20US") # 3. Tempo por Divisão: 5 microsegundos (5US ou 5E-06)
        self.scope.write(":ACQuire:RLENgth 5000") # 4. Record Length: Com 100 MS/s e 20us/div (total de 50us na tela), 20000 pontos capturam exatamente a tela cheia.
        self.scope.write(":CHAN7:DISP ON") 
        self.scope.write(":CHAN8:DISP ON")
        self.scope.write(":CHAN15:DISP ON") 
        self.scope.query('*OPC?')
        
    def measure_start(self):
        self.scope.write(":STARt")


    def measure_save(self, test_name):

        try:
            # Sincronização: Aguarda o Bit 0 (Capture) do registro de condição se tornar 0
            # Isso garante que o equipamento só avance quando a captura Single terminar
            capturando = True
            while capturando:
                status = int(self.scope.query(':STATus:CONDition?')) 
                if not (status & 1): # Bit 0 é 'Capture'
                    capturando = False
                time.sleep(0.01)

            #--- Configuração de arquivo CSV no instrumento ---
            self.scope.write(':FILE:DIRectory:DRIVe HD') 
            self.scope.write(':FILE:DIRectory:CDIRectory "Gabriel"') 

            self.scope.write(':FILE:SAVE:ASCii:EXTension CSV') 
            self.scope.write(':FILE:SAVE:ASCii:TINFormation ON') 
            self.scope.write(f':FILE:SAVE:NAME {test_name}') 

            # Comando crucial para executar o salvamento em ASCII/CSV
            self.scope.write(':FILE:SAVE:ASCii:EXECute') 
            self.scope.query('*OPC?')  # Aguarda a gravação física no HD terminar

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