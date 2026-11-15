# TCC — Benchmark de modelos de embedding para busca em e-commerce

Compara BM25, KNN (embeddings) e busca híbrida (RRF) no Amazon Shopping Queries Dataset (ESCI, locale US),
usando nDCG@k (k = 5, 10, 20, 45) com os ganhos ESCI: E=1.0, S=0.1, C=0.01, I=0.0.

Modelos (`src/models/models.json`): BERT, RoBERTa, BERTimbau, ModernBERT, BGE e RexBERT.

## Pipeline

Os notebooks rodam em sequência e foram feitos para o Google Colab.

| Notebook | Função | Entrada | Saída |
|---|---|---|---|
| `01_prepare_data.ipynb` | Filtra locale, amostra 200 mil produtos, EDA | `data/raw/*.parquet` | `data/processed/products_us.parquet`, `examples_us.parquet` |
| `02_indexing.ipynb` | Sobe o Elasticsearch, indexa BM25 e um índice por modelo, valida | `data/processed/products_us.parquet` | Índices `esci-<modelo>-us` |
| `03_evaluation.ipynb` | Calcula nDCG@k e latência, analisa os resultados | `examples_us.parquet` + índices | `results/elasticsearch/*.json` |
| `02_03_index_and_evaluate.ipynb` | Junta os notebooks 02 e 03 em uma única sessão (recomendado no Colab) | `data/processed/*.parquet` | Índices + `results/elasticsearch/*.json` |
| `04_results_analysis.ipynb` | Tabelas (CSV, Markdown, LaTeX), gráficos, hipóteses | `results/elasticsearch/all_results.json` | `results/report/` |

O notebook 01 baixa os dados do [repositório oficial do ESCI](https://github.com/amazon-science/esci-data/tree/main/shopping_queries_dataset)
para `data/raw/` (`DOWNLOAD_DATA = True`): `shopping_queries_dataset_products.parquet` (~1,1 GB),
`shopping_queries_dataset_examples.parquet` (~50 MB) e `shopping_queries_dataset_sources.csv`.
Arquivos já baixados são pulados. Os parquets ficam no Git LFS, então o download usa
`media.githubusercontent.com` (`src/download.py`). Para usar arquivos próprios, copie-os para `data/raw/`
e defina `DOWNLOAD_DATA = False`.

## Google Colab

1. Copie o projeto para o Google Drive em `MyDrive/tcc` (ou altere `DRIVE_PROJECT_DIR` na primeira célula).
2. Abra o notebook no Colab. A primeira célula monta o Drive e instala as dependências.
3. Execute os notebooks 02 e 03 **na mesma sessão**: o Elasticsearch iniciado no notebook 02 roda na VM e
   seus índices são perdidos quando a sessão termina.

## CPU ou GPU

Altere apenas `DEVICE` na primeira célula de cada notebook:

```python
DEVICE = "auto"   # "cpu" | "cuda" | "auto"
```

- Os embeddings (PyTorch) usam o dispositivo escolhido, com `batch_size` e `max_seq_length` padrão por dispositivo
  (`src/device.py`).
- O Polars usa o motor GPU (cudf-polars) quando `DEVICE` resolve para `cuda` e o pacote está instalado. Sem ele,
  a execução volta para a CPU com um aviso.
- Se `cuda` for pedido sem GPU disponível, o código usa CPU.

## Elasticsearch

- No Colab, o notebook 02 baixa e inicia o Elasticsearch 8.15 com segurança desativada (acesso só dentro da VM).
- Fora do Colab, suba um servidor por conta própria e ajuste `ES_URL`, `ES_USER` e a variável de ambiente
  `ES_PASSWORD` nos notebooks 02 e 03.
- A busca híbrida usa o retriever RRF, que exige licença paga. O notebook 02 ativa a licença trial de 30 dias.
  Sem ela, a estratégia `hybrid` falha e o notebook 03 a ignora.

## Estrutura

```
01_prepare_data.ipynb ... 04_results_analysis.ipynb
data/raw/            dataset original (não versionado)
data/processed/      parquets filtrados
results/             métricas (elasticsearch/) e relatório (report/)
requirements/        dependências
src/device.py        seleção CPU/GPU
src/models/          registro (registry.py, models.json) e carregamento (core.py)
src/elasticsearch/   mappings, indexer e searcher
```

## Execução local

Requer Python 3.13. Instale `requirements/requirements-core.txt` e abra os notebooks a partir da raiz do
projeto (o notebook usa o diretório atual como raiz).
