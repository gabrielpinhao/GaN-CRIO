import pyvisa
import time

class YokogawaDL850:
    def __init__(self, timeout=60000, yoko_address="TCPIP0::192.168.1.131::INSTR"):
        self.yoko_address = yoko_address
        self.timeout = timeout
        self.rm = pyvisa.ResourceManager()

    def conectar(self):
        print(f"Trying to connect to: {self.yoko_address}")
        try:
            self.scope = self.rm.open_resource(self.yoko_address)
            self.scope.timeout = 60000
            self.scope.clear()
            self.scope.write("*CLS")
        
            idn = self.scope.query('*IDN?').strip()
            print(f"Connected to: {idn}")

            self.scope.write(':COMMunicate:HEADer OFF')
            self.scope.query('*OPC?') # Garante que a configuração de Header foi aplicada
        
        except pyvisa.VisaIOError as e:
            print(f"Connection failed: {e}")
            exit()

    def ready(self):
        """Monitora o Event Status Register (ESR) sem travar o barramento."""
        self.scope.write('*OPC') 
        
        testing = True
        while testing:
            esr = int(self.scope.query('*ESR?')) 
            
            if esr & 1: # Bit 0: Operação Completa
                testing = False
            
            elif esr & 60: # Bits 2, 3, 4, 5 indicam erros de execução/comando
                print("\nALERTA: Ocorreu um erro no instrumento durante a operação!")
                erro = self.scope.query(':SYSTem:ERRor?')
                print(f"Error: {erro}")
                testing = False
            
            time.sleep(0.1) # Reduzido para 0.1s para deixar a resposta mais ágil

    def configurar_aquisicao(self, test_name):
        print("Setting acquisition parameters...")

        self.scope.write(":TRIGger:MODE SINGle")
        self.scope.write(":ACQuire:RLENgth 4000")
        self.scope.write(":TIMebase:SRATe 20E6")
        self.scope.write(":TIMebase:TDIV 20E-6")

        self.scope.write(":CHAN7:DISP ON")
        self.scope.write(':CHANnel7:LABEL "Vgate"')
        self.scope.write(":CHAN8:DISP ON")
        self.scope.write(':CHAN8:LABel "Vds"')
        self.scope.write(":CHAN15:DISP ON")
        self.scope.write(':CHAN15:LABel "Id"')

        self.scope.write(':FILE:DIRectory:DRIVe HD') 
        self.scope.write(':FILE:DIRectory:CDIRectory "Gabriel"') 
    
        self.scope.write(':FILE:SAVE:ASCii:EXTension CSV') 
        self.scope.write(':FILE:SAVE:ASCii:TINFormation ON') 
        self.scope.write(f':FILE:SAVE:NAME {test_name}') 

        # Substituímos o sleep/clear/WAI por um simples *OPC? para garantir a aplicação
        self.scope.query('*OPC?')
        
    def measure_start(self):
        """Arma o Single Trigger."""
        self.scope.write(":STARt")
        # Removemos o self.ready() daqui. O STARt não bloqueia do jeito que queremos.
        # A espera real acontece no início da função measure_save.

    def measure_save(self):
        try:
            capturando = True
            while capturando:
                status = int(self.scope.query(':STATus:CONDition?')) 
                if not (status & 1): 
                    capturando = False
                time.sleep(0.1) 

            time.sleep(0.5)

            self.scope.write('*CLS')
            self.scope.write(':FILE:SAVE:ASCii:EXECute')
            
            time.sleep(2.0)

        except KeyboardInterrupt:
            print("\nMANUAL STOP!")
            self.scope.write(":STOP") 

        except Exception as e:
            print(f"\nERRO PyVISA in measure_save: {e}")

    def desconectar(self):
        self.scope.close()
        print("Scope disconnected.")