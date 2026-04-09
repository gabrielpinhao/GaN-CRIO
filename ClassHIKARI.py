import pyvisa
import time

class HikariHF3205P:
    def __init__(self, resource="ASRL3::INSTR"):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource)
        self.inst.baud_rate = 9600
        self.inst.data_bits = 8
        self.inst.parity = pyvisa.constants.Parity.none
        self.inst.stop_bits = pyvisa.constants.StopBits.one
        self.inst.timeout = 2000
        self.inst.write_termination = "\n"
        self.inst.read_termination = "\n"

    def _query_fixed(self, cmd, nbytes=5, delay=0.1):
        self.inst.write(cmd)
        time.sleep(delay)
        return self.inst.read_bytes(nbytes).decode(errors="ignore").strip()

    def _query_text(self, cmd, delay=0.1):
        self.inst.write(cmd)
        time.sleep(delay)
        return self.inst.read().strip()

    def idn(self):
        return self._query_text("*IDN?")

    def set_voltage(self, value):
        self.inst.write(f"VSET1:{value:0.2f}")

    def get_voltage_set(self):
        return float(self._query_fixed("VSET1?", 5))

    def set_current(self, value):
        self.inst.write(f"ISET1:{value:0.3f}")

    def get_current_set(self):
        return float(self._query_fixed("ISET1?", 5))

    def output_on(self):
        self.inst.write("OUT1")

    def output_off(self):
        self.inst.write("OUT0")

    def ocp_on(self):
        self.inst.write("OCP1")

    def ocp_off(self):
        self.inst.write("OCP0")

    def ovp_on(self):
        self.inst.write("OVP1")

    def ovp_off(self):
        self.inst.write("OVP0")

    def close(self):
        self.inst.close()

def main():
    psu = HikariHF3205P()

    try:
        print("Fonte conectada:", psu.idn())

        print("Configurando tensão para 10 V...")
        psu.set_voltage(10.00)

        print("Configurando corrente para 1 A...")
        psu.set_current(1.000)

        time.sleep(0.2)

        print("Ligando saída...")
        psu.output_on()

        print("Fonte configurada com sucesso.")

        time.sleep(5)

    finally:
        if psu is not None:
            try:
                print("Desligando saída...")
                psu.output_off()
                time.sleep(0.1)
            except Exception as e:
                print("Erro ao desligar saída:", e)

            try:
                print("Encerrando comunicação...")
                psu.close()
            except Exception as e:
                print("Erro ao fechar conexão:", e)

if __name__ == "__main__":
    main()