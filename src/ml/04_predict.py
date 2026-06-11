"""
04_predict.py — FarmTech Solutions / Fase 4 CAP 1

Carrega o modelo de regressao treinado (models/modelo_farmtech.pkl) e prediz a
produtividade (kg/ha) a partir das leituras de sensores + variaveis agronomicas.

Usado pelo dashboard Streamlit (Bloco 3) e executavel direto para teste rapido.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

ML_DIR = Path(__file__).resolve().parent
MODEL_PATH = ML_DIR / "models" / "modelo_farmtech.pkl"
META_PATH = ML_DIR / "models" / "model_columns.json"

_model = None
_meta = None


def _carregar():
    """Carrega modelo e metadados uma unica vez (cache em modulo)."""
    global _model, _meta
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo nao encontrado: {MODEL_PATH}\n"
                "Rode antes o notebook src/ml/02_modelagem.ipynb."
            )
        _model = joblib.load(MODEL_PATH)
        _meta = json.load(open(META_PATH, encoding="utf-8"))
    return _model, _meta


def prever(entrada: dict) -> float:
    """
    Preve a produtividade (kg/ha) para um conjunto de leituras.

    `entrada` deve conter as chaves de FEATURES:
        temperatura, umidade, ph, luminosity, n, p, k, chuva_mm, cultura

    Retorna a produtividade prevista em kg/ha (float).
    """
    model, meta = _carregar()
    features = meta["features"]

    faltando = [c for c in features if c not in entrada]
    if faltando:
        raise ValueError(f"Faltam variaveis na entrada: {faltando}")

    X = pd.DataFrame([{c: entrada[c] for c in features}])
    return float(model.predict(X)[0])


if __name__ == "__main__":
    exemplo = {
        "temperatura": 25.0,
        "umidade": 70.0,
        "ph": 6.5,
        "luminosity": 45000.0,
        "n": 90,
        "p": 42,
        "k": 43,
        "chuva_mm": 120.0,
        "cultura": "rice",
    }
    pred = prever(exemplo)
    print("Entrada:", exemplo)
    print(f"Produtividade prevista: {pred:.1f} kg/ha")
