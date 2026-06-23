import serial
import time
import sys

class ControladorESP32:
    def __init__(self, porta_com, velocidade=115200):
        """
        Inicializa o objeto e tenta conectar ao ESP32.
        """
        self.porta_com = porta_com
        self.velocidade = velocidade
        self.conexao = None

    def conectar(self):
        """Estabelece a conexão serial com o ESP32."""
        try:
            self.conexao = serial.Serial(self.porta_com, self.velocidade)
            time.sleep(2)  # Dá um tempinho para o ESP32 reiniciar após conectar
            print(f"Conectado ao ESP32 na porta {self.porta_com} com sucesso!")
        except Exception as e:
            print(f"Erro ao conectar na porta {self.porta_com}. O cabo está ligado?")
            print(f"Erro detalhado: {e}")
            sys.exit()

    def enviar_pulso(self):
        """Envia o comando de pulso rápido (80us)."""
        if self.conexao and self.conexao.is_open:
            self.conexao.write(b'1')
            print("Comando PULSO enviado.")
        else:
            print("Erro: Conexão serial fechada ou inexistente.")

    def desligar(self):
        """Envia o comando para desligar (0V)."""
        if self.conexao and self.conexao.is_open:
            self.conexao.write(b'0')
            print("Comando DESLIGAR enviado.")
        else:
            print("Erro: Conexão serial fechada ou inexistente.")

    def ligar(self):
        """Envia o comando para ligar estado alto (3.3V)."""
        if self.conexao and self.conexao.is_open:
            self.conexao.write(b'2')
            print("Comando LIGAR enviado.")
        else:
            print("Erro: Conexão serial fechada ou inexistente.")
            
    def enviar_heartbeat(self):
        """Envia o sinal de vida para o sistema fail-safe do ESP32."""
        if self.conexao and self.conexao.is_open:
            self.conexao.write(b'H')

    def desconectar(self):
        """Fecha a conexão serial com segurança."""
        if self.conexao and self.conexao.is_open:
            self.conexao.close()
            print("Conexão com ESP32 encerrada.")

# ==========================================
# EXEMPLO DE COMO USAR A CLASSE NO SEU CÓDIGO
# ==========================================

if __name__ == "__main__":
    # 1. Criando o objeto (isso já executa a conexão automaticamente)
    meu_esp32 = ControladorESP32(porta_com='COM4')
    meu_esp32.conectar()

    # 2. Chamando os métodos do objeto
    meu_esp32.ligar()
    time.sleep(5)
    
    meu_esp32.enviar_pulso()
    time.sleep(5)
    
    meu_esp32.desligar()

    # 3. Sempre é bom desconectar ao fechar o programa
    meu_esp32.desconectar()