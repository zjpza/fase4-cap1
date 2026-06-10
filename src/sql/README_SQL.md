# Banco de Dados — FarmTech Solutions (Fase 4 CAP 1)

Banco relacional **SQLite** que persiste os dados de sensores IoT do campo e as
recomendações de manejo geradas pelo modelo de Machine Learning.

## Modelo de dados (MER)

```
culturas (1) ──< (N) leituras_sensor
culturas (1) ──< (N) acoes_irrigacao
```

A base agronômica é **reusada da Fase 3** (`Atividade_Cap10_produtos_agricolas.csv`:
N, P, K, temperatura, umidade, pH, chuva) e adaptada ao contexto IoT da Fase 4 com
telemetria de sensores (timestamp, sensor_id, luminosidade) e o alvo de regressão
`produtividade_kg_ha`.

### Mapeamento sensor → coluna

| Sensor físico/virtual | Grandeza     | Coluna                        |
| --------------------- | ------------ | ----------------------------- |
| DHT22                 | Temperatura  | `leituras_sensor.temperatura` |
| DHT22                 | Umidade      | `leituras_sensor.umidade`     |
| Sensor de pH          | pH do solo   | `leituras_sensor.ph`          |
| LDR                   | Luminosidade | `leituras_sensor.luminosity`  |

## Dicionário de dados

### `culturas`

| Coluna       | Tipo    | Descrição                  |
| ------------ | ------- | -------------------------- |
| id           | INTEGER | PK, autoincremento         |
| nome         | TEXT    | Nome da cultura (único)    |
| area_hectare | REAL    | Área plantada (ha), > 0    |
| data_plantio | TEXT    | Data de plantio (ISO-8601) |

### `leituras_sensor` (tabela-fato que alimenta o ML)

| Coluna              | Tipo    | Descrição                            |
| ------------------- | ------- | ------------------------------------ |
| id                  | INTEGER | PK, autoincremento                   |
| timestamp           | TEXT    | Momento da leitura (ISO-8601)        |
| sensor_id           | TEXT    | Identificador do sensor (S001..S010) |
| cultura_id          | INTEGER | FK → `culturas.id`                   |
| temperatura         | REAL    | °C (−10..60)                         |
| umidade             | REAL    | % (0..100)                           |
| ph                  | REAL    | pH (0..14)                           |
| luminosity          | REAL    | lux (0..100000)                      |
| n / p / k           | REAL    | Nutrientes N, P, K (kg/ha)           |
| chuva_mm            | REAL    | Precipitação (mm)                    |
| produtividade_kg_ha | REAL    | **Alvo de regressão** (kg/ha)        |

### `acoes_irrigacao`

| Coluna          | Tipo    | Descrição                               |
| --------------- | ------- | --------------------------------------- |
| id              | INTEGER | PK, autoincremento                      |
| cultura_id      | INTEGER | FK → `culturas.id`                      |
| data            | TEXT    | Data da recomendação (ISO-8601)         |
| volume_m3       | REAL    | Volume de irrigação sugerido (m³), ≥ 0  |
| recomendacao_ml | TEXT    | Texto gerado pelo motor de recomendação |

Índices: `sensor_id`, `timestamp`, `cultura_id` (em `leituras_sensor`) e `cultura_id`
(em `acoes_irrigacao`).

## Notas de modelagem

O alvo `produtividade_kg_ha` é gerado em `generate_dataset.py` a partir de:

```
produtividade = base_cultura × fator_ambiente × fator_nutrientes + ruído_gaussiano
```

- `fator_ambiente`: média de scores gaussianos de temperatura, pH, umidade e chuva
  em torno de faixas agronômicas ótimas (cada um 0..1);
- `fator_nutrientes`: soma N+P+K normalizada para o intervalo 0.7..1.3;
- `base_cultura`: patamar de rendimento por cultura (2500..6000 kg/ha), fixo por `SEED=42`;
- `ruído`: gaussiano de ~5% sobre o valor, para quebrar a relação determinística.

O dataset serve para demonstrar o pipeline de regressão (treino, validação cruzada,
métricas, predição), não para afirmar valores reais de produtividade. A fórmula é
não-linear e ruidosa de propósito, exigindo que o modelo aprenda a combinação das
variáveis.

## Como popular o banco

### Ingestão automática

```bash
python src/data/generate_dataset.py   # gera src/data/processed/farmtech_dataset.csv
python src/data/load_to_sql.py        # cria farmtech.db e popula culturas + leituras_sensor
```

O `load_to_sql.py` recria o schema, trata nulos/duplicatas, insere em lote
(`chunksize=500`) e imprime a verificação (COUNT por tabela).

### Validação isolada do schema (opcional)

```bash
sqlite3 demo.db < src/sql/01_schema.sql
sqlite3 demo.db < src/sql/02_seed_data.sql
```
