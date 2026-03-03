import pyvisa
import pandas as pd
import time
import re # Importante adicionar o módulo de expressões regulares

def capturar_para_pc(canal=1, nome_arquivo="medicao_direta.csv"):
    """
    Puxa os dados da memória do osciloscópio Yokogawa DL850E via rede 
    e salva o CSV diretamente no disco do PC, ignorando caracteres especiais.
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
        # EM VEZ DE QUERY, SEPARAMOS EM WRITE E READ_RAW:
        scope.write(':WAVeform:SEND?')
        
        # Lê os bytes crus, burlando a falha do PyVISA com caracteres estranhos
        dados_brutos = scope.read_raw()
        
        # Decodifica ignorando os bytes ruins (como o 0xb4)
        dados_texto = dados_brutos.decode('ascii', errors='ignore')
        
        # Quebra nas vírgulas
        pedacos = dados_texto.strip().split(',')
        valores_y = []
        
        # Usa Regex para garantir que só pegamos os números, ignorando letras anexadas
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
        
        # 6. Salva no notebook usando Pandas
        df = pd.DataFrame({
            'Tempo (s)': valores_x,
            'Tensao (V)': valores_y
        })
        
        df.to_csv(nome_arquivo, index=False)
        print(f"Sucesso! {len(valores_y)} pontos salvos em: {nome_arquivo}")

    except Exception as e:
        print(f"Erro na captura: {e}")
    finally:
        if scope:
            scope.close()

# Executar a função
capturar_para_pc(canal=9)