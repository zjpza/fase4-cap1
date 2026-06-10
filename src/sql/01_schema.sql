-- =====================================================================
-- FarmTech Solutions - Fase 4 CAP 1
-- Schema relacional para persistir dados de sensores IoT (SQLite)
-- Issue #7 (Ir Alem 1): Integracao IoT com Banco de Dados SQL
-- =====================================================================
-- Tabelas:
--   culturas         -> catalogo de culturas monitoradas
--   leituras_sensor  -> telemetria dos sensores + variaveis agronomicas + alvo
--   acoes_irrigacao  -> recomendacoes de manejo geradas pelo modelo de ML
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS acoes_irrigacao;
DROP TABLE IF EXISTS leituras_sensor;
DROP TABLE IF EXISTS culturas;

-- ---------------------------------------------------------------------
-- culturas: uma linha por cultura agricola monitorada
-- ---------------------------------------------------------------------
CREATE TABLE culturas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT    NOT NULL UNIQUE,
    area_hectare  REAL    NOT NULL CHECK (area_hectare > 0),
    data_plantio  TEXT    NOT NULL          -- ISO-8601 (YYYY-MM-DD)
);

-- ---------------------------------------------------------------------
-- leituras_sensor: telemetria coletada no campo.
-- Estende o schema base do #7 (umidade, ph, temperatura, luminosidade)
-- com as variaveis agronomicas reusadas da Fase 3 (N, P, K, chuva) e o
-- alvo de regressao da Fase 4 (produtividade_kg_ha), formando a tabela-fato
-- que alimenta diretamente o pipeline de Machine Learning.
-- ---------------------------------------------------------------------
CREATE TABLE leituras_sensor (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp            TEXT    NOT NULL,            -- ISO-8601
    sensor_id            TEXT    NOT NULL,            -- ex.: S001..S010
    cultura_id           INTEGER NOT NULL,
    temperatura          REAL    CHECK (temperatura BETWEEN -10 AND 60),
    umidade              REAL    CHECK (umidade BETWEEN 0 AND 100),
    ph                   REAL    CHECK (ph BETWEEN 0 AND 14),
    luminosity           REAL    CHECK (luminosity BETWEEN 0 AND 100000),
    n                    REAL,                        -- Nitrogenio (kg/ha)
    p                    REAL,                        -- Fosforo (kg/ha)
    k                    REAL,                        -- Potassio (kg/ha)
    chuva_mm             REAL,                        -- Precipitacao (mm)
    produtividade_kg_ha  REAL,                        -- Alvo (kg/ha)
    FOREIGN KEY (cultura_id) REFERENCES culturas (id)
);

-- ---------------------------------------------------------------------
-- acoes_irrigacao: recomendacoes de manejo geradas a partir das predicoes
-- ---------------------------------------------------------------------
CREATE TABLE acoes_irrigacao (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    cultura_id        INTEGER NOT NULL,
    data              TEXT    NOT NULL,               -- ISO-8601
    volume_m3         REAL    CHECK (volume_m3 >= 0),  -- volume de irrigacao recomendado
    recomendacao_ml   TEXT,                            -- texto gerado pelo motor de recomendacao
    FOREIGN KEY (cultura_id) REFERENCES culturas (id)
);

-- ---------------------------------------------------------------------
-- Indices em colunas frequentemente consultadas
-- ---------------------------------------------------------------------
CREATE INDEX idx_leituras_sensor_id   ON leituras_sensor (sensor_id);
CREATE INDEX idx_leituras_timestamp   ON leituras_sensor (timestamp);
CREATE INDEX idx_leituras_cultura     ON leituras_sensor (cultura_id);
CREATE INDEX idx_acoes_cultura        ON acoes_irrigacao (cultura_id);
