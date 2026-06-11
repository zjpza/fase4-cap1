# Machine Learning — FarmTech Solutions (Fase 4 CAP 1)

Pipeline de **regressão supervisionada** (Scikit-Learn) que prevê a produtividade
das culturas (`produtividade_kg_ha`) a partir das leituras de sensores e variáveis
agronômicas, e gera recomendações de manejo. Atende às Partes 1 e 2 do projeto.

## Estrutura

| Arquivo | Função |
| ------- | ------ |
| `01_eda.ipynb` | Análise exploratória: estatística, distribuição do alvo, correlações, produtividade por cultura. |
| `02_modelagem.ipynb` | Treino e comparação de modelos por validação cruzada (5-fold); salva o melhor em `models/`. |
| `03_avaliacao.ipynb` | Métricas no teste (MAE, MSE, RMSE, R²), real vs predito, resíduos, importância das variáveis. |
| `04_predict.py` | Função `prever(entrada)` que carrega o modelo e retorna a produtividade prevista. |
| `recomendacao.py` | Motor de recomendação (irrigação, pH, NPK); grava em `acoes_irrigacao`. |
| `models/` | Artefatos gerados: `modelo_farmtech.pkl` e `model_columns.json`. |

## Features e alvo

Definidos de forma canônica em `src/data/feature_engineering.py` (ponto único de
verdade, reusado por notebooks e predição):

- **Numéricas**: temperatura, umidade, ph, luminosity, n, p, k, chuva_mm
- **Categórica**: cultura (one-hot)
- **Alvo**: produtividade_kg_ha

O pré-processador (`StandardScaler` nas numéricas + `OneHotEncoder` na cultura) entra
dentro de um `Pipeline`, garantindo o mesmo tratamento no treino e na predição.

## Modelos comparados

LinearRegression, Ridge, Polynomial (grau 2) + Ridge e RandomForestRegressor.
Seleção pelo maior R² médio na validação cruzada de 5 folds.

### Resultado

Melhor modelo: **Polynomial (grau 2) + Ridge**. Métricas no conjunto de teste (20%):

| Métrica | Valor |
| ------- | ----- |
| MAE | ~143 kg/ha |
| RMSE | ~191 kg/ha |
| R² | ~0.96 |

> O R² alto reflete o desenho do dataset: o alvo é sintético, derivado das próprias
> variáveis em `generate_dataset.py` (ver `src/sql/README_SQL.md`). O objetivo é
> demonstrar o pipeline de regressão completo, não afirmar valores reais.

## Como executar

Pré-requisito: banco populado (`python src/data/load_to_sql.py`).

```bash
# 1. Notebooks na ordem (gera models/*.pkl)
jupyter notebook src/ml/01_eda.ipynb
jupyter notebook src/ml/02_modelagem.ipynb
jupyter notebook src/ml/03_avaliacao.ipynb

# 2. Predição de teste
python src/ml/04_predict.py

# 3. Gera e grava recomendações de manejo
python src/ml/recomendacao.py
```
