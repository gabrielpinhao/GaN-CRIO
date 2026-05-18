import os
import time
import pyvisa
import pandas as pd
from ClassTEST import Characterization

start = time.time()

# --- Configurações Iniciais ---

test_name = "MOS2_VD25"
#test_name = "TRANSFER-"

ds_volt = 25

init_gate_volt = 1.0
max_gate_volt = 8.0
gate_step = 0.1

# --- Configurações Constantes ---

remote_folder = "/HD-0/Gabriel"
local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios_v2/"

ds_curr = 5.0
gate_curr = 1.0
error_threshold = 1.0

test = Characterization(local_folder, test_name)
test.ftp.connect()
test.current_set(gate_curr, ds_curr)

init_gate_error = 0.61

df_transfer = []
gate_volt = init_gate_volt + init_gate_error

ds_volt = ds_volt + 0.07
ds_target = ds_volt
good_vds = ds_volt
ds_integral = 0.0
ids = 0.0

print(f"----- Starting Transfer Test: {time.time()} -----")

while gate_volt < max_gate_volt + init_gate_error and ids < 130.0:

    try:
        test.send_pulse(gate_volt, ds_volt)

    except pyvisa.VisaIOError:
        print("Error in Sending Pulse")
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
    
        if (abs(vds - ds_target) / ds_target) * 100 > error_threshold:
            print(f"-- High Vds Error. Vds: {vds:.2f} V, Target: {ds_target:.2f} V --")

            if abs(vds - ds_target) < ds_target*0.05:
                ds_error = ds_target - vds
                ds_integral += ds_error
                ds_volt = ds_target + 0.5*ds_error + 0.2*ds_integral
            else:
                ds_volt = good_vds
                ds_integral = 0.0
        
        else:
            print(f"Vg: {vg:.2f} V, Vds: {vds:.2f} V, Ids: {ids:.2f} A")

            df_transfer.append({
            'Arquivo': latest_file_name,
            'Vg': vg,
            'Vds': vds,
            'Ids': ids
            })

            gate_volt += gate_step
            good_vds = ds_volt

test.ftp.close()

test.clear_capacitor()

end = time.time()
print(f"Tempo Total: {(end - start)/60:.2f} minutos")

df_final = pd.DataFrame(df_transfer)
file_final = f"{local_folder}/{test_name}/{test_name}_ALL.csv"

df_final.to_csv(file_final, index=False)

test.data.actual_plot(pd.read_csv(file_final), test_name, test='Transfer')