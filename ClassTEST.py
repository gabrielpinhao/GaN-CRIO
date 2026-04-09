import os
import time
import pyvisa
import pandas as pd
from ClassHIKARI import HikariHF3205P
from ClassYOKO import YokogawaDL850  
from ClassFTP import FTPDownloader
from ClassDATA import DATAclass

class Characterization:

    def __init__(self, local_folder, test_name, yoko_address="TCPIP0::192.168.1.131::INSTR"):
        self.data = DATAclass()
        self.ftp = FTPDownloader()
        self.rm = pyvisa.ResourceManager()
        self.yoko = YokogawaDL850(yoko_address)
        self.resources = self.rm.list_resources()
        self.local_folder = local_folder
        self.timeout = 60000

        os.makedirs(f"{local_folder}/{test_name}", exist_ok=True)

        try:
            self.yoko.conectar()
            self.yoko.configurar_aquisicao()

        except Exception as e:
            print(f"Erro ao conectar ao osciloscópio: {e}")

        for r in self.resources:
            try:
                inst = self.rm.open_resource(r)
                idn = inst.query('*IDN?').strip()
                print(f"{r}: SN:{idn[-8:]}")

                if int(idn[-8:]) == 49152063:
                    self.gate_source = HikariHF3205P(resource=r)
                    print("Fonte conectada:", self.gate_source.idn())

                elif int(idn[-8:]) == 9437206:
                    self.drain_source = HikariHF3205P(resource=r)
                    print("Fonte conectada:", self.drain_source.idn())

            except Exception as e:
                print(f"Error loading {r}: {e}")
                
        time.sleep(0.5)

    def send_pulse(self, gate_volt, ds_volt, test_name):
        
        self.yoko.measure_start()
    
        self.drain_source.set_voltage(ds_volt)
        self.gate_source.set_voltage(gate_volt)
      
        time.sleep(0.5)
      
        self.drain_source.output_on()
        time.sleep(5)
        self.drain_source.output_off()
        time.sleep(0.5)
        self.gate_source.output_on()
        time.sleep(0.08)
        self.gate_source.output_off()
      
        self.yoko.measure_save(test_name)


    def clear_capacitor(self):

        print("Discharging Capacitor...")
        self.gate_source.set_voltage(3.0)
        self.drain_source.set_voltage(2.0)
        self.drain_source.output_off()
        time.sleep(0.5)
        self.gate_source.output_on()
        time.sleep(5)
        self.gate_source.output_off()

    def current_set(self, gate_curr, ds_curr):
        self.gate_source.set_current(gate_curr)
        self.drain_source.set_current(ds_curr)
    

if __name__ == "__main__":
    test_name = "MOS8_OUTPUT"
    local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"

    test = Characterization(local_folder, test_name)
    test.send_pulse(gate_volt=5.0, ds_volt=2.0, test_name=test_name)
    test.clear_capacitor()

