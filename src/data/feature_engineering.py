"""
feature_engineering.py — FarmTech Solutions / Fase 4 CAP 1

Funcoes reutilizaveis (pelos notebooks de ML e por 04_predict.py) para:
  - carregar a tabela-fato do SQLite (leituras_sensor + cultura)
  - separar features/alvo
  - construir o pre-processador (scaling numerico + one-hot da cultura)

Mantem UM unico ponto de verdade para a definicao de features, evitando
divergencia entre treino, avaliacao e predicao.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "farmtech.db"

# Definicao canonica de features e alvo
TARGET = "produtividade_kg_ha"
NUMERIC_FEATURES = ["temperatura", "umidade", "ph", "luminosity",
                    "n", "p", "k", "chuva_mm"]
CATEGORICAL_FEATURES = ["cultura"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def carregar_dados(db_path: Path | str = DB_PATH) -> pd.DataFrame:
    """Le leituras_sensor unida ao nome da cultura, pronta para o ML."""
    engine = create_engine(f"sqlite:///{db_path}")
    query = """
        SELECT l.temperatura, l.umidade, l.ph, l.luminosity,
               l.n, l.p, l.k, l.chuva_mm,
               c.nome AS cultura,
               l.produtividade_kg_ha
        FROM leituras_sensor l
        JOIN culturas c ON c.id = l.cultura_id
    """
    return pd.read_sql(query, engine)


def separar_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Devolve (X, y) a partir do dataframe carregado."""
    X = df[FEATURES].copy()
    y = df[TARGET].copy()
    return X, y


def construir_preprocessador() -> ColumnTransformer:
    """Scaling das numericas + one-hot da cultura. Usado dentro de um Pipeline."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
