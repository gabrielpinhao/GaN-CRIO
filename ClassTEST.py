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
        self.scope_yoko = YokogawaDL850(yoko_address)

        os.makedirs(f"{local_folder}/{test_name}", exist_ok=True)
        print(self.rm.list_resources())

        try:
            if self.scope_yoko.scope.query('*IDN?').strip():
                print("Osciloscópio já conectado:", self.scope_yoko.scope.query('*IDN?').strip())
            else:
                self.scope_yoko.conectar()
                self.scope_yoko.configurar_aquisicao()
                print("Osciloscópio conectado:", self.scope_yoko.scope.query('*IDN?').strip())

        except Exception as e:
            print(f"Erro ao conectar ao osciloscópio: {e}")
            exit()

        for resource in self.rm.list_resources():
            try:
                inst = self.rm.open_resource(resource)
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

    def send_pulse(self, gate_volt, ds_volt, test_name):

        self.scope_yoko.measure_start()

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

        self.scope_yoko.measure_save(test_name)

    def clear_capacitor(self):

        self.gate_source.set_voltage(5.0)
        self.drain_source.output_off()
        time.sleep(0.5)
        self.gate_source.output_on()
        time.sleep(3)
        self.gate_source.output_off()
