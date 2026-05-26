# src/data
Dados brutos e processados do projeto.

- `raw/`: dados brutos (CSV, JSON, etc.).
- `processed/`: dados apos engenharia de features (CSV).

Scripts:
- `generate_dataset.py`: gera dados simulados se necessario.
- `feature_engineering.py`: cria features e normaliza.
- `load_to_sql.py`: carrega dados no banco SQL.
