import pyvisa
import time

class VoltimetroK2182A:
    def __init__(self, endereco_gpib):
        self.rm = pyvisa.ResourceManager()
        self.endereco = endereco_gpib
        self.instrumento = None

    def conectar(self):
        try:
            self.instrumento = self.rm.open_resource(self.endereco)
            self.instrumento.timeout = 5000 
            
            # Reset inicial
            self.instrumento.write("*CLS")
            self.instrumento.write("*RST")
            time.sleep(0.5) # Tempo para o reset processar
            return True
        except pyvisa.VisaIOError as e:
            print(f"Erro de conexão: {e}")
            return False

    def configurar_para_pulsos(self, nplc=1):
        """
        Configura o aparelho UMA VEZ para o modo de Trigger via Software.
        Isso evita atrasos reconfigurando o aparelho a cada pulso.
        """
        if not self.instrumento:
            return

        try:
            # 1. Configurações de Medição
            self.instrumento.write(":SENS:FUNC 'VOLT'")
            self.instrumento.write(":SENS:CHAN 1")
            self.instrumento.write(f":SENS:VOLT:DC:NPLC {nplc}")
            self.instrumento.write(":SENS:VOLT:DC:RANG:AUTO ON")
            
            # 2. Configuração Crítica para Pulsos (Trigger)
            # Define que o trigger virá pelo comando *TRG (BUS) e não automático
            self.instrumento.write(":TRIG:SOUR BUS") 
            self.instrumento.write(":TRIG:DEL 0") # Sem atraso artificial
            
            print(f"Configurado: NPLC {nplc}, Trigger BUS.")
            time.sleep(1) # Garante que a config foi aplicada
        except Exception as e:
            print(f"Erro na configuração: {e}")

    # --- MÉTODOS GRANULARES PARA O LOOP DE PULSO ---

    def armar_leitura(self):
        """Passo 1: Coloca o voltímetro em estado de espera (Wait for Trigger)"""
        # O display do K2182 geralmente mostra um indicador de espera ou para de atualizar
        self.instrumento.write(":INIT")

    def disparar_gatilho(self):
        """Passo 2: Envia o sinal para medir AGORA"""
        # A latência deste comando é muito menor que um :READ?
        self.instrumento.write("*TRG")

    def coletar_resultado(self):
        """Passo 3: Busca o valor na memória após a medição"""
        try:
            leitura = self.instrumento.query(":FETCH?")
            return float(leitura)
        except Exception as e:
            print(f"Erro ao coletar dados: {e}")
            return None

    def desconectar(self):
        if self.instrumento:
            # Tenta voltar para modo local antes de fechar
            try:
                self.instrumento.write(":SYST:LOC")
            except:
                pass
            self.instrumento.close()
            print("Instrumento desconectado.")
        self.rm.close()

k2182a = VoltimetroK2182A("GPIB0::7::INSTR")
k2182a.conectar()
k2182a.configurar_para_pulsos(nplc=1)
k2182a.armar_leitura()
time.sleep(0.2)  # Simula o tempo em que a fonte está ligada
k2182a.disparar_gatilho()
tensao = k2182a.coletar_resultado()
print(f"Tensão medida: {tensao} V")
k2182a.desconectar()


# ==========================================
# EXEMPLO DE USO COM FONTE PULSADA (SIMULADO)
# ==========================================

# 1. Setup
#k2182a = VoltimetroK2182A("GPIB0::7::INSTR")

#if k2182a.conectar():
    # Configura APENAS UMA VEZ antes do loop
    #k2182a.configurar_para_pulsos(nplc=1) 
    
    #print("\nIniciando sequência de pulsos...")
    
    # Vamos simular 5 pulsos
    #for i in range(5):
        #print(f"--- Pulso {i+1} ---")
        
        # [A] ARMAR: O voltímetro fica pronto antes do pulso começar
        #k2182a.armar_leitura()
        
        # [B] FONTE ON (Aqui entra seu código da Fonte de Corrente)
        # fonte.write("OUTPUT ON") 
        #print("  >> Fonte LIGADA")
        
        # Pequeno delay para a corrente estabilizar (Settling time)
        #time.sleep(0.05) 
        
        # [C] DISPARAR: Mede exatamente no platô do pulso
        #k2182a.disparar_gatilho()
        
        # Aguarda o tempo da medição (NPLC 1 ~ 17ms + margem)
        #time.sleep(0.05) 
        
        # [D] FONTE OFF
        # fonte.write("OUTPUT OFF")
        #print("  >> Fonte DESLIGADA")
        
        # [E] COLETAR: Pega o dado com calma
        #valor = k2182a.coletar_resultado()
        #print(f"  Resultado: {valor:.9f} V")
        
        # Tempo OFF do pulso (espera antes do próximo)
        #time.sleep(0.5)

    #k2182a.desconectar()