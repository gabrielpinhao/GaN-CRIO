import time
from itertools import count

# Entradas
try:
    valor_partida = float(input("Digite a corrente de partida (A): "))
    valor_maxima = float(input("Digite a corrente máxima (A): "))
    acrescimo = float(input("Digite o acréscimo (A): "))
except ValueError:
    print("Erro: Digite apenas números.")
    exit()

print("--- INICIANDO TESTE COM FOR INFINITO ---")

try:
    # count(0) gera 0, 1, 2, 3... infinitamente (substitui o range limitado), for mais rapido que while
    for i in count(0):
        
        # Sua fórmula matemática original (Mais precisa para decimais!)
        atual = (i * acrescimo) + valor_partida
        
        # Arredonda por segurança de display/comando
        atual = round(atual, 4)

        if atual > valor_maxima:
            print(f"Limite {valor_maxima}A atingido. Encerrando rampagem.")
            break

        # APLICAR CORRENTE (LIGA)
        print(f"Aplicando: {atual} A")
        # hardware.set_current(atual) <--- SEU COMANDO AQUI
        
        time.sleep(1)

        # PULSO (ZERO)
        print("Zerando...")
        # hardware.set_current(0)     <--- SEU COMANDO AQUI
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\nPARADA MANUAL!")

except Exception as e:
    print(f"\nERRO: {e}")

finally:
    # SEGURANÇA FINAL (Roda sempre)
    print("\n--- SAFETY: Zerando fonte ---")
    # hardware.set_current(0)         <--- SEU COMANDO AQUI
    print("Fim.")
