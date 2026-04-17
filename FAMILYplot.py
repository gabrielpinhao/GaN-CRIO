import os
import pandas as pd
import matplotlib.pyplot as plt
from ClassTEST import Characterization
from ClassDATA import DATAclass

def consolidar_dados(folder, prefix, output_file):
    """
    Lê arquivos CSV, ordena por Vg médio e consolida em um único DataFrame e arquivo CSV.
    """
    tests = [f for f in os.listdir(folder) if f.startswith(prefix)]
    #tests = [t for t in tests if t != 'OUT_VG25_'] 

    colecao = []

    for t in tests:
        try:
            file = os.path.join(folder, t, t + '_ALL.csv')
            df = pd.read_csv(file)
            vg_mean = df['Vg'].mean()
            
            # Prepara subset e renomeia coluna de corrente
            df_temp = df[['Vds', 'Ids']].copy()
            df_temp = df_temp.rename(columns={'Ids': f'Ids (Vg={vg_mean:.1f}V)'})
            colecao.append((vg_mean, df_temp))
        except Exception as e:
            print(f"Erro ao processar {t}: {e}")

    # Ordena pelo valor numérico de Vg
    colecao.sort(key=lambda x: x[0])

    df_consolidado = pd.DataFrame()
    for _, df_data in colecao:
        if df_consolidado.empty:
            df_consolidado = df_data
        else:
            # Merge externo para alinhar pontos de Vds
            df_consolidado = pd.merge(df_consolidado, df_data, on='Vds', how='outer')

    # Ordenação final e salvamento
    df_consolidado = df_consolidado.sort_values(by='Vds').reset_index(drop=True)
    df_consolidado.to_csv(output_file, index=False)
    print(f"Dados consolidados com sucesso em: {output_file}")
    
    return df_consolidado

def plotar_consolidado(caminho_arquivo, tipo_plot='linear', titulo='Curvas Características'):
    try:
        df = pd.read_csv(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao ler o arquivo para plotagem: {e}")
        return

    plt.figure(figsize=(5, 4))

    colunas_ids = [col for col in df.columns if col != 'Vds']

    for col in colunas_ids:
        label_limpo = col.replace('Ids (', '').replace(')', '')
        if label_limpo == "Vg=14.9V": label_limpo = "Vg=15.0V"

        dados_plot = df[['Vds', col]].dropna()
        
        # Agora plotamos usando os dados limpos
        plt.plot(dados_plot['Vds'], dados_plot[col], 
                 label=label_limpo, lw=1.5, ls="-",
                 marker='.', markersize=3)

    if tipo_plot == 'log':
        plt.yscale('log')
    elif tipo_plot == 'loglog':
        plt.yscale('log')
        plt.xscale('log')

    plt.title(titulo)
    plt.xlabel('Vds, Drain-to-Source Voltage [V]')
    plt.ylabel('Id, Drain-to-Source Current [A]')
    plt.grid(True, which="both", ls="-", lw=0.5, alpha=0.7)
    plt.legend(loc='upper left', fontsize='x-small', ncol=1)

    plt.xlim(0,4.5)  # Garantir que o eixo x comece em 0
    plt.ylim(0,100)  # Garantir que o eixo y
    
    plt.tight_layout()
    plt.show()

def gerar_arquivo_all(test_name, local_folder= 'Ensaios'):
    """
    Gera o arquivo CSV_ALL para um teste específico.
    """
    data = DATAclass()    
    family = [f for f in os.listdir(local_folder) if f.startswith(test_name)]

    for test in family:
        test_path = os.path.join(local_folder, test)
        samples = [f for f in os.listdir(test_path) if f.lower().endswith('.csv')]

        if any(f.lower().endswith('all.csv') for f in samples):
            print(f"Aviso: O arquivo ALL.csv foi encontrado em {test}")

        else:
            df_final = []
            vg_target = float(test[7:9])
            if vg_target == 25.0: vg_target = 2.5

            print((f"Processando {test} com {len(samples)} amostras. Vg alvo: {vg_target}"))

            for sample in samples:
                sample_path = os.path.join(test_path, sample)
                df = data.processar_dados(sample_path)
                vg, vds, ids = data.dc_estimator(df)

                if (abs(vg - vg_target) / vg_target) * 100 < 0.5:

                    df_final.append({
                        'Arquivo': sample,
                        'Vg': vg,
                        'Vds': vds,
                        'Ids': abs(ids)
                    })

            df_final = pd.DataFrame(df_final)

            file_final = f"{test_path}/{test}_ALL.csv"
            df_final.to_csv(file_final, index=False)
            print(f"Arquivo ALL.csv gerado para {test} em: {file_final}")

## ----- EXECUÇÃO DO PROCESSO ----- ##

CAMINHO_PASTA = 'Ensaios'

#PREFIXO_ARQUIVOS = 'OUT_VG' #Output MOSFET Room Temperature
#PREFIXO_ARQUIVOS = 'M2CT_VG' #Output MOSFET Cryo Temperature
PREFIXO_ARQUIVOS = 'IGBT_VG' #Output IGBT Room Temperature

ESTILO_PLOT = 'linear'
TIPO_TESTE = 'Output'

ARQUIVO_SAIDA = f'{PREFIXO_ARQUIVOS}_final.csv'

if not os.path.exists(ARQUIVO_SAIDA):
    consolidar_dados(CAMINHO_PASTA, PREFIXO_ARQUIVOS, ARQUIVO_SAIDA) # 1. Consolidar

if os.path.exists(ARQUIVO_SAIDA): # 2. Plotar
    plotar_consolidado(ARQUIVO_SAIDA, 
                       tipo_plot=ESTILO_PLOT,
                       titulo=f'{TIPO_TESTE} Characteristics: IGBT @{'CT' if 'CT'in PREFIXO_ARQUIVOS else "RT"}')

#gerar_arquivo_all(PREFIXO_ARQUIVOS) 