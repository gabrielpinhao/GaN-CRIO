import pyvisa
import time

import pyvisa
import time

class YokogawaDL850:
    def __init__(self, ip_address, timeout=30000):
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
        print(f"Tentando conectar a: {self.endereco}")
        self.scope = self.rm.open_resource(self.endereco)
        self.scope.timeout = self.timeout
        self.scope.clear()
        
        # Identifica o equipamento
        idn = self.scope.query('*IDN?').strip()
        print(f"Conectado: {idn}")
        time.sleep(1)

        # Desliga os cabeçalhos das respostas para evitar erros de parser
        self.scope.write(':COMMunicate:HEADer OFF')
        self.scope.query('*OPC?') # Aguarda o comando terminar

    def configurar_aquisicao(self, record_length=1000, sample_rate=1000, time_div=0.001):
        """Configura os parâmetros de tempo e amostragem."""
        print("Configurando parâmetros de aquisição...")
        self.scope.write(f':ACQuire:RLENgth {record_length}')
        self.scope.write(f':TIMebase:SRATe {sample_rate}')
        self.scope.write(':TRIGger:MODE SINGle')
        self.scope.write(f':TIMebase:TDIV {time_div}')
        self.scope.query('*OPC?')

    def iniciar_medicao(self):
        """Inicia e para a aquisição de dados."""
        print("Iniciando aquisição de dados por 1 segundo...")
        self.scope.write(':STARt')
        self.scope.query('*OPC?')
        
        # Nota: Dependendo do trigger, você pode precisar de um time.sleep(1) aqui
        # para garantir que ele capture 1 segundo real antes de dar STOP.
        
        self.scope.write(':STOP')
        self.scope.query('*OPC?')

    def salvar_csv(self, drive="HD", diretorio="Gabriel", nome_arquivo="teste_csv"):
        """Salva os dados internamente no HD do Yokogawa no formato CSV."""
        print(f"Salvando dados como {nome_arquivo}.csv no diretório '{diretorio}' do {drive}...")
        self.scope.write(':COMMunicate:HEADer OFF')
        self.scope.write(f':FILE:DIRectory:DRIVe {drive}')
        self.scope.write(f':FILE:DIRectory:CDIRectory "{diretorio}"')
        
        # Configurações do CSV
        self.scope.write(':FILE:SAVE:ASCii:EXTension CSV')
        self.scope.write(':FILE:SAVE:ASCii:TINFormation ON') # Inclui os dados de tempo
        self.scope.write(f':FILE:SAVE:NAME "{nome_arquivo}"')
        
        # Executa o salvamento
        self.scope.write(':FILE:SAVE:ASCii:EXECute')
        self.scope.query('*OPC?') # Aguarda o salvamento terminar no disco do osciloscópio
        print("Arquivo salvo com sucesso no equipamento.")

    def desconectar(self):
        """Encerra a conexão de forma segura."""
        if self.scope is not None:
            self.scope.close()
            print("Conexão encerrada de forma segura.")


# ==========================================
# Exemplo de como usar a classe criada
# ==========================================
if __name__ == "__main__":
    ip = "192.168.1.131"
    
    # Instancia o objeto do osciloscópio
    osciloscopio = YokogawaDL850(ip_address=ip)

    try:
        # Chama os métodos na ordem necessária
        osciloscopio.conectar()
        osciloscopio.configurar_aquisicao(record_length=1000, sample_rate=1000, time_div=0.001)
        osciloscopio.iniciar_medicao()
        osciloscopio.salvar_csv(nome_arquivo="medicao_1s")

    except pyvisa.errors.VisaIOError as e:
        print(f"Erro de comunicação VISA: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        # O finally garante que, mesmo que dê erro no meio do processo, 
        # a conexão sempre será fechada, evitando travar a porta do equipamento.
        osciloscopio.desconectar()