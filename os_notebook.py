import pyvisa
import pandas as pd
import time
import re 
import os # Necessário para criar a pasta e manipular os caminhos

def capturar_para_pc(canal=1, nome_arquivo="medicao_direta.csv"):
    """
    Puxa os dados da memória do osciloscópio Yokogawa DL850E via rede 
    e salva o CSV na pasta especificada.
    """
    rm = pyvisa.ResourceManager()
    ip_yokogawa = "192.168.1.131" 
    endereco = f"TCPIP::{ip_yokogawa}::INSTR"
    
    scope = None
    try:
        scope = rm.open_resource(endereco)
        scope.timeout = 60000  # Timeout alto para transferências ASCII longas
        
        # 1. Garante que o equipamento não envie cabeçalhos nas respostas
        scope.write(':COMMunicate:HEADer OFF') 
        
        print(f"Transferindo dados do canal {canal}...")
        
        # 2. Seleciona o canal e o formato de transmissão
        scope.write(f':WAVeform:TRACe {canal}')
        scope.write(':WAVeform:FORMat ASCii') 
        
        # 3. Coleta parâmetros reais do Yokogawa para reconstruir o Eixo X (Tempo)
        sample_rate = float(scope.query(':WAVeform:SRATe?'))
        x_incr = 1.0 / sample_rate
        
        trig_pos_points = int(scope.query(':WAVeform:TRIGger?')) 
        x_start = -(trig_pos_points * x_incr)
        
        # 4. Solicita os dados brutos de tensão (Eixo Y)
        scope.write(':WAVeform:SEND?')
        
        dados_brutos = scope.read_raw()
        dados_texto = dados_brutos.decode('ascii', errors='ignore')
        
        pedacos = dados_texto.strip().split(',')
        valores_y = []
        
        for pedaco in pedacos:
            try:
                if pedaco.strip(): 
                    valores_y.append(float(pedaco))
            except ValueError:
                numeros = re.findall(r"[-+]?\d*\.\d+[eE]?[-+]?\d*|[-+]?\d+", pedaco)
                if numeros:
                    valores_y.append(float(numeros[-1]))
        
        # 5. Reconstrói matematicamente o eixo do tempo
        valores_x = [x_start + (i * x_incr) for i in range(len(valores_y))]
        
        # ==========================================================
        # 6. Prepara o caminho exato fornecido
        # Usamos o 'r' na frente da string para que o Python entenda as barras (\) corretamente
        # ==========================================================
        pasta_destino = r"C:\Users\nitee\Desktop\GaN-CRIO\Teste"
        
        # Cria a pasta caso ela ainda não exista no seu computador
        os.makedirs(pasta_destino, exist_ok=True)
        
        # Junta o caminho da pasta com o nome do arquivo (ex: medicao_direta.csv)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        
        # 7. Salva usando Pandas no caminho completo
        df = pd.DataFrame({
            'Tempo (s)': valores_x,
            'Tensao (V)': valores_y
        })
        
        df.to_csv(caminho_completo, index=False)
        print(f"Sucesso! {len(valores_y)} pontos salvos em: {caminho_completo}")

    except Exception as e:
        print(f"Erro na captura: {e}")
    finally:
        if scope:
            scope.close()

# Executar a função
capturar_para_pc(canal=9)