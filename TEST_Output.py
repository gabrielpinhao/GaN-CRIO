import os
import time
import pyvisa
import pandas as pd
from ClassTEST import Characterization

start = time.time()

# --- Configurações Iniciais ---

test_name = "MOS10_OUTPUT"

gate_volt = 3.0

max_ds_volt = 1.0
ds_step = 0.5

# --- Configurações Normalmente Constantes ---

remote_folder = "/HD-0/Gabriel"
local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"

init_ds_volt = 0.0
ds_curr = 5.0
gate_curr = 1.0
gate_error_threshold = 0.6 #% de erro permitido de Vg

test = Characterization(local_folder, test_name)
test.ftp.connect()

test.current_set(gate_curr, ds_curr)

# ----- Verificação Inicial de Vg ----

vg_target = gate_volt

try:
    
    test.send_pulse(gate_volt, max_ds_volt/2, test_name)
    
    last_file_addr, latest_file_name = test.ftp.download_latest_file(test_name, remote_folder, local_folder)

    df = test.data.processar_dados(last_file_addr)
    vg, vds, ids = test.data.dc_estimator(df)

    gate_volt = 2*gate_volt - vg

    print(f"Target Vg: {vg_target:.2f} V, Applied Vg: {vg:.2f} V, Vg Adjust: {(vg_target - gate_volt):.2f} V")

except pyvisa.VisaIOError:
    print("Falha no Teste Inicial de Vg")
    test.drain_source.output_off()
    test.gate_source.output_off()
    exit()

finally: 
    test.clear_capacitor()

# ----- Loop Principal de Ensaio ----

df_output = []
ds_volt = init_ds_volt

while ds_volt < max_ds_volt:
    try:
        test.send_pulse(gate_volt, ds_volt, test_name)

    except pyvisa.VisaIOError:
        print("Falha na Conexao")
        test.drain_source.output_off()
        test.gate_source.output_off()
        exit()

    except KeyboardInterrupt:
        print("\nMANUAL STOP!")
        test.drain_source.output_off()
        test.gate_source.output_off()
        exit()

    finally:
        
        last_file_addr, latest_file_name = test.ftp.download_latest_file(test_name, remote_folder, local_folder)

        df = test.data.processar_dados(last_file_addr)
        vg, vds, ids = test.data.dc_estimator(df)
    
        if (abs(vg - vg_target) / vg_target) * 100 > gate_error_threshold:
            print(f"High Vg Error. Vg: {vg:.2f} V, Target: {vg_target:.2f} V")
        
        else:
            print(f"Vg: {vg:.2f} V, Vds: {vds:.2f} V, Ids: {ids:.2f} A")

            df_output.append({
            'Arquivo': latest_file_name,
            'Vg': vg,
            'Vds': vds,
            'Ids': ids
            })

            ds_volt += ds_step

test.ftp.close()

test.clear_capacitor()

end = time.time()
print(f"Tempo Total: {(end - start)/60:.2f} minutos")

df_final = pd.DataFrame(df_output)
file_final = f"{local_folder}/{test_name}/{test_name}_ALL.csv"

df_final.to_csv(file_final, index=False)

test.data.actual_plot(pd.read_csv(file_final), test_name, test='Output')