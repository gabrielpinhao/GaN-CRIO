// Para Caracterização estática
#include <Arduino.h>

#define PINO_SAIDA 19 

void setup() {
  Serial.begin(115200);         // Inicia a comunicação serial
  pinMode(PINO_SAIDA, OUTPUT);  // Configura o pino como saída

  // Inicializa o pino em LOW (0.0V) por padrão
  digitalWrite(PINO_SAIDA, LOW); 
}

void loop() {
  // Verifica se chegou algo do notebook
  if (Serial.available() > 0) {
    char comando = Serial.read(); // Lê o caractere enviado pelo Python

    // Comando '1': Executa o pulso rápido de 80 microssegundos
    if (comando == '1') {
      digitalWrite(PINO_SAIDA, HIGH);   // Desliga (0V)
      delayMicroseconds(120);           // Aguarda 80us
      digitalWrite(PINO_SAIDA, LOW);  // Liga de novo (3.3V)
    } 
    
    // Comando '0': Desliga a saída e mantém em 0V
    else if (comando == '0') {
      digitalWrite(PINO_SAIDA, LOW); 
    } 
    
    // Comando '2': Liga a saída e mantém em 3.3V (Estado Alto)
    else if (comando == '2') {
      digitalWrite(PINO_SAIDA, HIGH); 
    }
  }
}