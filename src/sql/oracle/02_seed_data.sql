-- =====================================================================
-- FarmTech Solutions - Fase 4 CAP 1
-- 02_seed_data.sql (Oracle) - dados de EXEMPLO para validar o schema.
-- =====================================================================
-- A carga COMPLETA (2200 leituras reusadas da Fase 3) e feita por
-- `python src/data/load_to_sql.py` (popula Oracle quando ha .env). Este
-- seed serve para inspecionar o schema rapidamente no SQL Developer apos
-- rodar 01_schema_oracle.sql.
-- =====================================================================

-- Culturas
INSERT INTO culturas (nome, area_hectare, data_plantio) VALUES
    ('rice',   45.0, TO_DATE('2026-01-15', 'YYYY-MM-DD'));
INSERT INTO culturas (nome, area_hectare, data_plantio) VALUES
    ('maize',  60.5, TO_DATE('2026-01-20', 'YYYY-MM-DD'));
INSERT INTO culturas (nome, area_hectare, data_plantio) VALUES
    ('grapes', 12.0, TO_DATE('2026-02-01', 'YYYY-MM-DD'));

-- Leituras de sensores (telemetria + variaveis agronomicas + alvo)
INSERT INTO leituras_sensor
    (ts, sensor_id, cultura_id, temperatura, umidade, ph, luminosity, n, p, k, chuva_mm, produtividade_kg_ha)
VALUES
    (TO_TIMESTAMP('2026-01-15 06:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'S001', 1, 24.5, 82.0, 6.5, 38000, 90, 42, 43, 202.9, 3120.5);
INSERT INTO leituras_sensor
    (ts, sensor_id, cultura_id, temperatura, umidade, ph, luminosity, n, p, k, chuva_mm, produtividade_kg_ha)
VALUES
    (TO_TIMESTAMP('2026-01-20 07:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'S002', 2, 26.0, 65.0, 6.2, 52000, 78, 48, 40, 88.3, 4210.8);
INSERT INTO leituras_sensor
    (ts, sensor_id, cultura_id, temperatura, umidade, ph, luminosity, n, p, k, chuva_mm, produtividade_kg_ha)
VALUES
    (TO_TIMESTAMP('2026-02-01 08:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'S003', 3, 22.8, 81.5, 6.0, 41000, 23, 132, 200, 70.1, 6480.0);

-- Acao de irrigacao de exemplo (normalmente gerada por src/ml/recomendacao.py)
INSERT INTO acoes_irrigacao (cultura_id, data_acao, volume_m3, recomendacao_ml) VALUES
    (1, TO_DATE('2026-01-15', 'YYYY-MM-DD'), 320.0, 'Irrigacao moderada; pH adequado; manter adubacao NPK.');

COMMIT;
