"""
load_to_sql.py — FarmTech Solutions / Fase 4 CAP 1
Issue #7 (Ir Alem 1): ingestao automatica dos dados IoT no banco SQL.

Persistencia DUPLA:
  - ORACLE FIAP  -> entrega obrigatoria. Populado quando ha credencial valida
                    no .env (ver src/db.py).
  - SQLite local -> fallback, SEMPRE populado (farmtech.db na raiz). Garante
                    que dashboard e ML rodem sem credencial.

Fluxo (por backend):
  1. (Re)cria o schema a partir do .sql correspondente.
  2. Le src/data/processed/farmtech_dataset.csv (gerado por generate_dataset.py).
  3. Trata duplicatas e valores nulos.
  4. Popula `culturas` (catalogo) e `leituras_sensor` (telemetria) em lote.
  5. Imprime queries de verificacao (COUNT por tabela).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Garante o import de src/db.py (raiz/src no path)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]            # raiz do repo
DATASET_CSV = ROOT / "src" / "data" / "processed" / "farmtech_dataset.csv"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
def criar_schema_sqlite(engine: Engine) -> None:
    """Roda o DDL do SQLite (multiplos statements via executescript)."""
    ddl = db.schema_path(db.SQLITE).read_text(encoding="utf-8")
    raw = engine.raw_connection()
    try:
        raw.executescript(ddl)
        raw.commit()
    finally:
        raw.close()
    print("[OK] Schema SQLite criado.")


def criar_schema_oracle(engine: Engine) -> None:
    """DROP idempotente (ignora ORA-00942) + CREATE de cada objeto."""
    with engine.begin() as conn:
        for tabela in db.ORACLE_TABLES:
            try:
                conn.execute(text(f"DROP TABLE {tabela} CASCADE CONSTRAINTS"))
            except Exception:                          # noqa: BLE001 (tabela inexistente)
                pass
        for stmt in db.oracle_create_statements():
            conn.execute(text(stmt))
    print("[OK] Schema Oracle criado.")


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
def carregar_dataset() -> pd.DataFrame:
    if not DATASET_CSV.exists():
        raise FileNotFoundError(
            f"Dataset nao encontrado: {DATASET_CSV}\n"
            "Rode antes: python src/data/generate_dataset.py"
        )
    df = pd.read_csv(DATASET_CSV, parse_dates=["timestamp"])

    essenciais = ["temperatura", "umidade", "ph", "cultura"]
    antes = len(df)
    df = df.dropna(subset=essenciais)
    df = df.drop_duplicates()
    print(f"[OK] Dataset carregado: {len(df)} linhas "
          f"({antes - len(df)} removidas por nulo/duplicata)")
    return df


def montar_culturas(df: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    nomes = sorted(df["cultura"].unique())
    return pd.DataFrame({
        "nome": nomes,
        "area_hectare": np.round(rng.uniform(5, 120, size=len(nomes)), 2),
        # datetime real (nao string): Oracle exige DATE; SQLite grava como ISO.
        "data_plantio": [pd.Timestamp(2026, 1, 1)] * len(nomes),
    })


def montar_leituras(df: pd.DataFrame, mapa_cultura: dict[str, int]) -> pd.DataFrame:
    return pd.DataFrame({
        # datetime real (nao strftime): Oracle exige TIMESTAMP; SQLite grava ISO.
        "ts": pd.to_datetime(df["timestamp"]),
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


# ---------------------------------------------------------------------------
# Carga + verificacao (por engine)
# ---------------------------------------------------------------------------
def popular(engine: Engine, culturas: pd.DataFrame, df: pd.DataFrame) -> None:
    backend = db.backend_of(engine)
    db.coerce_datetimes(culturas, backend).to_sql(
        "culturas", engine, if_exists="append", index=False)
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, nome FROM culturas")).fetchall()
    mapa = {nome: cid for cid, nome in rows}
    print(f"[OK] culturas inseridas: {len(mapa)}")

    leituras = db.coerce_datetimes(montar_leituras(df, mapa), backend)
    # SQLite: 1 INSERT multirow (rapido). Oracle nao suporta multirow VALUES;
    # usa executemany nativo do oracledb (method=None).
    metodo = "multi" if backend == db.SQLITE else None
    leituras.to_sql("leituras_sensor", engine, if_exists="append",
                    index=False, chunksize=500, method=metodo)
    print(f"[OK] leituras_sensor inseridas: {len(leituras)}")


def verificar(engine: Engine) -> None:
    with engine.connect() as conn:
        for tabela in ("culturas", "leituras_sensor", "acoes_irrigacao"):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}")).scalar()
            print(f"     {tabela:18s} -> {n} registros")
        amostra = db.read_sql(
            "SELECT c.nome, COUNT(*) AS leituras, "
            "ROUND(AVG(l.produtividade_kg_ha),0) AS prod_media "
            "FROM leituras_sensor l JOIN culturas c ON c.id = l.cultura_id "
            "GROUP BY c.nome ORDER BY prod_media DESC FETCH FIRST 5 ROWS ONLY"
            if engine.dialect.name == "oracle" else
            "SELECT c.nome, COUNT(*) AS leituras, "
            "ROUND(AVG(l.produtividade_kg_ha),0) AS prod_media "
            "FROM leituras_sensor l JOIN culturas c ON c.id = l.cultura_id "
            "GROUP BY c.nome ORDER BY prod_media DESC LIMIT 5",
            engine,
        )
    print("     Top 5 culturas por produtividade media:")
    for _, r in amostra.iterrows():
        print(f"       {r['nome']:14s} {int(r['leituras']):4d} leituras  "
              f"~{r['prod_media']:.0f} kg/ha")


def carregar_backend(engine: Engine, backend: str, df: pd.DataFrame,
                     culturas: pd.DataFrame) -> None:
    print(f"\n=== Backend: {backend.upper()} ===")
    if backend == db.ORACLE:
        criar_schema_oracle(engine)
    else:
        criar_schema_sqlite(engine)
    popular(engine, culturas, df)
    verificar(engine)


def main() -> None:
    df = carregar_dataset()
    culturas = montar_culturas(df)

    # SQLite: fallback, sempre populado.
    carregar_backend(db.sqlite_engine(), db.SQLITE, df, culturas)

    # Oracle: entrega obrigatoria, quando ha credencial no .env.
    oracle = db.oracle_engine()
    if oracle is not None:
        carregar_backend(oracle, db.ORACLE, df, culturas)
    else:
        print("\n[INFO] Oracle nao configurado (.env). Apenas SQLite populado.")

    print("\n[OK] Ingestao concluida.")


if __name__ == "__main__":
    main()
