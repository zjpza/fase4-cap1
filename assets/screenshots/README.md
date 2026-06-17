# Screenshots — evidências

Prints organizados por etapa do projeto. Cada imagem é referenciada na documentação
correspondente — **mantenha os nomes abaixo** para os links não quebrarem.

## `oracle/` — banco Oracle FIAP (entrega obrigatória) → `docs/oracle_import.md`
| Arquivo                      | Conteúdo                                              |
| ---------------------------- | ----------------------------------------------------- |
| `01_conexao.png`             | Conexão no SQL Developer testada com sucesso.         |
| `02_schema.png`              | `01_schema_oracle.sql` executado; tabelas criadas.    |
| `03_carga.png`               | Carga concluída (COUNT por tabela).                   |
| `04_query_correlacao.png`    | Q3 — correlações variável × produtividade.            |
| `05_query_produtividade.png` | Q2 — ranking de produtividade por cultura.            |
| `06_query_outliers.png`      | Q5 — outliers de produtividade (IQR).                 |

## `wokwi/` — coleta ESP32 → `docs/esp32.md`
| Arquivo               | Conteúdo                                        |
| --------------------- | ----------------------------------------------- |
| `01_circuito.png`     | Circuito montado no simulador Wokwi.            |
| `02_serial_monitor.png` | Serial Monitor com as leituras dos sensores.  |

## `dashboard/` — Streamlit
| Arquivo               | Conteúdo                                            |
| --------------------- | --------------------------------------------------- |
| `01_resumo.png`       | Aba Resumo (indicadores + badge da fonte de dados). |
| `02_correlacoes.png`  | Aba Correlações (mapa de calor / dispersão).        |
| `03_predicoes.png`    | Aba Predições (entrada + produtividade prevista).   |

## `ml/` — Machine Learning
| Arquivo               | Conteúdo                                       |
| --------------------- | ---------------------------------------------- |
| `01_metricas.png`     | Métricas do modelo (MAE, RMSE, R²).            |
