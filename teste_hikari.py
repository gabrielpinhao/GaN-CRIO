from HIKARI_DC import HikariHF3205P  
import time

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