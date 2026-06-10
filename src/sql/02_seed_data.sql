-- =====================================================================
-- FarmTech Solutions - Fase 4 CAP 1
-- 02_seed_data.sql - dados de EXEMPLO para demonstracao rapida do schema
-- =====================================================================
-- Observacao: a carga COMPLETA (2200 leituras reais reusadas da Fase 3) e
-- feita automaticamente por `python src/data/load_to_sql.py`. Este seed
-- serve apenas para validar o schema isoladamente, ex.:
--   sqlite3 demo.db < src/sql/01_schema.sql
--   sqlite3 demo.db < src/sql/02_seed_data.sql
-- =====================================================================

-- Culturas
INSERT INTO culturas (nome, area_hectare, data_plantio) VALUES
    ('rice',   45.0, '2026-01-15'),
    ('maize',  60.5, '2026-01-20'),
    ('grapes', 12.0, '2026-02-01');

-- Leituras de sensores (telemetria + variaveis agronomicas + alvo)
INSERT INTO leituras_sensor
    (timestamp, sensor_id, cultura_id, temperatura, umidade, ph, luminosity, n, p, k, chuva_mm, produtividade_kg_ha)
VALUES
    ('2026-01-15T06:00:00', 'S001', 1, 24.5, 82.0, 6.5, 38000, 90, 42, 43, 202.9, 3120.5),
    ('2026-01-20T07:30:00', 'S002', 2, 26.0, 65.0, 6.2, 52000, 78, 48, 40, 88.3, 4210.8),
    ('2026-02-01T08:15:00', 'S003', 3, 22.8, 81.5, 6.0, 41000, 23, 132, 200, 70.1, 6480.0);

-- Acao de irrigacao de exemplo (normalmente gerada por src/ml/recomendacao.py)
INSERT INTO acoes_irrigacao (cultura_id, data, volume_m3, recomendacao_ml) VALUES
    (1, '2026-01-15', 320.0, 'Irrigacao moderada; pH adequado; manter adubacao NPK.');
