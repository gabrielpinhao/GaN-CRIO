import pyvisa
import time


class Medidor:
    def __init__(self, endereco_gpib):
        self.rm = pyvisa.ResourceManager()
        self.endereco = endereco_gpib
        self.instrumento = None

    def conectar(self):
        try:
            self.instrumento = self.rm.open_resource(self.endereco)
            self.instrumento.timeout = 5000
            return True
        except pyvisa.VisaIOError:
            return False

    def ler_tensao(self):
        self.instrumento.write("MEAS:VOLT?")
        tensao = self.instrumento.read()
        return float(tensao)

    def ler_corrente(self):
        self.instrumento.write("MEAS:CURR?")
        corrente = self.instrumento.read()
        return float(corrente)

    def fechar(self):
        self.instrumento.close()
        self.rm.close()


