// Caracterizacao de duplo pulso
// Pulso: HIGH -> LOW -> HIGH -> LOW
// Padrao: LOW (0V) em repouso

#include <Arduino.h>

#define PINO_SAIDA 23

void setup() {
  Serial.begin(115200);
  pinMode(PINO_SAIDA, OUTPUT);
  digitalWrite(PINO_SAIDA, LOW);
}

void duplo_pulso(unsigned int p1_us, unsigned int delay_us, unsigned int p2_us) {
  digitalWrite(PINO_SAIDA, HIGH);
  delayMicroseconds(p1_us);

  digitalWrite(PINO_SAIDA, LOW);
  delayMicroseconds(delay_us);

  digitalWrite(PINO_SAIDA, HIGH);
  delayMicroseconds(p2_us);

  digitalWrite(PINO_SAIDA, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.peek();

    if (comando == '0') {
      Serial.read();
      digitalWrite(PINO_SAIDA, LOW);
    }
    else if (comando == '2') {
      Serial.read();
      digitalWrite(PINO_SAIDA, HIGH);
    }
    else if (comando == '1') {
      Serial.read();
      duplo_pulso(80, 0, 0);
    }
    else if (comando == 'P') {
      Serial.read();
      char buffer[64];
      int len = Serial.readBytesUntil('\n', buffer, sizeof(buffer) - 1);
      if (len > 0) {
        buffer[len] = '\0';
        unsigned int p1, delay_us, p2;
        if (sscanf(buffer, "%u,%u,%u", &p1, &delay_us, &p2) == 3) {
          duplo_pulso(p1, delay_us, p2);
        }
      }
    }
    else {
      Serial.read();
    }
  }
}
