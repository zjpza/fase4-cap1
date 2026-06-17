# src/sql
Scripts de banco de dados relacional.

- `01_schema.sql`: DDL SQLite (CREATE TABLE, indices, constraints).
- `02_seed_data.sql`: INSERTs de dados de exemplo (SQLite).
- `oracle/`: versao Oracle (FIAP) — `01_schema_oracle.sql`, `02_seed_data.sql` e
  `03_queries_exploratorias.sql` (consultas analiticas da base de sensores).
- `README_SQL.md`: dicionario de dados e instrucoes de execucao.

Persistencia dupla (ver `src/db.py`): Oracle FIAP (obrigatoria, via `.env`) + SQLite
local (fallback). Importacao no SQL Developer: `docs/oracle_import.md`.
