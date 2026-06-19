"""
simulacao.py — FarmTech Solutions / Fase 4 CAP 1
Issue #9 (ESP32/Wokwi) — coleta de dados via sensores.

Simula em Python a telemetria que um ESP32 com DHT22 (temperatura/umidade),
sensor de pH e LDR (luminosidade) enviaria do campo ao longo do tempo. Gera
leituras realistas com ciclo diario (dia/noite) e ruido, servindo de alternativa
a execucao no hardware/Wokwi.

Gera um stream de telemetria pura (timestamp, sensor_id, temperatura, umidade,
ph, luminosity), correspondente as colunas de sensor da tabela `leituras_sensor`.
Nao inclui cultura, NPK nem o alvo de produtividade (que vem de outras fontes),
portanto NAO substitui o dataset de treino usado por load_to_sql.py.

Saida: src/data/processed/simulacao_sensores.csv

Uso:
    python src/esp32/simulacao.py --sensores 5 --horas 48 --intervalo 30
"""
from __future__ import annotations

import argparse
import math
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_CSV = ROOT / "src" / "data" / "processed" / "simulacao_sensores.csv"

SEED = 42


def _ciclo_diario(hora: float, base: float, amplitude: float) -> float:
    """Onda senoidal com pico ~15h e vale ~3h (modela dia/noite)."""
    fase = (hora - 9) / 24 * 2 * math.pi
    return base + amplitude * math.sin(fase)


def simular(n_sensores: int, horas: int, intervalo_min: int,
            seed: int = SEED) -> pd.DataFrame:
    """Gera um DataFrame de leituras simuladas dos sensores."""
    rng = np.random.default_rng(seed)
    inicio = datetime(2026, 1, 1, 0, 0, 0)
    passos = int(horas * 60 / intervalo_min)

    registros = []
    for s in range(1, n_sensores + 1):
        sensor_id = f"S{s:03d}"
        # cada sensor tem um vies leve (microclima distinto)
        vies_temp = rng.normal(0, 1.5)
        vies_umid = rng.normal(0, 4.0)
        ph_base = rng.uniform(5.8, 7.2)
        for i in range(passos):
            ts = inicio + timedelta(minutes=i * intervalo_min)
            hora = ts.hour + ts.minute / 60.0

            temperatura = _ciclo_diario(hora, 24 + vies_temp, 6) + rng.normal(0, 0.8)
            # umidade anticorrelacionada com temperatura
            umidade = _ciclo_diario(hora, 65 + vies_umid, -15) + rng.normal(0, 3)
            umidade = float(np.clip(umidade, 0, 100))
            # luminosidade: ~0 a noite, pico ao meio-dia
            luz_frac = max(0.0, math.sin((hora - 6) / 12 * math.pi))
            luminosity = float(np.clip(luz_frac * 95000 + rng.normal(0, 3000), 0, 100000))
            # pH varia muito pouco
            ph = float(np.clip(ph_base + rng.normal(0, 0.05), 0, 14))

            registros.append({
                "timestamp": ts.isoformat(),
                "sensor_id": sensor_id,
                "temperatura": round(temperatura, 2),
                "umidade": round(umidade, 2),
                "ph": round(ph, 2),
                "luminosity": round(luminosity, 1),
            })

    return pd.DataFrame(registros).sort_values("timestamp").reset_index(drop=True)


def emitir_serial(df: pd.DataFrame, limite: int, atraso: float) -> None:
    """
    Reproduz no terminal o stream JSON que o firmware (arduino_sensores.ino)
    publica no Serial Monitor do Wokwi, uma leitura por linha. Serve de
    evidencia de coleta quando o Serial Monitor do Wokwi nao esta acessivel.
    """
    import time

    print("FarmTech ESP32 - coleta de sensores iniciada")
    for _, r in df.head(limite).iterrows():
        print(
            '{"temperatura":%.1f,"umidade":%.1f,"ph":%.2f,"luminosity":%.0f}'
            % (r["temperatura"], r["umidade"], r["ph"], r["luminosity"])
        )
        if atraso:
            time.sleep(atraso)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador de sensores ESP32 (FarmTech)")
    parser.add_argument("--sensores", type=int, default=5, help="numero de sensores")
    parser.add_argument("--horas", type=int, default=48, help="duracao em horas")
    parser.add_argument("--intervalo", type=int, default=30,
                        help="intervalo entre leituras (min)")
    parser.add_argument("--serial", action="store_true",
                        help="imprime as leituras como JSON no terminal "
                             "(espelha o Serial Monitor do Wokwi)")
    parser.add_argument("--limite", type=int, default=20,
                        help="nº de linhas JSON no modo --serial")
    parser.add_argument("--atraso", type=float, default=0.3,
                        help="segundos entre linhas no modo --serial")
    args = parser.parse_args()

    df = simular(args.sensores, args.horas, args.intervalo)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    if args.serial:
        emitir_serial(df, args.limite, args.atraso)
        return

    print(f"[OK] {len(df)} leituras de {args.sensores} sensores em {args.horas}h.")
    print(f"     salvo em {OUT_CSV} (telemetria de sensores, sem cultura/NPK/alvo)")
    print(df.groupby("sensor_id")[["temperatura", "umidade", "ph", "luminosity"]]
            .mean().round(1))


if __name__ == "__main__":
    main()
