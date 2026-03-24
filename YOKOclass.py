import pyvisa
import time

class YokogawaDL850:
    def __init__(self, ip_address, timeout=60000): # Timeout aumentado para operações de disco
        """
        Inicializa as configurações básicas de conexão com o equipamento.
        """
        self.ip_address = ip_address
        self.endereco = f"TCPIP::{self.ip_address}::INSTR"
        self.timeout = timeout
        self.rm = pyvisa.ResourceManager()
        self.scope = None

    def conectar(self):
        """Estabelece a conexão VISA com o Yokogawa."""
        print(f"Trying to connect to: {self.endereco}")
        self.scope = self.rm.open_resource(self.endereco)
        self.scope.timeout = self.timeout
        self.scope.clear()
        
        # Identifica o equipamento
        idn = self.scope.query('*IDN?').strip()
        print(f"Connected to: {idn}")

        # Desliga os cabeçalhos das respostas para facilitar o processamento de dados [1]
        self.scope.write(':COMMunicate:HEADer OFF')
        self.scope.query('*OPC?')

    def configurar_aquisicao(self, record_length=1000, sample_rate=1000, time_div=0.1, trigger="AUTO"):
        """Configura os parâmetros de tempo e amostragem."""
        print("Configurando parâmetros de aquisição...")
        # Nota: Record Length deve ser um valor permitido (ex: 1000, 2500, 5000...) [2]
        self.scope.write(f':ACQuire:RLENgth {record_length}')
        self.scope.write(f':TIMebase:SRATe {sample_rate}')
        self.scope.write(f":TRIGger:MODE {trigger}")
        self.scope.write(f':TIMebase:TDIV {time_div}')
        self.scope.query('*OPC?')

    def measure_start(self):
        """Inicia a aquisição e aguarda o término real pelo registro de status."""
        self.scope.write(':STARt') # [4]
        
        # Sincronização Robusta: Em vez de time.sleep, verificamos o bit de "Capture"
        # Bit 0 do Condition Register indica se a aquisição está em progresso [5, 6]
        capturando = True
        while capturando:
             status = int(self.scope.query(':STATus:CONDition?'))
             if not (status & 1): # Se o Bit 0 for 0, a captura terminou
                 capturando = False
             time.sleep(0.1) # Evita sobrecarregar a rede

    def measure_stop(self):
        """Inicia a aquisição e aguarda o término real pelo registro de status."""
        self.scope.write(':STOp') # [4]
            

    def salvar_csv(self, drive="HD", diretorio="Gabriel", nome_arquivo="teste_csv"):
        """Salva os dados internamente no HD do Yokogawa no formato CSV."""
        print(f"Salvando dados como {nome_arquivo}.csv no diretório '{diretorio}' do {drive}...")
        
        # Seleção da mídia (HD interno) [7]
        self.scope.write(f':FILE:DIRectory:DRIVe {drive}')
        
        # Tenta mudar para o diretório. Nota: O diretório já deve existir no osciloscópio [8]
        self.scope.write(f':FILE:DIRectory:CDIRectory "{diretorio}"')
        
        # Configurações do formato ASCII/CSV [9, 10]
        self.scope.write(':FILE:SAVE:ASCii:EXTension CSV')
        self.scope.write(':FILE:SAVE:ASCii:TINFormation ON') # Coluna de tempo [11]
        self.scope.write(f':FILE:SAVE:NAME "{nome_arquivo}"') # Nome sem extensão [12]
        
        # EXECUÇÃO DO SALVAMENTO [9, 13]
        # Este é um 'Overlap Command': o Python deve esperar o instrumento terminar de escrever no disco
        self.scope.write(':FILE:SAVE:ASCii:EXECute')
        
        print("Gravando no disco do osciloscópio (aguarde)...")
        self.scope.query('*OPC?') # Só retorna quando a gravação física terminar [14]
        print("Arquivo salvo com sucesso no equipamento.")

    def desconectar(self):
        """Encerra a conexão de forma segura."""
        if self.scope is not None:
            self.scope.close()
            print("Conexão encerrada de forma segura.")


