from HIKARI_DC import HikariHF3205P  
from YOKOclass import YokogawaDL850     
import time

psu = HikariHF3205P(resource="ASRL5::INSTR")
scope_yoko = YokogawaDL850()

try:
    print("Fonte conectada:", psu.idn())
    scope_yoko.conectar()
    print("Osciloscópio conectado:", scope_yoko.scope.query('*IDN?').strip())
    scope_yoko.configurar_aquisicao()
    time.sleep(0.5)


    psu.set_voltage(10.00)
    psu.set_current(1.000)

    time.sleep(0.2)
    scope_yoko.measure_start()
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
            scope_yoko.scope.close()
        except Exception as e:
            print("Erro ao fechar conexão:", e)