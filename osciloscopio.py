import pyvisa
import time

def adquirir_dados_dl850(endereco_instrumento, nome_arquivo='dados_dl850.txt'):
    # 1. Configurar o Gerenciador de Recursos
    rm = pyvisa.ResourceManager()
    
    try:
        print(f"Tentando conectar a: {endereco_instrumento}")
        # Abrir conexão com o DL850
        scope = rm.open_resource(endereco_instrumento)
        
        # Configurações de Timeout e Chunk size (Importante para DL850 pois os dados são grandes)
        scope.timeout = 20000  # 20 segundos (a preparação dos dados pode demorar)
        scope.chunk_size = 102400 # Aumenta o buffer de leitura
        
        # Verificar conexão (pede a identificação do aparelho)
        idn = scope.query('*IDN?')
        print(f"Conectado a: {idn.strip()}")

        # 2. Configurar a transferência de forma de onda
        # Selecionar o Canal 1 (ajuste conforme seu módulo, ex: 1, CH1, etc)
        scope.write(':WAVeform:TRACe 1') 
        
        # Definir formato para ASCII (Texto/Float) para facilitar a gravação em .txt
        scope.write(':WAVeform:FORMat ASCii')
        
        # Definir o intervalo de dados (Start e Length)
        # 0 é o inicio, 10000 é o numero de pontos (ajuste conforme a memória usada)
        scope.write(':WAVeform:STARt 0')
        scope.write(':WAVeform:LENGth 10000') 

        print("Solicitando dados... aguarde.")
        
        # 3. Adquirir os dados
        # O DL850 retorna os valores separados por vírgula
        dados_brutos = scope.query(':WAVeform:SEND?')
        
        # Opcional: Obter parâmetros de tempo para criar a coluna X (Tempo)
        # Para simplificar, vamos pegar apenas os valores de tensão (Y) neste exemplo
        
        # 4. Processar e Salvar em TXT
        valores = dados_brutos.split(',')
        
        print(f"Recebidos {len(valores)} pontos. Salvando em {nome_arquivo}...")
        
        with open(nome_arquivo, 'w') as f:
            f.write("Amostra, Tensao(V)\n") # Cabeçalho
            for i, valor in enumerate(valores):
                # Limpeza básica de caracteres nulos ou quebra de linha se houver
                valor_limpo = valor.strip()
                if valor_limpo:
                    f.write(f"{i}, {valor_limpo}\n")
                    
        print("Aquisição concluída com sucesso!")
        
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        
    finally:
        # Fechar a conexão sempre
        if 'scope' in locals():
            scope.close()
        rm.close()

# --- EXECUÇÃO ---
# Exemplo via IP (Ethernet/VXI-11):
endereco = 'TCPIP::192.254.82.46::INSTR' 

# Se for USB, use algo como: 'USB0::0xB21::0x0001::SERIAL_NUMBER::0::INSTR'
# Você pode descobrir o endereço correto rodando: print(pyvisa.ResourceManager().list_resources())

adquirir_dados_dl850(endereco)