"""
app.py — FarmTech Solutions / Fase 4 CAP 1
Dashboard interativo (Streamlit + Plotly) do Assistente Agricola Inteligente.

5 abas:
  1. Resumo       - indicadores gerais do campo
  2. Correlacoes  - mapa de calor + dispersao
  3. Predicoes    - previsao de produtividade em tempo real + recomendacao
  4. Tendencias   - series temporais por cultura
  5. Acoes        - recomendacoes de manejo gravadas no banco

Pre-requisitos: banco populado (load_to_sql.py) e modelo treinado (02_modelagem.ipynb).
Execute: streamlit run src/dashboard/app.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "farmtech.db"
DATA_DIR = ROOT / "src" / "data"
ML_DIR = ROOT / "src" / "ml"

# Reusa feature_engineering (definicao canonica de features) e o modulo de predicao
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))
import feature_engineering as fe  # noqa: E402


def _carregar_modulo(nome: str, caminho: Path):
    """Importa um modulo cujo arquivo comeca com digito (ex.: 04_predict.py)."""
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


predict = _carregar_modulo("predict", ML_DIR / "04_predict.py")
recomendacao = _carregar_modulo("recomendacao", ML_DIR / "recomendacao.py")

ENGINE = create_engine(f"sqlite:///{DB_PATH}")

st.set_page_config(page_title="FarmTech - Assistente Agricola",
                   page_icon="🌱", layout="wide")


# ---------------------------------------------------------------------
# Acesso a dados (cache)
# ---------------------------------------------------------------------
@st.cache_data
def carregar_leituras() -> pd.DataFrame:
    query = """
        SELECT l.timestamp, l.sensor_id, c.nome AS cultura,
               l.temperatura, l.umidade, l.ph, l.luminosity,
               l.n, l.p, l.k, l.chuva_mm, l.produtividade_kg_ha
        FROM leituras_sensor l
        JOIN culturas c ON c.id = l.cultura_id
    """
    df = pd.read_sql(query, ENGINE, parse_dates=["timestamp"])
    return df


@st.cache_data
def carregar_acoes() -> pd.DataFrame:
    query = """
        SELECT c.nome AS cultura, a.data, a.volume_m3, a.recomendacao_ml
        FROM acoes_irrigacao a
        JOIN culturas c ON c.id = a.cultura_id
        ORDER BY a.volume_m3 DESC
    """
    return pd.read_sql(query, ENGINE)


@st.cache_data
def metricas_modelo() -> dict:
    """Recalcula metricas no conjunto de teste (mesmo split do notebook 03)."""
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                                  r2_score)
    import numpy as np

    df = fe.carregar_dados()
    X, y = fe.separar_xy(df)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model, meta = predict._carregar()
    y_pred = model.predict(X_test)
    return {
        "modelo": meta["melhor_modelo"],
        "MAE": mean_absolute_error(y_test, y_pred),
        "RMSE": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "R2": r2_score(y_test, y_pred),
    }


# ---------------------------------------------------------------------
# Carrega dados base
# ---------------------------------------------------------------------
if not DB_PATH.exists():
    st.error("Banco farmtech.db nao encontrado. Rode antes: "
             "python src/data/load_to_sql.py")
    st.stop()

df = carregar_leituras()

st.title("🌱 FarmTech Solutions — Assistente Agricola Inteligente")
st.caption("Pipeline de Machine Learning sobre dados de sensores IoT | Fase 4 CAP 1")

aba_resumo, aba_corr, aba_pred, aba_tend, aba_acoes = st.tabs(
    ["Resumo", "Correlacoes", "Predicoes", "Tendencias", "Acoes"]
)

# ---------------------------------------------------------------------
# Aba 1 - Resumo
# ---------------------------------------------------------------------
with aba_resumo:
    st.subheader("Indicadores gerais")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Culturas monitoradas", df["cultura"].nunique())
    c2.metric("Leituras de sensores", f"{len(df):,}".replace(",", "."))
    c3.metric("Umidade media", f"{df['umidade'].mean():.1f} %")
    c4.metric("Produtividade media", f"{df['produtividade_kg_ha'].mean():.0f} kg/ha")

    c5, c6 = st.columns(2)
    c5.metric("pH medio", f"{df['ph'].mean():.2f}")
    c6.metric("Chuva media", f"{df['chuva_mm'].mean():.0f} mm")

    st.markdown("#### Produtividade media por cultura")
    prod = (df.groupby("cultura")["produtividade_kg_ha"].mean()
              .sort_values(ascending=False).reset_index())
    fig = px.bar(prod, x="cultura", y="produtividade_kg_ha",
                 color="produtividade_kg_ha", color_continuous_scale="YlGn",
                 labels={"produtividade_kg_ha": "kg/ha"})
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------
# Aba 2 - Correlacoes
# ---------------------------------------------------------------------
with aba_corr:
    st.subheader("Mapa de correlacao")
    num_cols = fe.NUMERIC_FEATURES + [fe.TARGET]
    corr = df[num_cols].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdYlGn",
                    zmin=-1, zmax=1, aspect="auto")
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Dispersao entre variaveis")
    c1, c2 = st.columns(2)
    eixo_x = c1.selectbox("Eixo X", fe.NUMERIC_FEATURES, index=1)  # umidade
    eixo_y = c2.selectbox("Eixo Y", num_cols, index=len(num_cols) - 1)  # alvo
    fig = px.scatter(df, x=eixo_x, y=eixo_y, color="cultura",
                     opacity=0.6, hover_data=["cultura"])
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------
# Aba 3 - Predicoes
# ---------------------------------------------------------------------
with aba_pred:
    st.subheader("Previsao de produtividade em tempo real")
    met = metricas_modelo()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Modelo", met["modelo"])
    m2.metric("MAE", f"{met['MAE']:.0f} kg/ha")
    m3.metric("RMSE", f"{met['RMSE']:.0f} kg/ha")
    m4.metric("R2", f"{met['R2']:.3f}")

    st.markdown("Ajuste as variaveis e clique em **Prever**:")
    col1, col2, col3 = st.columns(3)
    entrada = {
        "cultura": col1.selectbox("Cultura", sorted(df["cultura"].unique())),
        "temperatura": col1.slider("Temperatura (C)", -5.0, 50.0, 25.0),
        "umidade": col1.slider("Umidade (%)", 0.0, 100.0, 70.0),
        "ph": col2.slider("pH", 0.0, 14.0, 6.5),
        "luminosity": col2.slider("Luminosidade (lux)", 0.0, 100000.0, 45000.0),
        "chuva_mm": col2.slider("Chuva (mm)", 0.0, 300.0, 120.0),
        "n": col3.slider("Nitrogenio (N)", 0.0, 140.0, 90.0),
        "p": col3.slider("Fosforo (P)", 0.0, 145.0, 42.0),
        "k": col3.slider("Potassio (K)", 0.0, 205.0, 43.0),
    }

    if st.button("Prever", type="primary"):
        prod = predict.prever(entrada)
        st.success(f"Produtividade prevista: **{prod:.0f} kg/ha**")
        rec = recomendacao.recomendar(prod, entrada["umidade"], entrada["ph"],
                                      entrada["n"], entrada["p"], entrada["k"])
        st.info("Recomendacao de manejo: " + rec["recomendacao_ml"])
        if rec["volume_m3"] > 0:
            st.write(f"💧 Volume de irrigacao sugerido: **{rec['volume_m3']:.0f} m3/ha**")

# ---------------------------------------------------------------------
# Aba 4 - Tendencias
# ---------------------------------------------------------------------
with aba_tend:
    st.subheader("Tendencias temporais")
    culturas = st.multiselect("Culturas", sorted(df["cultura"].unique()),
                              default=list(df["cultura"].unique())[:3])
    variavel = st.selectbox("Variavel", ["produtividade_kg_ha", "umidade",
                                         "ph", "temperatura"])
    if culturas:
        sub = df[df["cultura"].isin(culturas)].copy()
        sub["dia"] = sub["timestamp"].dt.date
        serie = (sub.groupby(["dia", "cultura"])[variavel].mean().reset_index())
        fig = px.line(serie, x="dia", y=variavel, color="cultura", markers=False)
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Selecione ao menos uma cultura.")

# ---------------------------------------------------------------------
# Aba 5 - Acoes
# ---------------------------------------------------------------------
with aba_acoes:
    col_t, col_b = st.columns([4, 1])
    col_t.subheader("Recomendacoes de manejo")
    if col_b.button("🔄 Atualizar"):
        carregar_acoes.clear()
        st.rerun()
    acoes = carregar_acoes()
    if acoes.empty:
        st.warning("Nenhuma recomendacao gravada. Rode: python src/ml/recomendacao.py")
    else:
        st.dataframe(acoes, width="stretch", hide_index=True)
        st.download_button("Baixar recomendacoes (CSV)",
                           acoes.to_csv(index=False).encode("utf-8"),
                           file_name="recomendacoes_farmtech.csv",
                           mime="text/csv")
