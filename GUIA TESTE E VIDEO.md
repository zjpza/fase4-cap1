# Guia HIPER-DETALHADO — Teste, Prints e Vídeos
## FarmTech Solutions · Fase 4 CAP 1 — Previsão Inteligente na Agricultura

Este guia leva você do zero até a entrega: prepara o ambiente, **testa cada parte do
projeto com a saída esperada**, lista **todos os prints** (e onde salvar) e traz o
**roteiro falado + ações** dos 4 vídeos. Siga na ordem.

> **Regra de ouro:** rode **tudo** no mesmo ambiente — o conda `fiap`
> (Python 3.14, scikit-learn 1.8.0, streamlit 1.58.0, oracledb 4.0.1, python-dotenv).
> Misturar ambientes causa avisos de versão do scikit-learn no vídeo.

---

## 0. Mapa da entrega (enunciado → o que gravar)

São **4 vídeos** (YouTube *não listado*). Cada um cobre uma parte do enunciado:

| Vídeo | Parte do enunciado | Duração máx. | Foco principal |
| ----- | ------------------ | ------------ | -------------- |
| 1 | **PARTE 1** — Integração ML + dashboard Streamlit | 5 min | Pipeline ML conectado ao dashboard; bibliotecas; métricas/gráficos/previsões |
| 2 | **PARTE 2** — Algoritmos preditivos + recomendações | 5 min | Treino/validação (MAE, MSE, RMSE, R²); recomendações de irrigação/manejo |
| 3 | **IR ALÉM 1** — Integração IoT ↔ Banco de dados | 3 min | Ingestão/população automática no banco (Oracle SQL) |
| 4 | **IR ALÉM 2** — Dashboard analítico interativo | 5 min | Correlações, previsões, tendências; usabilidade para o gestor |

Critérios pontuados (10 pts): integração modelo↔dashboard (3), aplicação correta da
regressão + ações (3), clareza dos resultados no dashboard (2), domínio na apresentação
em vídeo (2). O **Ir Além 1 (banco)** foi o ponto fraco do trabalho anterior — por isso
este projeto tem **dupla persistência Oracle FIAP + SQLite**, documentação de importação
e consultas exploratórias. Dê **destaque ao banco** no vídeo 3.

---

## 1. Preparação do ambiente (fazer uma vez)

Abra o **PowerShell** na raiz do projeto:
`C:\Users\henri\Documents\ProjetosLocal\fase4-cap1`

### 1.1. Ativar o ambiente
```powershell
conda activate fiap
```

### 1.2. Instalar dependências
```powershell
pip install -r requirements.txt
```
Garante `numpy, pandas, scikit-learn, matplotlib, seaborn, joblib, sqlalchemy,
oracledb, python-dotenv, streamlit, plotly, jupyter`.

### 1.3. Configurar credenciais do Oracle FIAP
```powershell
Copy-Item .env.example .env
```
Abra `.env` e preencha:
```
ORACLE_USER=rm570527           # seu RM
ORACLE_PASSWORD=sua_senha_fiap # senha da FIAP
ORACLE_DSN=oracle.fiap.com.br:1521/ORCL
```
> O `.env` **não** é versionado (está no `.gitignore`). Sem ele, o projeto roda
> automaticamente no **SQLite local** (fallback) — útil se a rede da FIAP cair.

### 1.4. Conferir versões (opcional, sanidade)
```powershell
python -c "import sys, sklearn, streamlit, oracledb; print('py', sys.version.split()[0]); print('sklearn', sklearn.__version__, '| streamlit', streamlit.__version__, '| oracledb', oracledb.__version__)"
```
Esperado (aprox.): `py 3.14.x` · `sklearn 1.8.0 | streamlit 1.58.0 | oracledb 4.0.1`.

---

## 2. Bateria de testes (rode e confira a saída)

Execute na ordem. Para cada passo está a **saída esperada** e **o que observar**.
Quando indicado 📷, tire o print (ver seção 3).

