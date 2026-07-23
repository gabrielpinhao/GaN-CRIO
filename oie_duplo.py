import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports
import time

PORTA_COM = 'COM4'
VELOCIDADE = 115200


class ControleDuploPulso:
    def __init__(self):
        self.esp32 = None
        self._conectar()

        self.janela = tk.Tk()
        self.janela.title("Controle ESP32 - Pulso Duplo")
        self.janela.geometry("350x320")
        self.janela.eval('tk::PlaceWindow . center')

        tk.Label(self.janela, text="Controle Pulso Duplo",
                 font=("Arial", 14, "bold")).pack(pady=10)

        frame = tk.LabelFrame(self.janela, text="Configuracao dos Pulsos", padx=10, pady=10)
        frame.pack(pady=10, padx=15, fill="x")

        tk.Label(frame, text="Pulso 1 (us):").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_p1 = tk.Entry(frame, width=12)
        self.entry_p1.grid(row=0, column=1, pady=2)
        self.entry_p1.insert(0, "20")

        tk.Label(frame, text="Delay (us):").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_delay = tk.Entry(frame, width=12)
        self.entry_delay.grid(row=1, column=1, pady=2)
        self.entry_delay.insert(0, "1000")

        tk.Label(frame, text="Pulso 2 (us):").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_p2 = tk.Entry(frame, width=12)
        self.entry_p2.grid(row=2, column=1, pady=2)
        self.entry_p2.insert(0, "20")

        btn_pulso = tk.Button(frame, text="Enviar Pulso Duplo", bg="#4CAF50", fg="white",
                              font=("Arial", 11, "bold"), width=22, command=self._pulso_duplo)
        btn_pulso.grid(row=3, column=0, columnspan=2, pady=12)

        frame2 = tk.LabelFrame(self.janela, text="Controles Manuais", padx=10, pady=10)
        frame2.pack(pady=10, padx=15, fill="x")

        btn_on = tk.Button(frame2, text="ON", bg="#2196F3", fg="white",
                           font=("Arial", 12, "bold"), width=10, command=self._ligar)
        btn_on.grid(row=0, column=0, padx=8, pady=5)

        btn_off = tk.Button(frame2, text="OFF", bg="#f44336", fg="white",
                            font=("Arial", 12, "bold"), width=10, command=self._desligar)
        btn_off.grid(row=0, column=1, padx=8, pady=5)

        self.label_status = tk.Label(self.janela, text="Conectado", fg="green",
                                     font=("Arial", 9))
        self.label_status.pack(pady=5)

        self.janela.protocol("WM_DELETE_WINDOW", self._fechar)

    def _conectar(self):
        try:
            self.esp32 = serial.Serial(PORTA_COM, VELOCIDADE)
            time.sleep(2)
            print(f"Conectado ao ESP32 na porta {PORTA_COM}")
        except Exception as e:
            messagebox.showwarning(
                "Erro de Conexao",
                f"Falha ao conectar na porta {PORTA_COM}.\n"
                f"Verifique se o cabo esta conectado.\n\nErro: {e}"
            )
            self.esp32 = None

    def _validar_campos(self):
        try:
            p1 = int(self.entry_p1.get())
            delay = int(self.entry_delay.get())
            p2 = int(self.entry_p2.get())
            if p1 <= 0 or delay <= 0 or p2 <= 0:
                raise ValueError("Valores devem ser positivos.")
            return p1, delay, p2
        except ValueError as e:
            messagebox.showerror("Erro de Validacao", str(e))
            return None, None, None

    def _enviar(self, dados):
        if self.esp32 and self.esp32.is_open:
            try:
                self.esp32.write(dados)
                self.esp32.flush()
                return True
            except Exception as e:
                print(f"Erro ao enviar: {e}")
                return False
        else:
            messagebox.showwarning("Sem Conexao", "ESP32 nao esta conectado.")
            return False

    def _pulso_duplo(self):
        p1, delay, p2 = self._validar_campos()
        if p1 is None:
            return
        comando = f"P{p1},{delay},{p2}\n"
        if self._enviar(comando.encode()):
            self.label_status.config(
                text=f"Pulso: {p1}us / {delay}us / {p2}us", fg="blue")
            print(f"Comando enviado: {comando.strip()}")

    def _ligar(self):
        if self._enviar(b'2'):
            self.label_status.config(text="ON", fg="green")
            print("Comando ON enviado.")

    def _desligar(self):
        if self._enviar(b'0'):
            self.label_status.config(text="OFF", fg="red")
            print("Comando OFF enviado.")

    def _fechar(self):
        if self.esp32 and self.esp32.is_open:
            self.esp32.write(b'0')
            self.esp32.flush()
            self.esp32.close()
            print("Conexao encerrada.")
        self.janela.destroy()

    def iniciar(self):
        self.janela.mainloop()


if __name__ == "__main__":
    app = ControleDuploPulso()
    app.iniciar()
