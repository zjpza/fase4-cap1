# Coleta de Sensores com ESP32 (Wokwi)

Issue #9 (opcional). Documenta a coleta de dados do campo via ESP32 com três
sensores, simulada no [Wokwi](https://wokwi.com). Os arquivos estão em `src/esp32/`.

## Sensores e pinagem

| Sensor | Grandeza | Pino ESP32 | Tipo |
| ------ | -------- | ---------- | ---- |
| DHT22 | Temperatura (°C) e umidade (%) | GPIO 15 | Digital |
| LDR (fotoresistor) | Luminosidade → 0..100000 lux | GPIO 34 | Analógico (ADC1) |
| Potenciômetro (simula pH) | pH → 0..14 | GPIO 35 | Analógico (ADC1) |

Alimentação dos três: `3V3` e `GND`.

> O sensor de pH é representado por um potenciômetro: no Wokwi não há sensor de pH
> nativo, então o potenciômetro fornece a tensão analógica equivalente, mapeada
> para a escala 0..14 no firmware.

## Arquivos

| Arquivo | Função |
| ------- | ------ |
| `arduino_sensores.ino` | Firmware: lê os sensores e publica JSON no Serial a cada 2 s. |
| `diagram.json` | Circuito do Wokwi (placa + sensores + ligações). |
| `wokwi.toml` | Configuração do projeto Wokwi. |
| `simulacao.py` | Alternativa em Python: gera a telemetria sem hardware. |

## Como rodar no Wokwi

1. Acesse https://wokwi.com e crie um projeto **ESP32 / Arduino**.
2. Cole o conteúdo de `arduino_sensores.ino`.
3. Substitua o `diagram.json` do projeto pelo desta pasta.
4. Em **Library Manager**, adicione `DHT sensor library` (Adafruit) e
   `Adafruit Unified Sensor`.
5. Clique em **Play**. O Serial Monitor mostrará as leituras:

```json
{"temperatura":24.3,"umidade":61.0,"ph":6.52,"luminosity":48000}
```

## Alternativa sem hardware (Python)

Para gerar a mesma telemetria sem o simulador, com ciclo dia/noite e ruído:

```bash
python src/esp32/simulacao.py --sensores 5 --horas 48 --intervalo 30
```

Gera `src/data/processed/simulacao_sensores.csv`, que pode alimentar o pipeline
de ingestão e análise.

## Integração com o pipeline

O JSON publicado pelo ESP32 e o CSV da simulação trazem os campos de **sensor**
(`temperatura`, `umidade`, `ph`, `luminosity`), que correspondem às colunas de
telemetria da tabela `leituras_sensor`.

Importante: esse stream é telemetria pura. Ele **não** inclui `cultura`, `N/P/K`,
`chuva_mm` nem o alvo `produtividade_kg_ha` — essas variáveis vêm de outras fontes
(catálogo de culturas, análise de solo, dados históricos). Por isso a simulação
**não substitui** o dataset de treino carregado por `src/data/load_to_sql.py`; ela
demonstra a etapa de coleta. Para persistir as leituras, os campos de sensor seriam
combinados com a cultura correspondente antes da gravação.

## Evidências (vídeo / capturas)

- Captura do circuito no Wokwi: _adicionar em `assets/screenshots/`._
- Captura do Serial Monitor com as leituras: _adicionar em `assets/screenshots/`._
