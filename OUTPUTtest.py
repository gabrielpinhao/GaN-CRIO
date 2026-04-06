##Teste de configuração de 2 fontes Hikari

import os
import time
import pyvisa
import pandas as pd
from HIKARI_DC import HikariHF3205P
from YOKOclass import YokogawaDL850  
from FTPDownloader import FTPDownloader
from DATAclass import DATAclass

# --- Configurações Iniciais ---

remote_folder = "/HD-0/Gabriel"
local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"
test_name = "MOS6_OUTPUT"

tensao_gate = 4.5
corrente_gate = 1.0

tensao_ds_init = 0.0
tensao_ds_max = 2.5
tensao_step = 0.05
corrente_ds = 5.0

# --- Preparar Pasta e Instrumentos ---

data = DATAclass()
ftp = FTPDownloader()
os.makedirs(f"{local_folder}/{test_name}", exist_ok=True)

rm = pyvisa.ResourceManager()
print(rm.list_resources())

scope_yoko = YokogawaDL850("TCPIP0::192.168.1.131::INSTR")

try:
    scope_yoko.conectar()
    print("Osciloscópio conectado:", scope_yoko.scope.query('*IDN?').strip())
    scope_yoko.configurar_aquisicao()
except Exception as e:
    print(f"Erro ao conectar ao osciloscópio: {e}")
    exit()

for resource in rm.list_resources():
    try: ## Identifica o instrumento pelo IDN e instancia a fonte correspondente.
        inst = rm.open_resource(resource)
        idn = inst.query('*IDN?').strip()
        print(f"{resource}: SN:{idn[-8:]}")

        if int(idn[-8:]) == 49152063:
            gate_source = HikariHF3205P(resource=resource)
            print("Fonte conectada:", gate_source.idn())

        elif int(idn[-8:]) == 9437206:
            drain_source = HikariHF3205P(resource=resource)
            print("Fonte conectada:", drain_source.idn())
    except:
        print(f"{resource}: Não é um instrumento VISA ou não respondeu ao *IDN?")
    finally: 
        time.sleep(0.5)

df_output = []
tensao_ds = tensao_ds_init
i = 0

while tensao_ds < tensao_ds_max:
    try:
        
        drain_source.set_voltage(tensao_ds)
        drain_source.set_current(corrente_ds)

        gate_source.set_voltage(tensao_gate)
        gate_source.set_current(corrente_gate)

        scope_yoko.measure_start()
        time.sleep(1)

        drain_source.output_on()
        time.sleep(5)
        drain_source.output_off()
        time.sleep(0.2)
        gate_source.output_on()
        time.sleep(0.08)
        gate_source.output_off()

        scope_yoko.measure_save(test_name)

    except pyvisa.VisaIOError:
        print("Falha na Conexao")
        drain_source.output_off()
        gate_source.output_off()
        exit()

    finally:
        drain_source.output_off()
        gate_source.output_off()

        ftp.connect()
        last_file_addr, latest_file_name = ftp.download_latest_file(test_name, remote_folder, local_folder)
        ftp.close()

        df = data.processar_dados(last_file_addr)
        vg, vds, ids = data.dc_estimator(df)
        print(f"Vg: {vg:.2f} V, Vds: {vds:.2f} V, Ids: {ids:.2f} A")
        #data.plot_separated(df)

        df_output.append({
        'Arquivo': latest_file_name,
        'Vg': vg,
        'Vds': vds,
        'Ids': ids
        })
        
        tensao_ds += tensao_step
        i += 1

gate_source.output_on()
time.sleep(2)
gate_source.output_off()

df_final = pd.DataFrame(df_output)
df_final.to_csv(f"{local_folder}/{test_name}/{test_name}_ALL.csv", index=False)

data.plot_output_characteristic(local_folder, test_name)