-- =====================================================================
-- FarmTech Solutions - Fase 4 CAP 1
-- 03_queries_exploratorias.sql (Oracle)
-- Consultas analiticas sobre a base de SENSORES (leituras_sensor).
-- =====================================================================
-- Objetivo: evidenciar exploracao SQL da base obrigatoria - cada query
-- responde a uma pergunta de negocio. Rodar no SQL Developer e capturar
-- o resultado (print) para a documentacao (docs/oracle_import.md).
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1. Volume de dados: quantas leituras e culturas existem?
-- ---------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM culturas)        AS total_culturas,
    (SELECT COUNT(*) FROM leituras_sensor) AS total_leituras,
    (SELECT COUNT(DISTINCT sensor_id) FROM leituras_sensor) AS total_sensores
FROM dual;

-- ---------------------------------------------------------------------
-- Q2. Produtividade por cultura: media, desvio e amplitude (ranking).
--     Responde: quais culturas rendem mais e quao dispersas sao?
-- ---------------------------------------------------------------------
SELECT
    c.nome                                  AS cultura,
    COUNT(*)                                AS leituras,
    ROUND(AVG(l.produtividade_kg_ha), 1)    AS prod_media,
    ROUND(STDDEV(l.produtividade_kg_ha), 1) AS prod_desvio,
    ROUND(MIN(l.produtividade_kg_ha), 1)    AS prod_min,
    ROUND(MAX(l.produtividade_kg_ha), 1)    AS prod_max
FROM leituras_sensor l
JOIN culturas c ON c.id = l.cultura_id
GROUP BY c.nome
ORDER BY prod_media DESC;

-- ---------------------------------------------------------------------
-- Q3. Correlacao de Pearson entre variaveis ambientais e o alvo.
--     Responde: quais sensores mais se relacionam com a produtividade?
-- ---------------------------------------------------------------------
SELECT
    ROUND(CORR(umidade,     produtividade_kg_ha), 3) AS corr_umidade,
    ROUND(CORR(ph,          produtividade_kg_ha), 3) AS corr_ph,
    ROUND(CORR(temperatura, produtividade_kg_ha), 3) AS corr_temperatura,
    ROUND(CORR(chuva_mm,    produtividade_kg_ha), 3) AS corr_chuva,
    ROUND(CORR(n,           produtividade_kg_ha), 3) AS corr_n,
    ROUND(CORR(p,           produtividade_kg_ha), 3) AS corr_p,
    ROUND(CORR(k,           produtividade_kg_ha), 3) AS corr_k
FROM leituras_sensor;

-- ---------------------------------------------------------------------
-- Q4. Faixas medias de umidade e pH por cultura (condicao agronomica).
--     Responde: cada cultura opera em que faixa de solo/clima?
-- ---------------------------------------------------------------------
SELECT
    c.nome                          AS cultura,
    ROUND(AVG(l.umidade), 1)        AS umidade_media,
    ROUND(AVG(l.ph), 2)             AS ph_medio,
    ROUND(AVG(l.temperatura), 1)    AS temp_media,
    ROUND(AVG(l.chuva_mm), 1)       AS chuva_media
FROM leituras_sensor l
JOIN culturas c ON c.id = l.cultura_id
GROUP BY c.nome
ORDER BY c.nome;

-- ---------------------------------------------------------------------
-- Q5. Outliers de produtividade via IQR, calculado POR CULTURA.
--     Responde: dentro de cada cultura, ha leituras anomalas (fora de
--     Q1-1.5*IQR .. Q3+1.5*IQR)? O IQR por cultura evita falsos positivos
--     causados pelos patamares de rendimento muito diferentes entre culturas.
-- ---------------------------------------------------------------------
WITH stats AS (
    SELECT
        c.nome                       AS cultura,
        l.sensor_id,
        l.produtividade_kg_ha,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY l.produtividade_kg_ha)
            OVER (PARTITION BY l.cultura_id) AS q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY l.produtividade_kg_ha)
            OVER (PARTITION BY l.cultura_id) AS q3
    FROM leituras_sensor l
    JOIN culturas c ON c.id = l.cultura_id
)
SELECT cultura, sensor_id, ROUND(produtividade_kg_ha, 1) AS produtividade_kg_ha
FROM stats
WHERE produtividade_kg_ha < q1 - 1.5 * (q3 - q1)
   OR produtividade_kg_ha > q3 + 1.5 * (q3 - q1)
ORDER BY cultura, produtividade_kg_ha DESC;

-- ---------------------------------------------------------------------
-- Q6. Atividade por sensor: contagem e janela temporal coberta.
--     Responde: todos os sensores reportaram? Qual o periodo de coleta?
-- ---------------------------------------------------------------------
SELECT
    sensor_id,
    COUNT(*)        AS leituras,
    MIN(ts)         AS primeira_leitura,
    MAX(ts)         AS ultima_leitura
FROM leituras_sensor
GROUP BY sensor_id
ORDER BY sensor_id;

-- ---------------------------------------------------------------------
-- Q7. Recomendacoes de irrigacao geradas pelo ML (acoes_irrigacao).
--     Responde: o pipeline gravou recomendacoes? Volume medio por cultura?
-- ---------------------------------------------------------------------
SELECT
    c.nome                       AS cultura,
    COUNT(*)                     AS recomendacoes,
    ROUND(AVG(a.volume_m3), 1)   AS volume_medio_m3
FROM acoes_irrigacao a
JOIN culturas c ON c.id = a.cultura_id
GROUP BY c.nome
ORDER BY volume_medio_m3 DESC;
