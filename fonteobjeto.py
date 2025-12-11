import pyvisa
import time

#Criar a classe para importamos na interface depois
class Fonte:
    def __init__(self,endereco_gpib): #colocar endereco gpib
        self.rm = pyvisa.ResourceManager()
        self.endereco = endereco_gpib
        self.instrumento = None

    def conectar(self):
        try:
            self.instrumento = self.rm.open_resource(self.endereco)
            self.instrumento.timeout = 5000
            return True
        except pyvisa.VisaIOError or con == False:
            return False

# funçao de teste não funciona, verificar porque depois
    def teste(self):

        try:
            ident = self.instrumento.query('*IDN?')
            self.instrumento.write('*RST')
            self.instrumento.write('OUTP ON')
            self.instrumento.write('VOLT 0.1')
            self.instrumento.write('CURR 0')
            time.sleep(3)
            self.instrumento.write('VOLT 0.1')
            self.instrumento.write('CURR 1')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            time.sleep(3)

        finally:
            self.instrumento.write('OUTP OFF')
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')
            print("Zerar valores no instrumento...")
            # instrumento.close()
            print("Execução finalizada e instrumento zerado.")

    def controleCorrente(self, corrente_partida, corrente_maxima, acrescimo, ton,toff):

        tempo_on = float(ton)
        tempo_off = float(toff)

        try:

            ident = self.instrumento.query('*IDN?')
            self.instrumento.write('*RST')
            self.instrumento.write('VOLT 0.1')
            self.instrumento.write('CURR 0.01')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            self.instrumento.write('OUTP ON')
            time.sleep(1)


            while True:
                # Ponto de Parada (Break Condition)
                if corrente_partida > corrente_maxima:
                    print(f"Corrente máxima de {corrente_maxima}A atingida. Encerrando o ciclo de testes.")
                    break

                # Conversão para String
                comando_curr = f'CURR {corrente_partida}'

                print(f"Configurando Tensão: 1V | Corrente: {corrente_partida}A")

                self.instrumento.write('VOLT 1')
                self.instrumento.write(comando_curr)  # Usa o valor incrementado
                time.sleep(tempo_on/2)  # Tempo para estabilização antes da medição
                # Incremento para a próxima iteração
                corrente_partida += acrescimo

                time.sleep(tempo_on/2) #Ton

                # Bloco de Reset (Zera dentro do ciclo) ---
                self.instrumento.write('VOLT 0.01')
                self.instrumento.write('CURR 0.01')
                time.sleep(tempo_off) #Toff

        except KeyboardInterrupt:
            print("\nInterrupção detectada. Prosseguindo para zerar os valores...")

        finally:
            # Rotina de segurança
            # Desligar Saída
            self.instrumento.write('OUTP OFF')
            print("Zerar valores no instrumento...")
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')

            # instrumento.close()
            print("Execução finalizada e instrumento zerado.")

    def controleTensao(self, tensao_partida, tensao_maxima, acrescimo, toff,ton):

        tempo_on = float(ton)
        tempo_off = float(toff)

        try:
            ident = self.instrumento.query('*IDN?')
            self.instrumento.write('*RST')
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0.1')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            self.instrumento.write('OUTP ON')
            time.sleep(1)

            while True:
                # Ponto de Parada (Break Condition)
                if tensao_partida > tensao_maxima:
                    print(f"Tensão máxima de {tensao_maxima}V atingida. Encerrando o ciclo de testes.")
                    break

                # Conversão para String
                comando_tensao = f'CURR {tensao_partida}'

                print(f"Configurando Tensão: 1V | Corrente: {tensao_partida}A")

                self.instrumento.write('VOLT 1')
                self.instrumento.write(comando_tensao)  # Usa o valor incrementado
                time.sleep(tempo_on)

                # Incremento para a próxima iteração
                tensao_partida += acrescimo

                # Bloco de Reset (Zera dentro do ciclo) ---
                self.instrumento.write('VOLT 0.01')
                self.instrumento.write('CURR 0.01')
                time.sleep(tempo_off)

        except KeyboardInterrupt:
            print("\nInterrupção detectada. Prosseguindo para zerar os valores...")

        finally:
            # Rotina de segurança
            # Desligar Saída
            self.instrumento.write('OUTP OFF')
            print("Zerar valores no instrumento...")
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')

            # instrumento.close()
            print("Execução finalizada e instrumento zerado.")

    def seguranca(self):

        self.instrumento.write('OUTP OFF')
        self.instrumento.write('VOLT 0')
        self.instrumento.write('CURR 0')
        self.instrumento.close()