### 2.1. Gerar o dataset processado
```powershell
python src/data/generate_dataset.py
```
Saída esperada:
```
[OK] Base carregada: 2200 linhas, colunas ['N', 'P', 'K', 'temperature', ...]
[OK] Dataset processado salvo: ...\src\data\processed\farmtech_dataset.csv
     2200 linhas, 22 culturas
     produtividade_kg_ha: min=1612 media=3348 max=7558
```
Observe: **2200 linhas, 22 culturas**. Cria `src/data/processed/farmtech_dataset.csv`.

### 2.2. Criar e popular o banco (Oracle + SQLite) — IR ALÉM 1
```powershell
python src/data/load_to_sql.py
```
Saída esperada:
```
[OK] Dataset carregado: 2200 linhas (0 removidas por nulo/duplicata)

=== Backend: SQLITE ===
[OK] Schema SQLite criado.
[OK] culturas inseridas: 22
[OK] leituras_sensor inseridas: 2200
     culturas           -> 22 registros
     leituras_sensor    -> 2200 registros
     acoes_irrigacao    -> 0 registros
     Top 5 culturas por produtividade media:
       grapes          100 leituras  ~6507 kg/ha
       ...
=== Backend: ORACLE ===
[OK] Schema Oracle criado.
[OK] culturas inseridas: 22
[OK] leituras_sensor inseridas: 2200
[OK] Ingestao concluida.
```
Observe: aparecem **os dois backends**. Se só aparecer SQLite e
`[INFO] Oracle nao configurado (.env)`, revise a senha no `.env`.
📷 **Print do terminal** com `=== Backend: ORACLE ===` e os counts → `assets/screenshots/oracle/03_carga.png`.

### 2.3. Gerar recomendações de manejo — PARTE 2
```powershell
python src/ml/recomendacao.py
```
Saída esperada:
```
[OK] 22 recomendacoes gravadas em acoes_irrigacao.
  cultura_id= 1  vol=     0 m3/ha  Produtividade media observada: 3550 kg/ha. Umidade adequada; ...
  ...
```
Observe: **22 recomendações** gravadas (uma por cultura), com volume de irrigação e texto.

### 2.4. Teste rápido de predição — PARTE 2
```powershell
python src/ml/04_predict.py
```
Saída esperada:
```
Entrada: {'temperatura': 25.0, 'umidade': 70.0, 'ph': 6.5, ...}
Produtividade prevista: ~3800 kg/ha
```
Observe: o modelo prevê produtividade para uma leitura de exemplo.

### 2.5. Notebooks de ML (EDA, modelagem, avaliação) — PARTE 2
```powershell
jupyter notebook
```
No navegador, abra e execute **na ordem** (menu *Run → Run All Cells*):
1. `src/ml/01_eda.ipynb` — estatística descritiva, histograma do alvo, mapa de
   correlação, boxplot por cultura.
2. `src/ml/02_modelagem.ipynb` — treina modelos (linear, múltipla, polinomial),
   escolhe o melhor e salva `models/modelo_farmtech.pkl`.
3. `src/ml/03_avaliacao.ipynb` — métricas no conjunto de teste e gráficos
   (previsto × real, resíduos).

Modelo vencedor: **Polynomial(grau2)+Ridge**. Métricas aproximadas:
**MAE ≈ 145 kg/ha · RMSE ≈ 194 kg/ha · R² ≈ 0.965**.
📷 **Print do mapa de correlação** (notebook 01) → `assets/screenshots/ml/01_metricas.png`
(ou print das métricas do notebook 03).

### 2.6. Dashboard Streamlit — PARTE 1 e IR ALÉM 2
```powershell
streamlit run src/dashboard/app.py
```
Abre em `http://localhost:8501`. Confira na **barra lateral** o selo
**🗄️ Fonte de dados: Oracle FIAP** (se `.env` ok) ou **SQLite local** (fallback).

