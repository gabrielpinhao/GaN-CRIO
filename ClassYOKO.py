import pyvisa
import time

class YokogawaDL850:
    def __init__(self, timeout=60000, yoko_address="TCPIP0::192.168.1.131::INSTR"): # Timeout aumentado para operações de disco
        """
        Inicializa as configurações básicas de conexão com o equipamento.
        """
        self.yoko_address = yoko_address
        self.timeout = timeout
        self.rm = pyvisa.ResourceManager()

    def conectar(self):
        """Estabelece a conexão VISA com o Yokogawa."""
        print(f"Trying to connect to: {self.yoko_address}")
        try:
            self.scope = self.rm.open_resource(self.yoko_address)
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

        print("Setting acquisition parameters...")

        self.scope.write(":TRIGger:MODE SINGle")
        time.sleep(0.1) # Pequena pausa para o processador

        self.scope.write(":ACQuire:RLENgth 4000")
        time.sleep(0.1)

        self.scope.write(":TIMebase:SRATe 20E6")
        time.sleep(0.1)

        self.scope.write(":TIMebase:TDIV 20E-6")

        self.scope.write(":CHAN7:DISP ON")
        self.scope.write(':CHANnel7:LABEL "Vgate"')
        self.scope.write(":CHAN8:DISP ON")
        self.scope.write(':CHAN8:LABel "Vds"')
        self.scope.write(":CHAN15:DISP ON")
        self.scope.write(':CHAN15:LABel "Id"')

        self.scope.write("*WAI") 
        time.sleep(0.5)
        self.scope.clear()
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

            self.scope.write(':FILE:SAVE:ASCii:EXECute')
            time.sleep(0.5)
            
            self.scope.query('*OPC?')
        
        except KeyboardInterrupt:
            print("\nMANUAL STOP!")
            self.scope.write(":STOP") 

        except Exception as e:
            print(f"\nERRO: {e}")

    def salvar_csv(self, drive="HD", diretorio="Gabriel", nome_arquivo="teste_csv"):
        pass

    def test_connection(self):
        self.idn = self.scope.query('*IDN?')
        print(f"Connected to: {self.idn.strip()}")

    def desconectar(self):
        self.scope.close()
        print("Scope disconnected.")

if __name__ == "__main__":
    
    # Instancia o objeto do osciloscópio
    osciloscopio = YokogawaDL850(yoko_address="TCPIP0::192.168.1.131::INSTR")

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