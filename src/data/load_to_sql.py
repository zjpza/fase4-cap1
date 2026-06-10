"""
load_to_sql.py — FarmTech Solutions / Fase 4 CAP 1
Issue #7 (Ir Alem 1): ingestao automatica dos dados IoT no banco SQL.

Fluxo:
  1. Cria/recria o banco SQLite a partir de src/sql/01_schema.sql.
  2. Le src/data/processed/farmtech_dataset.csv (gerado por generate_dataset.py).
  3. Trata duplicatas e valores nulos.
  4. Popula `culturas` (catalogo) e `leituras_sensor` (telemetria) em lote.
  5. Imprime queries de verificacao (COUNT por tabela).

Banco: SQLite (farmtech.db na raiz do projeto). Usa SQLAlchemy.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]            # raiz do repo
DB_PATH = ROOT / "farmtech.db"
SCHEMA_SQL = ROOT / "src" / "sql" / "01_schema.sql"
DATASET_CSV = ROOT / "src" / "data" / "processed" / "farmtech_dataset.csv"

ENGINE = create_engine(f"sqlite:///{DB_PATH}")


def criar_schema() -> None:
    """Executa o DDL do 01_schema.sql (recria as tabelas)."""
    ddl = SCHEMA_SQL.read_text(encoding="utf-8")
    raw = ENGINE.raw_connection()
    try:
        raw.executescript(ddl)        # SQLite: roda multiplos statements
        raw.commit()
    finally:
        raw.close()
    print(f"[OK] Schema criado em {DB_PATH}")


def carregar_dataset() -> pd.DataFrame:
    if not DATASET_CSV.exists():
        raise FileNotFoundError(
            f"Dataset nao encontrado: {DATASET_CSV}\n"
            "Rode antes: python src/data/generate_dataset.py"
        )
    df = pd.read_csv(DATASET_CSV, parse_dates=["timestamp"])

    # Trata nulos: descarta linhas sem leitura de sensor essencial
    essenciais = ["temperatura", "umidade", "ph", "cultura"]
    antes = len(df)
    df = df.dropna(subset=essenciais)
    # Trata duplicatas exatas
    df = df.drop_duplicates()
    print(f"[OK] Dataset carregado: {len(df)} linhas "
          f"({antes - len(df)} removidas por nulo/duplicata)")
    return df


def popular_culturas(df: pd.DataFrame) -> dict[str, int]:
    """Insere o catalogo de culturas e devolve mapa nome -> id."""
    rng = np.random.default_rng(42)
    nomes = sorted(df["cultura"].unique())
    culturas = pd.DataFrame({
        "nome": nomes,
        "area_hectare": np.round(rng.uniform(5, 120, size=len(nomes)), 2),
        "data_plantio": [date(2026, 1, 1).isoformat()] * len(nomes),
    })
    culturas.to_sql("culturas", ENGINE, if_exists="append", index=False)

    with ENGINE.connect() as conn:
        rows = conn.execute(text("SELECT id, nome FROM culturas")).fetchall()
    mapa = {nome: cid for cid, nome in rows}
    print(f"[OK] culturas inseridas: {len(mapa)}")
    return mapa


def popular_leituras(df: pd.DataFrame, mapa_cultura: dict[str, int]) -> None:
    leituras = pd.DataFrame({
        "timestamp": df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "sensor_id": df["sensor_id"],
        "cultura_id": df["cultura"].map(mapa_cultura),
        "temperatura": df["temperatura"],
        "umidade": df["umidade"],
        "ph": df["ph"],
        "luminosity": df["luminosity"],
        "n": df["N"],
        "p": df["P"],
        "k": df["K"],
        "chuva_mm": df["chuva_mm"],
        "produtividade_kg_ha": df["produtividade_kg_ha"],
    })
    # Ingestao em lote
    leituras.to_sql("leituras_sensor", ENGINE, if_exists="append",
                    index=False, chunksize=500, method="multi")
    print(f"[OK] leituras_sensor inseridas: {len(leituras)}")


def verificar() -> None:
    with ENGINE.connect() as conn:
        for tabela in ("culturas", "leituras_sensor", "acoes_irrigacao"):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}")).scalar()
            print(f"     {tabela:18s} -> {n} registros")
        amostra = conn.execute(text(
            "SELECT c.nome, COUNT(*) AS leituras, "
            "ROUND(AVG(l.produtividade_kg_ha),0) AS prod_media "
            "FROM leituras_sensor l JOIN culturas c ON c.id = l.cultura_id "
            "GROUP BY c.nome ORDER BY prod_media DESC LIMIT 5"
        )).fetchall()
    print("     Top 5 culturas por produtividade media:")
    for nome, n, prod in amostra:
        print(f"       {nome:14s} {n:4d} leituras  ~{prod:.0f} kg/ha")


def main() -> None:
    criar_schema()
    df = carregar_dataset()
    mapa = popular_culturas(df)
    popular_leituras(df, mapa)
    print("[VERIFICACAO]")
    verificar()
    print(f"\n[OK] Banco pronto: {DB_PATH}")


if __name__ == "__main__":
    main()