As 5 abas:
- **Resumo** — indicadores (culturas, leituras, umidade/pH/chuva médios) + barras de
  produtividade por cultura. 📷 `assets/screenshots/dashboard/01_resumo.png`
- **Correlações** — mapa de calor + dispersão configurável. 📷 `assets/screenshots/dashboard/02_correlacoes.png`
- **Predições** — métricas do modelo (Modelo, MAE, RMSE, R²) + sliders. Ajuste e clique
  **Prever** → mostra produtividade prevista + recomendação. 📷 `assets/screenshots/dashboard/03_predicoes.png`
- **Tendências** — linha temporal por cultura/variável.
- **Ações** — tabela das recomendações geradas + botão *Baixar CSV* e *🔄 Atualizar*.

> Se a aba **Ações** estiver vazia, rode o passo 2.3 antes.

### 2.7. Banco no SQL Developer + consultas exploratórias — IR ALÉM 1
Siga `docs/oracle_import.md`. Resumo:
1. **Conexão**: New Connection → Name `farmtech-fiap`, User seu RM, Password senha FIAP,
   Hostname `oracle.fiap.com.br`, Port `1521`, Service name `ORCL` → **Test** (Success) → **Connect**.
   📷 `assets/screenshots/oracle/01_conexao.png`
2. **Schema**: abrir `src/sql/oracle/01_schema_oracle.sql` → **Run Script (F5)**. Cria
   `culturas`, `leituras_sensor`, `acoes_irrigacao` + índices.
   📷 `assets/screenshots/oracle/02_schema.png`
3. **Carga**: já feita pelo `load_to_sql.py` (passo 2.2). Confira em *Tables → LEITURAS_SENSOR → Data*.
4. **Consultas exploratórias**: abrir `src/sql/oracle/03_queries_exploratorias.sql` e
   rodar cada uma (Ctrl+Enter). São 7 perguntas de negócio:
   - Q1 volume de dados · Q2 ranking de produtividade por cultura · Q3 correlações `CORR()`
     · Q4 faixas médias por cultura · Q5 outliers por cultura (IQR) · Q6 atividade por sensor
     · Q7 recomendações geradas.
   📷 `oracle/04_query_correlacao.png` (Q3), `oracle/05_query_produtividade.png` (Q2),
   `oracle/06_query_outliers.png` (Q5).

### 2.8. (Opcional) Provar o fallback SQLite
Renomeie temporariamente o `.env` (ou esvazie a senha) e rode `python src/data/load_to_sql.py`:
deve aparecer só `=== Backend: SQLITE ===` e `[INFO] Oracle nao configurado`. Restaure o `.env` depois.
Isso mostra robustez (o projeto roda sem credencial).

