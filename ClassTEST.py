import os
import time
import pyvisa
import pandas as pd
import serial
import sys
from ClassHIKARI import HikariHF3205P
from ClassYOKO import YokogawaDL850  
from ClassFTP import FTPDownloader
from ClassDATA import DATAclass
from ClassESP32 import ControladorESP32

class Characterization:

    def __init__(self, local_folder, test_name, yoko_address="TCPIP0::192.168.1.131::INSTR"):
        
        self.data = DATAclass()
        self.ftp = FTPDownloader()
        self.rm = pyvisa.ResourceManager()
        self.yoko = YokogawaDL850(yoko_address)
        self.esp32 = ControladorESP32(porta_com='COM4')
        self.resources = self.rm.list_resources()
        self.local_folder = local_folder
        self.timeout = 60000

        os.makedirs(f"{local_folder}/{test_name}", exist_ok=True)
        
        try:
            print("ENTROU NO TRY")
            self.esp32.conectar()
            self.yoko.conectar()
            self.yoko.configurar_aquisicao(test_name)

        except Exception as e:
            print(f"Erro ao conectar ao osciloscópio: {e}")

        for r in self.resources:
            inst = None
            try:
                inst = self.rm.open_resource(r)
                idn = inst.query('*IDN?').strip()
                print(f"{r}: SN:{idn[-8:]}")

                sn = int(idn[-8:])

                if sn == 9437206:
                    inst.close()
                    inst = None
                    self.drain_source = HikariHF3205P(resource=r)
                    print("Fonte conectada:", self.drain_source.idn())

            except Exception as e:
                print(f"Error loading {r}: {e}")
            finally:
                if inst is not None:
                    try:
                        inst.close()
                    except Exception:
                        pass
                
        time.sleep(0.5)

    def send_pulse(self, ds_volt):
        
        self.yoko.measure_start()
    
        self.drain_source.set_voltage(ds_volt)
      
        time.sleep(0.5)
      
        self.drain_source.output_on()
        time.sleep(5)
        self.drain_source.output_off()
        time.sleep(0.5)
        self.esp32.enviar_pulso()
        time.sleep(0.1)
        
      
        self.yoko.measure_save()


    def clear_capacitor(self):
        print("Discharging Capacitor...")
        #self.gate_source.set_voltage(4.0)
        self.drain_source.set_voltage(2.0)
        self.drain_source.output_off()
        time.sleep(0.5)
        #self.gate_source.output_on()
        self.esp32.ligar()
        time.sleep(10)
        self.esp32.desligar()
        #self.gate_source.output_off()
        

    def current_set(self, ds_curr):
        #self.gate_source.set_current(gate_curr)
        self.drain_source.set_current(ds_curr)
    

if __name__ == "__main__":
    test_name = "MOS8_OUTPUT"
    local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"

    test = Characterization(local_folder, test_name)
    test.send_pulse(ds_volt=2.0, test_name=test_name)
    test.clear_capacitor()

