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
            print(f"Conectado a {self.endereco}")
        except pyvisa.VisaIOError:
            print("Erro ao conectar!")


    def ligandoFonte(self):

        try:

            ident = self.instrumento.query('*IDN?')
            self.instrumento.write('*RST')
            self.instrumento.write('VOLT 0.1')
            self.instrumento.write('CURR 0')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            self.instrumento.write('OUTP ON')
            time.sleep(1)

        finally:
            self.instrumento.write('OUTP OFF')
            print("Zerar valores no instrumento...")
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')
            # instrumento.close()
            print("Execução finalizada e instrumento zerado.")

    def controleCorrente(self, corrente_partida, corrente_maxima, acrescimo, toff,ton):

        partida = corrente_partida
        maxima = corrente_maxima
        incremento = acrescimo
        tempo_off = toff
        tempo_ton = ton
        try:
            while True:
                # Ponto de Parada (Break Condition)
                if partida > corrente_maxima:
                    print(f"Corrente máxima de {corrente_maxima}A atingida. Encerrando o ciclo de testes.")
                    break

                # Conversão para String
                comando_curr = f'CURR {partida}'

                print(f"Configurando Tensão: 1V | Corrente: {partida}A")

                self.instrumento.write('VOLT 1')
                self.instrumento.write(comando_curr)  # Usa o valor incrementado
                time.sleep(0.3)

                # Incremento para a próxima iteração
                partida += incremento

                # Bloco de Reset (Zera dentro do ciclo) ---
                self.instrumento.write('VOLT 0.01')
                self.instrumento.write('CURR 0.01')
                time.sleep(0.3)

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

        try:
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
                time.sleep(0.3)

                # Incremento para a próxima iteração
                tensao_partida += acrescimo

                # Bloco de Reset (Zera dentro do ciclo) ---
                self.instrumento.write('VOLT 0.01')
                self.instrumento.write('CURR 0.01')
                time.sleep(0.3)

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

minha_fonte = Fonte('GPIB0::1::INSTR')

minha_fonte.conectar()
minha_fonte.ligandoFonte()