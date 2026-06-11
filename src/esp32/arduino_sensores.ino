/*
 * arduino_sensores.ino - FarmTech Solutions / Fase 4 CAP 1
 * Issue #9 (ESP32/Wokwi) - Coleta de dados via sensores.
 *
 * Le tres grandezas do campo e publica no Serial em formato JSON, prontas para
 * serem ingeridas pelo pipeline (load_to_sql.py / simulacao):
 *   - DHT22  : temperatura (C) e umidade (%)
 *   - LDR    : luminosidade (mapeada para 0..100000 lux)
 *   - pH     : potenciometro simula o sensor de pH (0..14)
 *
 * Plataforma: ESP32 (DOIT DevKit V1). Testado no simulador Wokwi.
 */

#include <DHT.h>

// ----- Pinos -----
#define PINO_DHT    15      // DHT22 (digital)
#define PINO_LDR    34      // LDR   (entrada analogica, ADC1)
#define PINO_PH     35      // potenciometro = sensor de pH (entrada analogica, ADC1)

#define TIPO_DHT    DHT22

DHT dht(PINO_DHT, TIPO_DHT);

const int   ADC_MAX     = 4095;    // ESP32: ADC de 12 bits
const float LUX_MAX     = 100000;  // teto de luminosidade
const long  INTERVALO   = 2000;    // ms entre leituras

void setup() {
  Serial.begin(115200);
  dht.begin();
  analogReadResolution(12);
  Serial.println("FarmTech ESP32 - coleta de sensores iniciada");
}

void loop() {
  float temperatura = dht.readTemperature();   // C
  float umidade     = dht.readHumidity();      // %

  int leituraLdr = analogRead(PINO_LDR);
  float luminosity = (leituraLdr / (float)ADC_MAX) * LUX_MAX;   // 0..100000 lux

  int leituraPh = analogRead(PINO_PH);
  float ph = (leituraPh / (float)ADC_MAX) * 14.0;              // 0..14

  // Descarta leitura invalida do DHT (NaN)
  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("{\"erro\":\"falha na leitura do DHT22\"}");
    delay(INTERVALO);
    return;
  }

  // Publica em JSON (uma linha por leitura)
  Serial.print("{\"temperatura\":");
  Serial.print(temperatura, 1);
  Serial.print(",\"umidade\":");
  Serial.print(umidade, 1);
  Serial.print(",\"ph\":");
  Serial.print(ph, 2);
  Serial.print(",\"luminosity\":");
  Serial.print(luminosity, 0);
  Serial.println("}");

  delay(INTERVALO);
}
