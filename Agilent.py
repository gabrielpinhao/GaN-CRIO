import pyvisa
import time

class Agilent34401A:
    def __init__(self, endereco_gpib):
        self.rm = pyvisa.ResourceManager()
        self.endereco = endereco_gpib
        self.instrumento = None

    def conectar(self):
        try:
            self.instrumento = self.rm.open_resource(self.endereco)
            self.instrumento.timeout = 5000

            self.instrumento.write("*CLS")
            self.instrumento.write("*RST")
            time.sleep(0.5)
            return True
        except pyvisa.VisaIOError as e:
            print(f"Erro de conexão: {e}")
            return False

    def configurar_para_pulsos(self, nplc=1):
        if not self.instrumento:
            return

        try:
            # Configuração de medição DC
            self.instrumento.write("CONF:VOLT:DC")
            self.instrumento.write("VOLT:DC:RANG:AUTO ON")
            self.instrumento.write(f"VOLT:DC:NPLC {nplc}")

            # Trigger por BUS (*TRG)
            self.instrumento.write("TRIG:SOUR BUS")
            self.instrumento.write("TRIG:COUN 1")

            print(f"34401A configurado: NPLC={nplc}, Trigger BUS")
            time.sleep(0.5)

        except Exception as e:
            print(f"Erro na configuração: {e}")

    # ---- LOOP DE PULSO ----

    def armar_leitura(self):
        self.instrumento.write("INIT")

    def disparar_gatilho(self):
        self.instrumento.write("*TRG")

    def coletar_resultado(self):
        try:
            leitura = self.instrumento.query("FETCH?")
            return float(leitura)
        except Exception as e:
            print(f"Erro ao coletar dados: {e}")
            return None

    def desconectar(self):
        if self.instrumento:
            try:
                self.instrumento.write("SYST:LOC")
            except:
                pass
            self.instrumento.close()
            print("Instrumento desconectado.")
        self.rm.close()

