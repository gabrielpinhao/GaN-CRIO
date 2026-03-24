from HIKARI_DC import HikariHF3205P  
import time

psu = HikariHF3205P(resource="ASRL5::INSTR")

try:
    print("Fonte conectada:", psu.idn())

    psu.set_voltage(10.00)
    psu.set_current(1.000)

    time.sleep(0.2)

    psu.output_on()
    time.sleep(0.05)

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