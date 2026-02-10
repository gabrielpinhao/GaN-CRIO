import pyvisa
import time
from itertools import count

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
        except pyvisa.VisaIOError:
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
            self.instrumento.write('VOLT 3.0')
            self.instrumento.write('CURR 0.01')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            self.instrumento.write('OUTP ON')
            time.sleep(1)


            for i in count(0):

                inicio = time.perf_counter()
        
                # Sua fórmula matemática original (Mais precisa para decimais!)
                atual = (i * acrescimo) + corrente_partida
                
                # Arredonda por segurança de display/comando
                atual = round(atual, 4)

                if atual > corrente_maxima:
                    print(f"Limite {corrente_maxima}A atingido. Encerrando rampagem.")
                    break

                # APLICAR CORRENTE (LIGA)

                comando_curr = f'CURR {atual}'
                print(f"Corrente atual: {atual}A")

                self.instrumento.write('VOLT 3.0')
                self.instrumento.write(comando_curr)
                
                time.sleep(ton)

                # PULSO (ZERO)
                print("Zerando...")

                fim = time.perf_counter()
                print(f"Tempo do ciclo: {fim - inicio:.4f} segundos\n")

                # APLICAR ZERO (DESLIGA)
                self.instrumento.write('VOLT 3.0')
                self.instrumento.write('CURR 0.01')
                # hardware.set_current(0)     <--- SEU COMANDO AQUI
                
                time.sleep(toff)

        except KeyboardInterrupt:
            print("\nInterrupção detectada. Prosseguindo para zerar os valores...")
        
        except Exception as e:
            print(f"\nERRO: {e}")

        finally:
            # Rotina de segurança
            # Desligar Saída
             # SEGURANÇA FINAL (Roda sempre)
            print("\n--- SAFETY: Zerando fonte ---")
            self.instrumento.write('OUTP OFF')
            print("Zerar valores no instrumento...")
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')
            self.instrumento.close()
            print("Fim.")
            print("Execução finalizada e instrumento zerado.")

    def controleTensao(self, tensao_partida, tensao_maxima, acrescimo, toff,ton, corrente_limite):

        tempo_on = float(ton)
        tempo_off = float(toff)

        try:
            ident = self.instrumento.query('*IDN?')
            self.instrumento.write('*RST')
            self.instrumento.write('VOLT 0')
            self.instrumento.write('CURR 0')
            set_curr = self.instrumento.query('CURR?')
            set_volt = self.instrumento.query('VOLT?')
            self.instrumento.write('OUTP ON')
            time.sleep(1)

            self.instrumento.write(f'CURR {corrente_limite}')
            
            for i in count(0):
                inicio = time.perf_counter()
        
        # Sua fórmula matemática original (Mais precisa para decimais!)
                atual = (i * acrescimo) + tensao_partida
        
        # Arredonda por segurança de display/comando
                atual = round(atual, 4)

                if atual > tensao_maxima or atual > 5.0:
                    print(f"Limite {tensao_maxima}V atingido. Encerrando rampagem.")
                    break

                # APLICAR CORRENTE (LIGA)

                comando_tensao = f'VOLT {atual}' # controle Tensão
                print(f"Tensão atual: {atual}V")

                self.instrumento.write(comando_tensao)

                time.sleep(ton)  # Tempo ON

                fim = time.perf_counter()
                tempo_ciclo = fim - inicio

                # PULSO (ZERO)
                print("Zerando...")


                print(f"Tempo do ciclo: {tempo_ciclo:.4f} segundos\n")

                # APLICAR ZERO (DESLIGA)
                self.instrumento.write('VOLT 0')
                # hardware.set_current(0)     <--- SEU COMANDO AQUI
                
                time.sleep(toff) # Tempo OFF
                
            self.instrumento.write('CURR 0')



        except KeyboardInterrupt:
            print("\nInterrupção detectada. Prosseguindo para zerar os valores...")

        finally:
            # Rotina de segurança
            # Desligar Saída
            self.instrumento.write('OUTP OFF')
            print("Zerar valores no instrumento...")
            self.instrumento.write('VOLT 3.0')
            self.instrumento.write('CURR 0')

            # instrumento.close()
            print("Execução finalizada e instrumento zerado.")

    def seguranca(self):

        self.instrumento.write('OUTP OFF')
        self.instrumento.write('VOLT 0')
        self.instrumento.write('CURR 0')
        self.instrumento.close()
