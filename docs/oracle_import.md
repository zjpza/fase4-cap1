# Importação e exploração no Oracle (FIAP) — Entrega obrigatória

Este documento descreve, passo a passo, como o banco relacional do FarmTech é criado,
populado e explorado no **Oracle Database da FIAP** usando o **Oracle SQL Developer**.
Cada etapa indica o print de evidência correspondente em `assets/screenshots/oracle/`.

> **Persistência dupla.** O Oracle é a entrega obrigatória. Em paralelo, o projeto mantém
> um SQLite local (`farmtech.db`) como _fallback_ para rodar dashboard/ML sem credencial.
> O resolver `src/db.py` escolhe o Oracle automaticamente quando há `.env` válido.

## Modelo de dados

```
culturas (1) ──< (N) leituras_sensor      -- telemetria dos sensores IoT (tabela-fato)
culturas (1) ──< (N) acoes_irrigacao      -- recomendações geradas pelo modelo de ML
```

| Tabela            | Papel                                                              |
| ----------------- | ------------------------------------------------------------------ |
| `culturas`        | Catálogo de culturas monitoradas (nome, área, plantio).            |
| `leituras_sensor` | Leituras dos sensores + variáveis agronômicas + alvo de regressão. |
| `acoes_irrigacao` | Recomendações de irrigação/manejo persistidas pelo pipeline de ML. |

DDL completo em [`src/sql/oracle/01_schema_oracle.sql`](../src/sql/oracle/01_schema_oracle.sql).

## Passo a passo (SQL Developer)

### 1. Criar a conexão com o Oracle FIAP
- **Connection Name**: `farmtech-fiap`
- **Username**: seu RM (ex.: `rm570527`) · **Password**: senha da FIAP
- **Hostname**: `oracle.fiap.com.br` · **Port**: `1521` · **Service name**: `ORCL`
- Clicar **Test** → _Status: Success_ → **Connect**.

📷 `assets/screenshots/oracle/01_conexao.png` — janela de conexão com teste bem-sucedido.

### 2. Criar o schema
Abrir [`01_schema_oracle.sql`](../src/sql/oracle/01_schema_oracle.sql) e executar como script (**F5**).
Cria as 3 tabelas (com PK `IDENTITY`, `CHECK`s e FKs) e os 4 índices. O bloco PL/SQL inicial
faz o _DROP_ idempotente (não falha na primeira execução).

📷 `assets/screenshots/oracle/02_schema.png` — script executado, tabelas em _Connections_.

### 3. Popular as tabelas
Duas opções:
- **Carga completa (recomendada)** — 2200 leituras reusadas da Fase 3, via Python:
  ```bash
  python src/data/load_to_sql.py     # com .env preenchido, popula Oracle + SQLite
  ```
- **Amostra rápida** — apenas para inspecionar o schema no SQL Developer:
  executar [`02_seed_data.sql`](../src/sql/oracle/02_seed_data.sql) (**F5**).

📷 `assets/screenshots/oracle/03_carga.png` — log do `load_to_sql.py` (COUNT por tabela)
ou o `COMMIT` do seed no SQL Developer.

### 4. Gerar as recomendações de ML (opcional)
```bash
python src/ml/recomendacao.py        # grava em acoes_irrigacao no backend ativo
```

### 5. Consultas exploratórias
Abrir [`03_queries_exploratorias.sql`](../src/sql/oracle/03_queries_exploratorias.sql) e
executar cada consulta. As 7 queries respondem perguntas de negócio sobre a base de sensores:

| Query | Pergunta respondida                                              |
| ----- | --------------------------------------------------------------- |
| Q1    | Volume de dados (culturas, leituras, nº de sensores).           |
| Q2    | Produtividade por cultura: média, desvio, amplitude (ranking).  |
| Q3    | Correlação (Pearson) de umidade/pH/temp/chuva/NPK com o alvo.   |
| Q4    | Faixas médias de umidade, pH, temperatura e chuva por cultura.  |
| Q5    | Outliers de produtividade via IQR.                              |
| Q6    | Atividade e janela temporal por sensor.                         |
| Q7    | Recomendações de irrigação geradas (volume médio por cultura).  |

📷 `assets/screenshots/oracle/04_query_correlacao.png`,
`assets/screenshots/oracle/05_query_produtividade.png`,
`assets/screenshots/oracle/06_query_outliers.png` — resultados (grid) de cada consulta.

## Checklist de evidências
- [ ] `01_conexao.png` — conexão Oracle FIAP testada com sucesso
- [ ] `02_schema.png` — tabelas criadas
- [ ] `03_carga.png` — carga concluída (COUNT por tabela)
- [ ] `04_query_correlacao.png` — Q3 (correlações)
- [ ] `05_query_produtividade.png` — Q2 (ranking por cultura)
- [ ] `06_query_outliers.png` — Q5 (outliers IQR)
