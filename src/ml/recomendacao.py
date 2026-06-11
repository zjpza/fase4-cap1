"""
recomendacao.py — FarmTech Solutions / Fase 4 CAP 1

Motor de recomendacao de manejo. A partir da produtividade prevista pelo modelo de
regressao e das leituras atuais (umidade, pH, NPK), gera acoes praticas:

  - volume de irrigacao (m3/ha) para aproximar a umidade da faixa otima;
  - ajuste de pH (calagem/acidificacao);
  - reforco de nutrientes (N, P, K).

As recomendacoes sao persistidas na tabela `acoes_irrigacao` do banco.

Regras baseadas nas faixas agronomicas usadas em generate_dataset.py
(umidade otima ~70%, pH otimo ~6.5).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "farmtech.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}")

# Faixas de referencia
UMIDADE_OTIMA = 70.0       # %
PH_MIN, PH_MAX = 6.0, 7.0  # faixa neutra desejavel
NPK_MIN = 40.0             # limiar abaixo do qual sugere reforco (kg/ha)

# Conversao didatica: 1 ponto percentual de umidade ~ 10 m3/ha de agua
M3_POR_PONTO_UMIDADE = 10.0


def recomendar(produtividade_kg_ha: float, umidade: float, ph: float,
               n: float, p: float, k: float) -> dict:
    """Gera volume de irrigacao (m3/ha) e texto de recomendacao."""
    partes = []

    # Irrigacao: cobre o deficit ate a umidade otima
    deficit = max(0.0, UMIDADE_OTIMA - umidade)
    volume_m3 = round(deficit * M3_POR_PONTO_UMIDADE, 1)
    if volume_m3 > 0:
        partes.append(f"Irrigar ~{volume_m3:.0f} m3/ha (umidade atual {umidade:.0f}%, "
                      f"{deficit:.0f} pontos abaixo do otimo de {UMIDADE_OTIMA:.0f}%).")
    else:
        partes.append("Umidade adequada; sem necessidade de irrigacao.")

    # pH
    if ph < PH_MIN:
        partes.append(f"pH acido ({ph:.1f}): aplicar calagem para elevar a ~6.5.")
    elif ph > PH_MAX:
        partes.append(f"pH alcalino ({ph:.1f}): corrigir para ~6.5.")
    else:
        partes.append(f"pH na faixa ideal ({ph:.1f}).")

    # Nutrientes
    baixos = [nome for nome, val in (("N", n), ("P", p), ("K", k)) if val < NPK_MIN]
    if baixos:
        partes.append("Reforcar nutriente(s): " + ", ".join(baixos) + ".")
    else:
        partes.append("Niveis de NPK satisfatorios.")

    texto = (f"Produtividade media observada: {produtividade_kg_ha:.0f} kg/ha. "
             + " ".join(partes))
    return {"volume_m3": volume_m3, "recomendacao_ml": texto}


def gerar_para_culturas() -> pd.DataFrame:
    """
    Calcula a media das leituras por cultura, gera uma recomendacao para cada uma
    e grava em `acoes_irrigacao`. Retorna o que foi inserido.
    """
    query = """
        SELECT c.id AS cultura_id, c.nome AS cultura,
               AVG(l.umidade) AS umidade, AVG(l.ph) AS ph,
               AVG(l.n) AS n, AVG(l.p) AS p, AVG(l.k) AS k,
               AVG(l.produtividade_kg_ha) AS produtividade
        FROM leituras_sensor l
        JOIN culturas c ON c.id = l.cultura_id
        GROUP BY c.id, c.nome
    """
    df = pd.read_sql(query, ENGINE)

    registros = []
    for _, r in df.iterrows():
        rec = recomendar(r["produtividade"], r["umidade"], r["ph"],
                         r["n"], r["p"], r["k"])
        registros.append({
            "cultura_id": int(r["cultura_id"]),
            "data": date.today().isoformat(),
            "volume_m3": rec["volume_m3"],
            "recomendacao_ml": rec["recomendacao_ml"],
        })

    saida = pd.DataFrame(registros)
    # Limpa recomendacoes anteriores antes de regravar
    with ENGINE.begin() as conn:
        conn.execute(text("DELETE FROM acoes_irrigacao"))
    saida.to_sql("acoes_irrigacao", ENGINE, if_exists="append", index=False)
    return saida


if __name__ == "__main__":
    saida = gerar_para_culturas()
    print(f"[OK] {len(saida)} recomendacoes gravadas em acoes_irrigacao.")
    for _, r in saida.head(5).iterrows():
        print(f"  cultura_id={r['cultura_id']:>2}  vol={r['volume_m3']:>6.0f} m3/ha  "
              f"{r['recomendacao_ml'][:80]}...")
