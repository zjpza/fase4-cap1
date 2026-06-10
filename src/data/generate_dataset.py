"""
generate_dataset.py — FarmTech Solutions / Fase 4 CAP 1

Pega a base agronomica reusada da Fase 3 (Atividade_Cap10_produtos_agricolas.csv:
N, P, K, temperature, humidity, ph, rainfall, label) e a adapta ao contexto IoT
da Fase 4:

  1. Adiciona colunas de telemetria de sensores (timestamp, sensor_id, luminosity)
     coerentes com os sensores do projeto (DHT22 -> temperature/humidity,
     sensor de pH -> ph, LDR -> luminosity).
  2. Engenha um alvo CONTINUO `produtividade_kg_ha` (regressao da Fase 4), ja que
     a Fase 3 era classificacao (recomendar cultura). A produtividade reaproveita
     o conceito de kg/ha do trabalho de grupo `fase3-cap1`.

A formula da produtividade e DIDATICA: combina faixas agronomicas otimas
(temperatura, pH, umidade, chuva) com a oferta de nutrientes (N, P, K) e uma base
por cultura, mais ruido gaussiano. Nao e uma identidade trivial de nenhuma feature
isolada — o modelo precisa aprender a combinacao nao-linear.

Saida: src/data/processed/farmtech_dataset.csv
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Reprodutibilidade
SEED = 42
rng = np.random.default_rng(SEED)

BASE_DIR = Path(__file__).resolve().parent
RAW_CSV = BASE_DIR / "raw" / "Atividade_Cap10_produtos_agricolas.csv"
OUT_CSV = BASE_DIR / "processed" / "farmtech_dataset.csv"

# Numero de sensores virtuais simulados no campo (ESP32/Wokwi)
N_SENSORES = 10


def _gauss_score(x: np.ndarray, optimo: float, tolerancia: float) -> np.ndarray:
    """Score 0..1: 1.0 no ponto otimo, caindo como uma gaussiana ao se afastar."""
    return np.exp(-0.5 * ((x - optimo) / tolerancia) ** 2)


def engenhar_produtividade(df: pd.DataFrame) -> np.ndarray:
    """
    Produtividade (kg/ha) didatica = base_cultura * fator_ambiente * fator_nutrientes + ruido.

    - fator_ambiente: media dos scores gaussianos de temperatura, pH, umidade e chuva
      em torno de faixas agronomicas otimas (0..1).
    - fator_nutrientes: oferta de N+P+K normalizada (0.7..1.3).
    - base_cultura: rendimento base distinto por cultura (kg/ha), pois 22 culturas
      tem patamares de produtividade muito diferentes.
    """
    # Faixas otimas genericas (didaticas)
    s_temp = _gauss_score(df["temperature"].to_numpy(), optimo=25.0, tolerancia=8.0)
    s_ph = _gauss_score(df["ph"].to_numpy(), optimo=6.5, tolerancia=1.2)
    s_hum = _gauss_score(df["humidity"].to_numpy(), optimo=70.0, tolerancia=25.0)
    s_rain = _gauss_score(df["rainfall"].to_numpy(), optimo=120.0, tolerancia=70.0)
    fator_ambiente = np.mean([s_temp, s_ph, s_hum, s_rain], axis=0)  # 0..1

    # Nutrientes: soma NPK normalizada para um multiplicador 0.7..1.3
    npk = df[["N", "P", "K"]].sum(axis=1).to_numpy()
    npk_norm = (npk - npk.min()) / (npk.max() - npk.min() + 1e-9)
    fator_nutrientes = 0.7 + 0.6 * npk_norm

    # Base por cultura: rendimento de referencia reprodutivel por label
    culturas = df["label"].unique()
    base_por_cultura = {
        c: rng.uniform(2500, 6000) for c in sorted(culturas)
    }
    base = df["label"].map(base_por_cultura).to_numpy()

    produtividade = base * (0.45 + 0.55 * fator_ambiente) * fator_nutrientes
    # Ruido gaussiano ~5% para evitar relacao deterministica
    ruido = rng.normal(0, 0.05, size=len(df)) * produtividade
    produtividade = np.clip(produtividade + ruido, 300, None)
    return np.round(produtividade, 2)


def adicionar_telemetria(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona timestamp (serie temporal), sensor_id e luminosity (LDR)."""
    n = len(df)

    # Serie temporal: leituras espalhadas nos ultimos 180 dias, ordenadas
    inicio = datetime(2026, 1, 1)
    minutos = np.sort(rng.integers(0, 180 * 24 * 60, size=n))
    df["timestamp"] = [inicio + timedelta(minutes=int(m)) for m in minutos]

    # sensor_id: S001..S010
    df["sensor_id"] = [f"S{1 + rng.integers(0, N_SENSORES):03d}" for _ in range(n)]

    # Luminosity (LDR, lux 0..100k): correlacionada de leve com a temperatura + ruido
    base_lux = (df["temperature"].to_numpy() / 40.0) * 70000
    lux = np.clip(base_lux + rng.normal(0, 12000, size=n), 0, 100000)
    df["luminosity"] = np.round(lux, 1)
    return df


def main() -> None:
    if not RAW_CSV.exists():
        raise FileNotFoundError(
            f"CSV base nao encontrado: {RAW_CSV}\n"
            "Baixe de farm-tech-fase3-cap-10 (branch Main, src/)."
        )

    df = pd.read_csv(RAW_CSV)
    print(f"[OK] Base carregada: {df.shape[0]} linhas, colunas {list(df.columns)}")

    df = adicionar_telemetria(df)
    df["produtividade_kg_ha"] = engenhar_produtividade(df)

    # Renomeia para nomes do dominio FarmTech (mantendo N/P/K)
    df = df.rename(columns={
        "temperature": "temperatura",
        "humidity": "umidade",
        "ph": "ph",
        "rainfall": "chuva_mm",
        "label": "cultura",
    })

    # Ordena colunas: telemetria -> agronomicas -> alvo
    cols = [
        "timestamp", "sensor_id", "cultura",
        "temperatura", "umidade", "ph", "luminosity",
        "N", "P", "K", "chuva_mm",
        "produtividade_kg_ha",
    ]
    df = df[cols].sort_values("timestamp").reset_index(drop=True)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"[OK] Dataset processado salvo: {OUT_CSV}")
    print(f"     {len(df)} linhas, {df['cultura'].nunique()} culturas")
    print(f"     produtividade_kg_ha: min={df['produtividade_kg_ha'].min():.0f} "
          f"media={df['produtividade_kg_ha'].mean():.0f} "
          f"max={df['produtividade_kg_ha'].max():.0f}")


if __name__ == "__main__":
    main()