### 2.9. (Opcional) Coleta de sensores ESP32 (Wokwi)
- Simulação em Python: `python src/esp32/simulacao.py` → gera `simulacao_sensores.csv`.
- Circuito no Wokwi: abra `src/esp32/diagram.json`/`arduino_sensores.ino` no
  [wokwi.com](https://wokwi.com), rode e veja o **Serial Monitor**.
  📷 `assets/screenshots/wokwi/01_circuito.png` e `wokwi/02_serial_monitor.png`.

---

## 3. Prints — checklist completo

Salve cada imagem com o **nome exato** abaixo (a documentação já aponta para eles).
Convenção em `assets/screenshots/README.md`.

### `assets/screenshots/oracle/` (entrega obrigatória — capriche)
- [ ] `01_conexao.png` — conexão SQL Developer testada (Status: Success)
- [ ] `02_schema.png` — `01_schema_oracle.sql` rodado; tabelas em *Connections*
- [ ] `03_carga.png` — terminal do `load_to_sql.py` com `=== Backend: ORACLE ===` + counts
- [ ] `04_query_correlacao.png` — Q3 (correlações) com resultado
- [ ] `05_query_produtividade.png` — Q2 (ranking por cultura)
- [ ] `06_query_outliers.png` — Q5 (outliers por cultura)

### `assets/screenshots/dashboard/`
- [ ] `01_resumo.png` — aba Resumo (com o selo da fonte de dados visível)
- [ ] `02_correlacoes.png` — mapa de calor / dispersão
- [ ] `03_predicoes.png` — sliders + “Produtividade prevista” + recomendação

### `assets/screenshots/ml/`
- [ ] `01_metricas.png` — mapa de correlação (nb 01) ou métricas MAE/RMSE/R² (nb 03)

### `assets/screenshots/wokwi/`
- [ ] `01_circuito.png` — circuito no Wokwi
- [ ] `02_serial_monitor.png` — Serial Monitor com leituras

> **Como tirar print no Windows:** `Win + Shift + S` (recorte) e salve com o nome exato
> na subpasta certa. Confira depois se a imagem abre normalmente.

---

## 4. Roteiro dos vídeos (fala + ações + tempo)

Dicas gerais: grave em **1080p**, áudio limpo, feche abas/notificações, deixe os comandos
**já testados** e o dashboard **já aberto** numa aba. Fale com calma. Mostre o **código**
e o **resultado**. *Não passe do tempo máximo.*

---

### 🎬 Vídeo 1 — PARTE 1 (Integração ML + Streamlit) · até 5 min

**Objetivo:** mostrar o pipeline de ML conectado ao dashboard, explicar as bibliotecas e
demonstrar métricas, gráficos e previsões em tempo real.

| Tempo | Ação na tela | Fala (roteiro) |
| ----- | ------------ | -------------- |
| 0:00–0:25 | Slide/título + estrutura de pastas no VS Code | “Olá, somos o grupo da FarmTech Solutions. Nesta Parte 1 mostramos a integração do nosso modelo de regressão com um dashboard interativo em Streamlit.” |
| 0:25–1:10 | Abrir `src/data/feature_engineering.py` e `src/ml/02_modelagem.ipynb` | “Usamos **scikit-learn** para o pipeline de ML: `ColumnTransformer` com `StandardScaler` nas numéricas e `OneHotEncoder` na cultura, dentro de um `Pipeline`. Testamos regressão linear, múltipla e polinomial; o melhor foi **Polynomial grau 2 + Ridge**.” |
| 1:10–1:40 | Mostrar `src/ml/04_predict.py` | “O modelo treinado é salvo em `.pkl` e carregado por este módulo de predição, que o dashboard reutiliza — um único ponto de verdade para as features.” |
| 1:40–2:10 | `streamlit run src/dashboard/app.py`; apontar o selo da fonte | “Subimos o dashboard com **Streamlit**. Repare no selo: a fonte de dados é o **Oracle FIAP**.” |
| 2:10–3:00 | Aba **Predições**: ler métricas, mexer sliders, clicar **Prever** | “Aqui as métricas do modelo: MAE em torno de 145 kg/ha e **R² 0.96**. Ajustando umidade, pH e NPK e clicando em Prever, a produtividade prevista atualiza em tempo real, com a recomendação de manejo.” |
| 3:00–4:00 | Aba **Resumo** e **Correlações** | “No Resumo, indicadores gerais e produtividade por cultura. Em Correlações, o mapa de calor mostra a relação de cada variável com a produtividade, e a dispersão é configurável.” |
| 4:00–4:40 | Aba **Tendências** | “As tendências temporais por cultura ajudam o gestor a acompanhar a evolução.” |
| 4:40–5:00 | Encerramento | “Assim integramos modelo e interface: do dado à decisão. Obrigado.” |

---

### 🎬 Vídeo 2 — PARTE 2 (Algoritmos preditivos + recomendações) · até 5 min

**Objetivo:** mostrar o pipeline completo (tratamento, treino, validação), as métricas
(MAE, MSE, RMSE, R²) e as recomendações de irrigação/manejo.

| Tempo | Ação na tela | Fala (roteiro) |
| ----- | ------------ | -------------- |
| 0:00–0:30 | Título + `src/ml/01_eda.ipynb` aberto | “Na Parte 2 detalhamos o pipeline de Machine Learning, da análise dos dados às recomendações de manejo.” |
| 0:30–1:30 | Rodar/percorrer **01_eda**: describe, histograma, correlação, boxplot | “Na EDA: 2200 leituras, 22 culturas. A produtividade varia por cultura; umidade, pH e chuva têm relação não-linear com o alvo — nenhuma variável sozinha explica tudo.” |
| 1:30–2:50 | **02_modelagem**: pré-processador, treino, comparação de modelos | “Tratamos os dados com `StandardScaler` e `OneHotEncoder`. Comparamos regressão linear, múltipla e polinomial por validação; o melhor foi **Polinomial grau 2 + Ridge**, salvo em `.pkl`.” |
| 2:50–3:50 | **03_avaliacao**: MAE/MSE/RMSE/R² + gráfico previsto×real e resíduos | “Na avaliação, no conjunto de teste: **MAE ≈ 145, RMSE ≈ 194, R² ≈ 0.965**. O gráfico previsto × real fica próximo da diagonal e os resíduos são bem distribuídos.” |
| 3:50–4:40 | Terminal: `python src/ml/recomendacao.py` e abrir aba **Ações** do dashboard | “Com as previsões, o motor de recomendação calcula o volume de irrigação para aproximar a umidade do ótimo e sugere ajuste de pH e reforço de NPK — 22 recomendações gravadas no banco e exibidas no dashboard.” |
| 4:40–5:00 | Encerramento | “Fechamos da modelagem à ação prática no campo. Obrigado.” |

---

### 🎬 Vídeo 3 — IR ALÉM 1 (Integração IoT ↔ Banco) · até 3 min

**Objetivo (este foi o ponto fraco antes — capriche):** mostrar a modelagem do banco, a
ingestão/população automática e atualização dos dados, de preferência em **SQL (Oracle)**.

| Tempo | Ação na tela | Fala (roteiro) |
| ----- | ------------ | -------------- |
| 0:00–0:25 | Abrir `src/sql/oracle/01_schema_oracle.sql` | “No Ir Além 1 modelamos o banco relacional dos sensores. Três tabelas: `culturas`, a tabela-fato `leituras_sensor` e `acoes_irrigacao`, com PKs `IDENTITY`, `CHECK`, chaves estrangeiras e índices.” |
| 0:25–1:00 | SQL Developer: conexão `farmtech-fiap` + rodar o schema (F5) | “Aqui no **SQL Developer**, conectados ao **Oracle da FIAP**, executamos o script de criação. As tabelas aparecem no painel de conexões.” |
| 1:00–1:50 | Terminal: `python src/data/load_to_sql.py` mostrando os dois backends | “A ingestão é **automática**: o `load_to_sql.py` lê o CSV processado, trata nulos e duplicatas, recria o schema e popula em lote. Ele grava **sempre no SQLite** local e **no Oracle** quando há credencial — persistência dupla. 22 culturas e 2200 leituras inseridas.” |
| 1:50–2:35 | SQL Developer: rodar Q1, Q2 e Q3 de `03_queries_exploratorias.sql` | “Explorando a base no Oracle: volume de dados, ranking de produtividade por cultura e as correlações com `CORR()` direto em SQL.” |
| 2:35–3:00 | Mostrar tabela `LEITURAS_SENSOR → Data` | “Os dados persistem prontos para o ML. Esse é o elo entre sensores, banco e IA. Obrigado.” |

> Mencione a **atualização**: re-rodar `load_to_sql.py` recria o schema e recarrega
> (idempotente); `recomendacao.py` atualiza a tabela `acoes_irrigacao`.

---

### 🎬 Vídeo 4 — IR ALÉM 2 (Dashboard analítico) · até 5 min

**Objetivo:** demonstrar o dashboard completo — correlações, previsões e tendências — e a
interpretação/usabilidade para o gestor.

| Tempo | Ação na tela | Fala (roteiro) |
| ----- | ------------ | -------------- |
| 0:00–0:30 | Dashboard aberto, barra lateral à vista | “No Ir Além 2 apresentamos o dashboard analítico em Streamlit, lendo direto do **Oracle FIAP** — veja o selo da fonte.” |
| 0:30–1:30 | Aba **Resumo** | “Indicadores gerais: 22 culturas, 2200 leituras, umidade e pH médios. As barras ordenam a produtividade por cultura — uva e banana no topo.” |
| 1:30–2:40 | Aba **Correlações**: heatmap + dispersão | “O mapa de calor mostra a força e o sinal de cada relação com a produtividade. Na dispersão, escolho os eixos — por exemplo umidade × produtividade — e vejo o padrão por cultura.” |
| 2:40–3:40 | Aba **Predições**: sliders + Prever | “Aqui o gestor simula cenários: ajusta variáveis e obtém a produtividade prevista e a recomendação de manejo na hora.” |
| 3:40–4:30 | Aba **Tendências** e aba **Ações** (com download CSV) | “As tendências temporais acompanham a evolução por cultura. Em Ações, as recomendações geradas pelo modelo, com exportação em CSV.” |
| 4:30–5:00 | Encerramento | “Uma interface clara e navegável, que transforma dados em decisão para o campo. Obrigado.” |

---

## 5. Checklist final de entrega

- [ ] Todos os testes da seção 2 rodaram com a saída esperada.
- [ ] Os prints da seção 3 estão salvos com os **nomes exatos** nas subpastas.
- [ ] Os 4 vídeos gravados (respeitando os tempos máximos) e subidos no YouTube **não listado**.
- [ ] Links colados no `README.md` (seção *Links e Observações*, linhas ~118–121),
      substituindo `<colocar_link_aqui>`.
- [ ] `git add -A && git commit` dos prints (o `.env` **não** entra — está ignorado).
- [ ] (Opcional) `git push`.

---

## 6. Troubleshooting

| Sintoma | Causa provável | Solução |
| ------- | -------------- | ------- |
| Só aparece `=== Backend: SQLITE ===` + `[INFO] Oracle nao configurado` | `.env` ausente/senha vazia | Preencher `ORACLE_PASSWORD` no `.env` |
| `[db] Oracle indisponivel (...)` | Sem rede/VPN da FIAP ou credencial errada | Conferir conexão e usuário/senha; o projeto cai pro SQLite e continua |
| `ORA-01017: invalid username/password` | Credencial incorreta | Revisar RM e senha no `.env` |
| `InconsistentVersionWarning` do scikit-learn | Modelo treinado em outro ambiente | Re-treinar no `fiap`: rodar `02_modelagem.ipynb` com o kernel do `fiap` |
| Aba **Ações** vazia | Recomendações não geradas | Rodar `python src/ml/recomendacao.py` e clicar **🔄 Atualizar** |
| `Dataset nao encontrado` no `load_to_sql` | Faltou gerar o CSV | Rodar `python src/data/generate_dataset.py` antes |
| Dashboard não abre | Streamlit não instalado no env ativo | `conda activate fiap` e `pip install -r requirements.txt` |
| Wokwi sem leituras | Simulação não iniciada | Clicar ▶ no Wokwi e abrir o Serial Monitor |

---

**Referências internas:** `docs/oracle_import.md` (passo a passo do banco) ·
`src/sql/oracle/03_queries_exploratorias.sql` (as 7 consultas) ·
`assets/screenshots/README.md` (convenção de prints) · `src/sql/README_SQL.md`
(dicionário de dados) · `README.md` (visão geral e execução).
