# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

## FarmTech Solutions — Fase 4 CAP 1

## Assistente Agrícola Inteligente com Machine Learning e Dashboard Streamlit

## Nome do grupo

## 👨‍🎓 Integrantes:

- <a href="https://github.com/HenriqueSanchesSilva">Henrique Sanches Silva</a> — RM 570527
- <a href="https://github.com/zjpza">João Pedro Zavanela Andreu</a> — RM 570231
- <a href="https://github.com/Kayckxz">Kayck Gabriel Evangelista da Silva</a> — RM 572331
- <a href="https://github.com/lhboschi">Luis Henrique Laurentino Boschi</a> — RM 571352
- <a href="https://github.com/Trickmelo">Patrick Borges de Melo</a> — RM 574030

## 👩‍🏫 Professores:

### Tutor(a)

- Sabrina Otoni

### Coordenador(a)

- André Godoi

## 📜 Descrição

Esta fase do projeto FarmTech Solutions consolida o conhecimento técnico e analítico adquirido ao longo das fases anteriores, integrando Inteligência Artificial diretamente aos dados agrícolas já coletados, estruturados e armazenados. O foco é transformar dados em conhecimento, utilizando aprendizado de máquina supervisionado (regressão) para gerar previsões e insights relevantes sobre o campo, como a relação entre umidade, pH e produtividade, e o impacto das ações de irrigação e fertilização no rendimento final das culturas.

O protótipo de Assistente Agrícola Inteligente desenvolvido integra sensores IoT (reais ou simulados via Wokwi), um banco de dados simples e modelos de regressão (Scikit-Learn) para prever variáveis críticas do campo — umidade do solo, pH e rendimento esperado. Com base nas previsões, o sistema sugere ações futuras de irrigação e manejo agrícola, implementadas em Python e/ou C++. Os resultados são apresentados em um dashboard interativo desenvolvido com Streamlit, facilitando a interpretação dos dados por gestores agrícolas.

A solução demonstra domínio técnico e pensamento analítico na jornada completa: coleta de dados via sensores, armazenamento em banco SQL, modelagem ML com Scikit-Learn, avaliação via métricas (MAE, MSE, RMSE, R²), sugestão automatizada de ações e visualização interativa em tempo real. Tudo isso representa o início da Agricultura Cognitiva — tecnologia que aprende com os dados do campo para otimizar resultados de forma sustentável.

### Objetivos

- Modelar banco SQL para persistir dados de sensores IoT
- Treinar modelos de regressão (linear, múltipla e não linear) com Scikit-Learn
- Avaliar modelos com métricas estatísticas robustas
- Sugerir ações de irrigação e manejo baseadas em predições
- Criar dashboard Streamlit com métricas, gráficos e previsões em tempo real
- Documentar todo o pipeline e apresentar via vídeo de até 5 minutos

## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.github</b>: Nesta pasta ficarão os arquivos de configuração específicos do GitHub que ajudam a gerenciar e automatizar processos no repositório.

- <b>assets</b>: aqui estão os arquivos relacionados a elementos não-estruturados deste repositório, como imagens, logos e screenshots do Streamlit.

- <b>config</b>: Posicione aqui arquivos de configuração que são usados para definir parâmetros e ajustes do projeto.

- <b>document</b>: aqui estão todos os documentos do projeto que as atividades poderão pedir. Na subpasta "other", adicione documentos complementares e menos importantes.

- <b>scripts</b>: Posicione aqui scripts auxiliares para tarefas específicas do seu projeto. Exemplo: deploy, migrações de banco de dados, backups.

- <b>src</b>: Todo o código fonte criado para o desenvolvimento do projeto.
  - <b>src/data</b>: Dataset simulado de sensores agrícolas e scripts de ETL (geração, feature engineering, ingestão SQL).
  - <b>src/sql</b>: Schema DDL (SQLite) e seed data para persistência de dados IoT. Subpasta <b>src/sql/oracle</b>: schema, seed e <b>consultas exploratórias</b> para o Oracle Database da FIAP (entrega obrigatória).
  - <b>src/ml</b>: Notebooks de análise exploratória, treinamento de modelos de regressão (Scikit-Learn), avaliação de métricas (MAE, MSE, RMSE, R²) e script de predição.
  - <b>src/dashboard</b>: Aplicação Streamlit com métricas de desempenho, gráficos de correlação, previsões em tempo real e recomendações de irrigação para gestores agrícolas.

- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).

## 🔧 Como executar o código

### Pré-requisitos

- Python 3.10+
- pip
- Git
- (Opcional, entrega obrigatória) Acesso ao **Oracle Database da FIAP** + **SQL Developer**

### Banco de dados — persistência dupla (Oracle FIAP + SQLite)

A persistência segue uma estratégia de **duplo backend**, resolvida em `src/db.py`:

- **Oracle Database (FIAP)** — entrega obrigatória. Usado automaticamente quando há
  credencial válida no arquivo `.env`. Criação, importação e consultas exploratórias
  documentadas passo a passo (com prints) em **[`docs/oracle_import.md`](docs/oracle_import.md)**.
- **SQLite local** (`farmtech.db`) — _fallback_ automático: garante que dashboard e ML
  rodem mesmo sem credencial (ex.: gravação de vídeo offline).

Para usar o Oracle, copie `.env.example` para `.env` e preencha a senha:

```bash
cp .env.example .env        # ORACLE_USER / ORACLE_PASSWORD / ORACLE_DSN
```

Sem `.env`, todo o pipeline funciona no SQLite sem nenhuma configuração extra. O dashboard
exibe um selo indicando a fonte ativa (**Oracle FIAP** ou **SQLite local**).

### Passo a passo

1. Clone o repositório:

```bash
git clone https://github.com/zjpza/fase4-cap1.git
cd fase4-cap1
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

> O banco `farmtech.db` não é versionado: ele é regenerado pelos scripts abaixo.
> Rode os passos na ordem indicada.

3. Gere o dataset processado (a partir da base agronômica em `src/data/raw`):

```bash
python src/data/generate_dataset.py
```

Isso cria `src/data/processed/farmtech_dataset.csv` com a telemetria de sensores e o
alvo de regressão `produtividade_kg_ha`.

4. Crie e popule o banco de dados:

```bash
python src/data/load_to_sql.py
```

O script lê o CSV processado, trata nulos/duplicatas e popula as tabelas. Ele **sempre**
popula o SQLite (`farmtech.db`) e, se houver `.env` com credencial válida, popula também o
**Oracle FIAP** (recriando o schema `src/sql/oracle/01_schema_oracle.sql`). Detalhes do
modelo em `src/sql/README_SQL.md`; importação no SQL Developer em
[`docs/oracle_import.md`](docs/oracle_import.md).

5. Treine e avalie o modelo de Machine Learning (rode os notebooks na ordem):

```bash
jupyter notebook src/ml/01_eda.ipynb
jupyter notebook src/ml/02_modelagem.ipynb
jupyter notebook src/ml/03_avaliacao.ipynb
```

6. Execute o dashboard Streamlit:

```bash
streamlit run src/dashboard/app.py
```

O dashboard ficará disponível em `http://localhost:8501`.

## 📎 Links e Observações

- <b>Vídeo demonstrativo (Parte 1)</b>: https://youtu.be/iBv6HP34Jf8
- <b>Vídeo demonstrativo (Parte 2)</b>: https://youtu.be/gV3HLYRzr5Y


## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/zjpza/fase4-cap1">FarmTech Solutions — Fase 4 CAP 1</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
