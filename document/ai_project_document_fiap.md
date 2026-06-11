
<img src="../assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=30% height=30%>

# AI Project Document - Módulo 1 - FIAP

## Nome do Grupo

> _Preencher com o nome do grupo._

#### Nomes dos integrantes do grupo

- Henrique Sanches Silva - RM 570527
- João Pedro Zavanela Andreu - RM 570231
- Kayck Gabriel Evangelista da Silva - RM 572331
- Luis Henrique Laurentino Boschi - RM 571352
- Patrick Borges de Melo - RM 574030

## Sumário

[1. Introdução](#c1)

[2. Visão Geral do Projeto](#c2)

[3. Desenvolvimento do Projeto](#c3)

[4. Resultados e Avaliações](#c4)

[5. Conclusões e Trabalhos Futuros](#c5)

[6. Referências](#c6)

[Anexos](#c7)

<br>

# <a name="c1"></a>1. Introdução

## 1.1. Escopo do Projeto

### 1.1.1. Contexto da Inteligência Artificial

O agronegócio é um dos setores em que a Inteligência Artificial tem avançado com
mais rapidez, tanto no Brasil quanto no exterior. A combinação de sensores de baixo
custo (IoT), conectividade no campo e aprendizado de máquina deu origem ao que se
chama de Agricultura de Precisão: o uso de dados para decidir, talhão a talhão,
quando irrigar, adubar ou corrigir o solo. As aplicações vão de modelos preditivos
de produtividade e detecção de pragas por visão computacional até a automação de
máquinas agrícolas. No Brasil, com peso expressivo do agro na economia, soluções
que aumentam a eficiência do uso de água e insumos têm impacto direto em custo e
sustentabilidade.

Este projeto se posiciona nesse contexto como um protótipo de Agricultura Cognitiva:
um sistema que aprende com os dados do campo para apoiar a tomada de decisão.

### 1.1.2. Descrição da Solução Desenvolvida

A FarmTech Solutions desenvolveu um Assistente Agrícola Inteligente. A solução coleta
leituras de sensores (temperatura, umidade, pH e luminosidade), persiste esses dados
em um banco SQL e treina um modelo de regressão para prever a produtividade da
cultura em kg/ha. A partir da previsão e das condições atuais do solo, o sistema
sugere ações de manejo: volume de irrigação, ajuste de pH e reforço de nutrientes.
Tudo é apresentado em um dashboard interativo, que permite ao gestor agrícola
explorar correlações, simular cenários e visualizar as recomendações.

O dado agronômico de base reaproveita o trabalho da Fase 3 do grupo (2200 amostras
com N, P, K, temperatura, umidade, pH e chuva), adaptado ao contexto de sensores IoT
da Fase 4.

# <a name="c2"></a>2. Visão Geral do Projeto

## 2.1. Objetivos do Projeto

- Modelar um banco de dados SQL para persistir as leituras dos sensores IoT.
- Treinar e comparar modelos de regressão (linear, regularizada e não linear) com
  Scikit-Learn para prever a produtividade.
- Avaliar os modelos com métricas estatísticas (MAE, MSE, RMSE, R²).
- Gerar recomendações automáticas de irrigação e manejo a partir das previsões.
- Disponibilizar um dashboard interativo (Streamlit) com métricas, gráficos e
  previsões em tempo real.
- Demonstrar a etapa de coleta via ESP32/Wokwi (ou simulação equivalente em Python).

## 2.2. Público-Alvo

Gestores e técnicos agrícolas (agrônomos, cooperativas, produtores de médio porte)
que precisam de apoio à decisão sobre irrigação e manejo, sem exigir conhecimento
técnico em ciência de dados. A interface em dashboard foi pensada para esse perfil.

## 2.3. Metodologia

O desenvolvimento seguiu a sequência natural de um projeto de dados, dividido em
blocos por dependência:

1. **Dados e banco**: geração do dataset (telemetria + alvo de produtividade) e
   modelagem do banco SQL relacional.
2. **Machine Learning**: análise exploratória, treino e seleção de modelos de
   regressão por validação cruzada, e avaliação no conjunto de teste.
3. **Aplicação**: dashboard Streamlit consumindo o modelo treinado e o banco.
4. **Coleta IoT**: firmware ESP32 (Wokwi) e simulador Python da telemetria.
5. **Documentação e entrega**: este documento, README e vídeos.

A reprodutibilidade foi garantida com semente fixa (SEED = 42) em todas as etapas
estocásticas.

# <a name="c3"></a>3. Desenvolvimento do Projeto

## 3.1. Tecnologias Utilizadas

| Categoria | Tecnologias |
| --------- | ----------- |
| Linguagem | Python 3.10+ |
| Dados | pandas, numpy |
| Machine Learning | scikit-learn, joblib |
| Banco de dados | SQLite, SQLAlchemy |
| Visualização | Streamlit, Plotly, matplotlib, seaborn |
| Notebooks | Jupyter |
| IoT | ESP32 (Wokwi), C++/Arduino, DHT22, LDR |

## 3.2. Modelagem e Algoritmos

O problema foi tratado como **regressão supervisionada**, com alvo
`produtividade_kg_ha`. As features são as leituras de sensores e variáveis
agronômicas (temperatura, umidade, pH, luminosidade, N, P, K, chuva) mais a cultura
(categórica, via one-hot). O pré-processamento (padronização das numéricas e one-hot
da cultura) é definido em um único módulo (`feature_engineering.py`) e encapsulado
em um `Pipeline`, garantindo o mesmo tratamento no treino, na avaliação e na predição.

Quatro modelos foram comparados:

- **Linear Regression**: baseline.
- **Ridge**: regressão linear regularizada (controla overfitting).
- **Polynomial (grau 2) + Ridge**: captura relações não lineares entre as variáveis.
- **Random Forest Regressor**: modelo de árvore, não linear, robusto a interações.

A escolha foi feita pelo maior R² médio na validação cruzada de 5 folds.

## 3.3. Treinamento e Teste

O conjunto (2200 registros) foi dividido em 80% treino e 20% teste
(`random_state=42`). A comparação dos modelos usou validação cruzada de 5 folds sobre
o treino; o modelo escolhido foi retreinado no treino completo e avaliado no teste.

Resultado da validação cruzada (R² médio):

| Modelo | R² médio | RMSE médio |
| ------ | -------- | ---------- |
| Polynomial (grau 2) + Ridge | 0.966 | 193 |
| Random Forest | 0.961 | 205 |
| Linear Regression | 0.956 | 219 |
| Ridge | 0.956 | 220 |

Modelo selecionado: **Polynomial (grau 2) + Ridge**.

# <a name="c4"></a>4. Resultados e Avaliações

## 4.1. Análise dos Resultados

No conjunto de teste, o modelo selecionado obteve:

| Métrica | Valor |
| ------- | ----- |
| MAE | ~143 kg/ha |
| MSE | ~36.400 |
| RMSE | ~191 kg/ha |
| R² | ~0.96 |

O erro médio absoluto de ~143 kg/ha é pequeno frente à faixa do alvo (de ~1600 a
~7600 kg/ha), e os resíduos se distribuem em torno de zero sem padrão evidente, o que
indica um bom ajuste.

É importante registrar que o alvo `produtividade_kg_ha` é **sintético**: foi
engenheirado a partir das próprias variáveis em `generate_dataset.py`, já que a base
da Fase 3 era de classificação e não possuía um alvo contínuo. Por isso o R² alto é,
em parte, consequência do desenho do dataset, e não apenas da qualidade do modelo. O
objetivo do projeto é demonstrar o pipeline de regressão completo (treino, validação,
métricas, predição e recomendação), e não afirmar valores reais de produtividade.

## 4.2. Feedback dos Usuários

A avaliação foi feita internamente pelo grupo, usando o dashboard como ferramenta de
inspeção. O fluxo de simular variáveis e obter previsão e recomendação em tempo real
se mostrou intuitivo. O feedback formal de usuários externos fica como trabalho futuro.

# <a name="c5"></a>5. Conclusões e Trabalhos Futuros

A solução atingiu os objetivos propostos: há um banco SQL populado, um pipeline de
regressão treinado e avaliado por métricas robustas, um motor de recomendações de
manejo e um dashboard interativo que integra tudo, além da demonstração da coleta via
ESP32/Wokwi.

**Pontos fortes:** pipeline reprodutível e modular, com um único ponto de verdade para
as features; integração de ponta a ponta (sensor → banco → modelo → dashboard);
coerência com os trabalhos anteriores do grupo.

**Pontos a melhorar:** o alvo é sintético, o que limita a interpretação dos resultados
como produtividade real; a coleta IoT é simulada.

**Plano de ações futuro:**

1. Substituir o alvo sintético por dados reais de colheita.
2. Coletar telemetria real de sensores em campo e ingerir de forma contínua.
3. Adicionar previsão de necessidade hídrica como alvo secundário.
4. Publicar o dashboard na nuvem (Streamlit Community Cloud) para acesso remoto.

# <a name="c6"></a>6. Referências

- Documentação Scikit-Learn: https://scikit-learn.org
- Documentação Streamlit: https://docs.streamlit.io
- Documentação Plotly: https://plotly.com/python
- Simulador Wokwi (ESP32): https://wokwi.com
- Base agronômica reutilizada (Fase 3 do grupo): repositório `farm-tech-fase3-cap-10`.

# <a name="c7"></a>Anexos

## Estrutura do repositório

- `src/data` - geração do dataset, engenharia de atributos e ingestão SQL.
- `src/sql` - schema do banco e dicionário de dados (`README_SQL.md`).
- `src/ml` - notebooks de EDA, modelagem e avaliação, predição e recomendação.
- `src/dashboard` - aplicação Streamlit.
- `src/esp32` - firmware ESP32/Wokwi e simulador Python.
- `docs/esp32.md` - documentação da coleta IoT.

## Capturas de tela

_Adicionar em `assets/screenshots/`: dashboard (abas Resumo, Correlações, Predições),
circuito no Wokwi e Serial Monitor com as leituras._
