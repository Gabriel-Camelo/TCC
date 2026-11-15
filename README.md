# TCC — Benchmark de modelos de embedding para busca em e-commerce

Compara BM25, KNN (embeddings) e busca híbrida (RRF) no Amazon Shopping Queries Dataset (ESCI, locale US),
usando nDCG@k (k = 5, 10, 20, 45) com os ganhos ESCI: E=1.0, S=0.1, C=0.01, I=0.0.

Modelos (`src/models/models.json`): BERT, RoBERTa, ModernBERT, BGE-M3 e RexBERT.

## Pipeline

O fluxo tem duas partes: a geração de embeddings (cara, usa GPU) roda no Google Colab, e todo o resto roda na
máquina local com o Elasticsearch em Docker.

| Etapa | Onde | O que faz | Entrada | Saída |
|---|---|---|---|---|
| `01_prepare_data.ipynb` | Colab ou local | Baixa o ESCI, filtra o locale, amostra 200 mil produtos, EDA | (download) | `data/processed/*.parquet` |
| `02_generate_embeddings.ipynb` | **Colab (GPU)** | Gera os embeddings de cada modelo (float32) | `data/processed/products_us.parquet` | `data/embeddings/<modelo>.parquet` + `.meta.json` |
| `scripts/index_embeddings.py` | **Local** | Indexa BM25 e um índice KNN por modelo no Elasticsearch, sem carregar modelos | produtos + embeddings | Índices `esci-<modelo>-us` |
| `02b_validate_indexing.ipynb` | Local | Confere contagens, normas e buscas manuais | Índices | — |
| `03_evaluation.ipynb` | Local | Calcula nDCG@k e latência, analisa os resultados | `examples_us.parquet` + índices | `results/elasticsearch/*.json` |
| `04_results_analysis.ipynb` | Local | Tabelas (CSV, Markdown, LaTeX), gráficos, hipóteses | `results/elasticsearch/all_results.json` | `results/report/` |

## Dados

O notebook 01 baixa os dados do [repositório oficial do ESCI](https://github.com/amazon-science/esci-data/tree/main/shopping_queries_dataset)
para `data/raw/` (`DOWNLOAD_DATA = True`): `shopping_queries_dataset_products.parquet` (~1,1 GB),
`shopping_queries_dataset_examples.parquet` (~50 MB) e `shopping_queries_dataset_sources.csv`.
Arquivos já baixados são pulados. Os parquets ficam no Git LFS, então o download usa
`media.githubusercontent.com` (`src/download.py`). Para usar arquivos próprios, copie-os para `data/raw/`
e defina `DOWNLOAD_DATA = False`.

## Geração de embeddings (Colab)

1. Copie o projeto para o Google Drive em `MyDrive/tcc` (ou altere `DRIVE_PROJECT_DIR` na primeira célula).
2. Execute `01_prepare_data.ipynb` (se ainda não tiver `data/processed/`) e depois `02_generate_embeddings.ipynb`.
3. Copie `data/embeddings/` do Drive para a mesma pasta do projeto local.

Cada modelo gera `<modelo>.parquet` (`product_id`, `embedding` em float32) e `<modelo>.meta.json` (modelo,
dimensão, `max_seq_length` efetivo, texto usado, data). Modelos já gerados e compatíveis são pulados, então uma
sessão interrompida pode ser retomada. A geração falha se a dimensão dos vetores diferir de `embedding_dim`
em `models.json`.

## Indexação (local)

Suba o Elasticsearch no Docker e execute, a partir da raiz do projeto:

```powershell
$env:ES_PASSWORD = "sua_senha"            # se o cluster tiver autenticação
python scripts/index_embeddings.py --es-url https://localhost:9200 --insecure
```

Opções úteis: `--models bge rexbert`, `--skip-bm25`, `--overwrite`. Sem `--models`, indexa todos os modelos que
têm embeddings gerados. O script recusa arquivos de embeddings incompatíveis com o `models.json` (modelo,
dimensão, normalização, texto ou número de produtos diferentes). Ele não importa `torch` nem baixa modelos.

A busca híbrida usa o retriever RRF, que exige licença paga. O notebook 02b ativa a licença trial de 30 dias.
Sem ela, a estratégia `hybrid` falha e o notebook 03 a ignora.

## Avaliação (local)

`03_evaluation.ipynb` conecta ao Elasticsearch por `ES_URL`, `ES_USER` e `ES_PASSWORD` (variáveis de ambiente).
A busca KNN codifica cada query com o mesmo modelo usado na indexação, então esse notebook baixa e carrega os
modelos na máquina local. Altere `DEVICE` (`"cpu"`, `"cuda"` ou `"auto"`) na primeira célula; sem GPU,
o processo usa CPU.

## CPU ou GPU

```python
DEVICE = "auto"   # "cpu" | "cuda" | "auto"
```

- Os embeddings (PyTorch) usam o dispositivo escolhido, com `batch_size` e `max_seq_length` padrão por dispositivo
  (`src/device.py`).
- O Polars usa o motor GPU (cudf-polars) quando `DEVICE` resolve para `cuda` e o pacote está instalado. Sem ele,
  a execução volta para a CPU com um aviso.
- Se `cuda` for pedido sem GPU disponível, o código usa CPU.

## Estrutura

```
01_prepare_data.ipynb, 02_generate_embeddings.ipynb, 02b_validate_indexing.ipynb,
03_evaluation.ipynb, 04_results_analysis.ipynb
scripts/index_embeddings.py   indexação local a partir dos embeddings
data/raw/                     dataset original (não versionado)
data/processed/               parquets filtrados
data/embeddings/              embeddings por modelo (não versionado)
results/                      métricas (elasticsearch/) e relatório (report/)
requirements/                 dependências
src/device.py                 seleção CPU/GPU
src/download.py               download do ESCI
src/text.py                   texto do produto usado nos embeddings e na indexação
src/embeddings.py             geração e leitura de embeddings
src/models/                   registro (registry.py, models.json) e carregamento (core.py)
src/elasticsearch/            mappings, indexer e searcher
```

## Execução local

Requer Python 3.13. Instale `requirements/requirements-core.txt` e abra os notebooks a partir da raiz do
projeto (o notebook usa o diretório atual como raiz).
