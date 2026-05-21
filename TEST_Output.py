import os
import time
import pyvisa
import pandas as pd
from ClassTEST import Characterization

start = time.time()

## ATENÇÃO: Definir CANAL e NÍVEL do Trigger no osciloscópio antes de rodar o teste. ##

# --- Configurações Iniciais ---

#test_name = "MOS12_OUT"
#test_name = "M2CT_VG25_A"

test_name = "SICCT_VG9_"


gate_volt = 9

max_ds_volt = 6
ds_step = 0.10
ds_step_sat = 0.10

# --- Configurações Normalmente Constantes ---

remote_folder = "/HD-0/Gabriel"
local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios_v2/"

init_ds_volt = 0
ds_curr = 5.0
gate_curr = 1.0
gate_error_threshold = 0.5 #% de erro permitido de Vg

test = Characterization(local_folder, test_name)
test.ftp.connect()
test.current_set(gate_curr, ds_curr)

vg_target = gate_volt
init_gate_error = 0.61
gate_volt = vg_target + init_gate_error
good_vg = gate_volt

df_output = []
ds_volt = init_ds_volt
gate_integral = 0.0

test.clear_capacitor()

print(f"----- Starting Output Test: {time.time()} -----")

while ds_volt < max_ds_volt:
    try:
        test.send_pulse(gate_volt, ds_volt)
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

            if abs(vg - vg_target) < vg_target*0.05:
                gate_error = vg_target - vg
                gate_integral += gate_error
                gate_volt = vg_target + init_gate_error + 0.25*gate_error + 0.05*gate_integral
            else:
                gate_volt = good_vg
                gate_integral = 0.0
        
        else:
            print(f"Vg: {vg:.2f} V, Vds: {vds:.2f} V, Ids: {ids:.2f} A")

            df_output.append({
            'Arquivo': latest_file_name,
            'Vg': vg,
            'Vds': vds,
            'Ids': ids
            })

            if ds_volt > 3.0: ds_step = ds_step_sat
            ds_volt += ds_step
            good_vg = gate_volt

test.ftp.close()

test.clear_capacitor()

end = time.time()
print(f"Tempo Total: {(end - start)/60:.2f} minutos")

df_final = pd.DataFrame(df_output)
file_final = f"{local_folder}/{test_name}/{test_name}_ALL.csv"

df_final.to_csv(file_final, index=False)

test.data.actual_plot(pd.read_csv(file_final), test_name, test='Output')