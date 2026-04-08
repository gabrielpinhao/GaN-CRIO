import os
import time
import pyvisa
import pandas as pd
from HIKARI_DC import HikariHF3205P
from YOKOclass import YokogawaDL850  
from FTPDownloader import FTPDownloader
from DATAclass import DATAclass

start = time.time()

# --- Configurações Iniciais ---

test_name = "MOS1_TRANSFER"

max_gate_volt = 10.0
gate_step = 0.05

ds_volt = 2.5

# --- Configurações Constantes ---

remote_folder = "/HD-0/Gabriel"
local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"

init_gate_volt = 0.0
ds_curr = 5.0
gate_curr = 1.0
error_threshold = 1 #% de erro permitido de Vg e Vds

def send_pulse(gate_volt, ds_volt, test_name):

    scope_yoko.measure_start()

    drain_source.set_voltage(ds_volt)
    gate_source.set_voltage(gate_volt)
    
    time.sleep(0.5)

    drain_source.output_on()
    time.sleep(5)
    drain_source.output_off()
    time.sleep(0.5)
    gate_source.output_on()
    time.sleep(0.08)
    gate_source.output_off()

    scope_yoko.measure_save(test_name)

def clear_capacitor():

    gate_source.set_voltage(5.0)
    drain_source.output_off()
    time.sleep(0.5)
    gate_source.output_on()
    time.sleep(3)
    gate_source.output_off()

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
    try:
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

gate_source.set_current(gate_curr)
drain_source.set_current(ds_curr)

# ----- Verificação Inicial de Vg ----

vg_target = 5.0

try:
    send_pulse(vg_target, ds_volt, test_name)

except pyvisa.VisaIOError:
    print("Falha no Teste Inicial de Vg")
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

    vg_error = vg / vg_target
    vds_error = vds / ds_volt

    print(f"Target Vg: {vg_target:.2f} V, Measured Vg: {vg:.2f} V, Vg Scale: {(vg_error)*100:.2f} %")
    print(f"Target Vds: {ds_volt:.2f} V, Measured Vds: {vds:.2f} V, Vds Scale: {(vds_error)*100:.2f} %")

    clear_capacitor()

# ----- Loop Principal de Ensaio ----

df_output = []
gate_volt = init_gate_volt

while gate_volt < max_gate_volt:
    try:
        send_pulse(gate_volt/vg_error, ds_volt/vds_error, test_name)

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
        
        if (abs(vg - vg_target) / vg_target) * 100 > error_threshold or (abs(vds - ds_volt) / ds_volt) * 100 > error_threshold:
            print(f"High Error. Vg: {vg:.2f} V, Target: {vg_target:.2f} V, Vds: {vds:.2f} V, Target: {ds_volt:.2f} V")
        
        else:
            print(f"Vg: {vg:.2f} V, Vds: {vds:.2f} V, Ids: {ids:.2f} A")

            df_output.append({
            'Arquivo': latest_file_name,
            'Vg': vg,
            'Vds': vds,
            'Ids': ids
            })

            gate_volt += gate_step

clear_capacitor()

df_final = pd.DataFrame(df_output)
df_final.to_csv(f"{local_folder}/{test_name}/{test_name}_ALL.csv", index=False)

data.plot_output_characteristic(local_folder, test_name)

end = time.time()
print(f"Tempo Total: {(end - start)/60:.2f} minutos")