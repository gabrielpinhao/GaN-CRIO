import pyvisa
import time


class Voltimetro:
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
            return True
        except pyvisa.VisaIOError:
            return False

    def ler_tensao(self):
        self.instrumento.write("SENS:FUNC 'VOLT'")
        self.instrumento.write('SENS:CHAN: 1')
        self.instrumento.write(':SENS:VOLT:DC:NPLC 1')
        self.instrumento.write(':SENS:VOLT:DC:RANG:AUTO ON')
        time.sleep(1)  # Aguarde um breve momento para garantir que as configurações sejam aplicadas
        
        try:
            leitura = self.instrumento.query(':READ?')
            return float(leitura)
        except pyvisa.VisaIOError as e:
            print(f"Erro ao ler tensão: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
        


    def ler_corrente(self):
        self.instrumento.write("MEAS:CURR?")
        corrente = self.instrumento.read()
        return float(corrente)

    def desconectar(self):
        if self.instrumento:
            self.instrumento.close()
            self.instrumento = None # Boa prática limpar a variável
            print("Instrumento desconectado.")


rm = pyvisa.ResourceManager()
resources = rm.list_resources()

print("Recursos GPIB disponíveis:")
for resource in resources:
    print(resource)

# GPIB0::7::INSTR
k2182a = Voltimetro("GPIB0::7::INSTR")

k2182a.conectar()
tensao = k2182a.ler_tensao()
print(f"Tensão medida: {tensao} V")
k2182a.desconectar()
