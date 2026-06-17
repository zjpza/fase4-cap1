"""
db.py — FarmTech Solutions / Fase 4 CAP 1

Resolver de conexao do banco. Ponto unico usado por toda a aplicacao
(ingestao, ML, dashboard) para decidir QUAL backend persiste/le os dados:

  - ORACLE FIAP  -> entrega obrigatoria. Usado quando ha credencial valida
                    no .env (ORACLE_USER/ORACLE_PASSWORD) e a conexao abre.
  - SQLite local -> fallback automatico (farmtech.db na raiz). Garante que o
                    dashboard e o ML rodem mesmo sem credencial (ex.: gravar
                    video em maquina sem acesso a rede da FIAP).

Padrao de conexao reaproveitado do repo farm-tech-fase2-cap-6 (oracledb thin,
DSN oracle.fiap.com.br:1521/ORCL), agora exposto via SQLAlchemy para reuso
com pandas (read_sql / to_sql).
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

ROOT = Path(__file__).resolve().parents[1]      # raiz do repo
DB_PATH = ROOT / "farmtech.db"
SQL_DIR = ROOT / "src" / "sql"

# Carrega o .env da raiz explicitamente (independe do diretorio de execucao).
load_dotenv(ROOT / ".env")

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN", "oracle.fiap.com.br:1521/ORCL")

# Backends suportados
ORACLE = "oracle"
SQLITE = "sqlite"


def _oracle_url() -> str:
    """Monta a URL SQLAlchemy do dialect oracle+oracledb (modo thin)."""
    host_port, _, service = ORACLE_DSN.partition("/")
    host, _, port = host_port.partition(":")
    port = port or "1521"
    return (
        f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}"
        f"@{host}:{port}/?service_name={service}"
    )


def _try_oracle() -> Engine | None:
    """Tenta abrir engine Oracle. Devolve None se sem credencial ou falha."""
    if not ORACLE_USER or not ORACLE_PASSWORD:
        return None
    try:
        engine = create_engine(_oracle_url())
        # Forca uma conexao real para validar credencial/rede antes de usar.
        with engine.connect():
            pass
        return engine
    except Exception as exc:                      # noqa: BLE001
        print(f"[db] Oracle indisponivel ({exc.__class__.__name__}: {exc}). "
              f"Usando SQLite local.")
        return None


def sqlite_engine() -> Engine:
    """Engine do SQLite local (sempre disponivel)."""
    return create_engine(f"sqlite:///{DB_PATH}")


def oracle_engine() -> Engine | None:
    """Engine do Oracle FIAP, ou None se sem credencial / conexao falha."""
    return _try_oracle()


def get_engine() -> tuple[Engine, str]:
    """
    Resolve o backend ativo para LEITURA (dashboard, ML).

    Returns:
        (engine, backend) onde backend e "oracle" ou "sqlite".
    Oracle tem prioridade quando ha credencial valida no .env; caso contrario
    cai para o SQLite local (farmtech.db).
    """
    engine = _try_oracle()
    if engine is not None:
        return engine, ORACLE
    return sqlite_engine(), SQLITE


def schema_path(backend: str) -> Path:
    """DDL correto por backend (Oracle vs SQLite)."""
    if backend == ORACLE:
        return SQL_DIR / "oracle" / "01_schema_oracle.sql"
    return SQL_DIR / "01_schema.sql"


def oracle_create_statements() -> list[str]:
    """
    CREATE TABLE/INDEX do DDL Oracle, prontos para executar um a um.

    O driver (oracledb) nao entende o terminador '/' nem multiplos statements
    numa chamada. Esta funcao descarta o bloco PL/SQL de DROP (que termina em
    '/') e devolve cada CREATE isolado. O DROP idempotente fica a cargo do
    chamador (ver load_to_sql.criar_schema_oracle), que ignora ORA-00942.
    """
    texto = schema_path(ORACLE).read_text(encoding="utf-8")
    # Tudo apos o primeiro terminador '/' = somente os CREATEs.
    _, _, creates = texto.partition("\n/")
    statements = []
    for bruto in creates.split(";"):
        linhas = [l for l in bruto.splitlines()
                  if l.strip() and not l.strip().startswith("--")]
        if linhas:
            statements.append("\n".join(linhas).strip())
    return statements


# Tabelas na ordem de DROP (filhas primeiro, respeitando as FKs).
ORACLE_TABLES = ("acoes_irrigacao", "leituras_sensor", "culturas")


def coerce_datetimes(df: pd.DataFrame, backend: str) -> pd.DataFrame:
    """
    Ajusta colunas datetime ao backend de destino antes de um to_sql.

    - SQLite: converte para string ISO. O sqlite3 do Python 3.12+ removeu o
      adapter default de datetime, entao Timestamps quebrariam o INSERT.
    - Oracle: converte para datetime.datetime nativo (DATE/TIMESTAMP); strings
      causariam ORA-01861 (literal does not match format string).
    """
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            if backend == SQLITE:
                out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                out[col] = out[col].dt.to_pydatetime()
    return out


def backend_of(engine: Engine) -> str:
    """Mapeia o dialect SQLAlchemy para a constante de backend."""
    return ORACLE if engine.dialect.name == "oracle" else SQLITE


def read_sql(query: str, engine: Engine, **kwargs) -> pd.DataFrame:
    """
    Wrapper de pd.read_sql que normaliza nomes de coluna para minusculo.

    O Oracle devolve identificadores nao-aspeados em MAIUSCULO, o que quebraria
    o codigo downstream (que espera 'temperatura', 'cultura', etc.). Padroniza
    para minusculo nos dois backends, mantendo o restante do pipeline identico.
    """
    df = pd.read_sql(query, engine, **kwargs)
    df.columns = [c.lower() for c in df.columns]
    return df
