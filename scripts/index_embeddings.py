"""
index_embeddings.py
-------------------
Indexa os produtos no Elasticsearch usando embeddings já gerados (notebook 02_generate_embeddings),
sem carregar nenhum modelo. Cria um índice BM25 e um índice KNN por modelo.

Entradas:
  data/processed/products_us.parquet   catálogo (notebook 01)
  data/embeddings/<alias>.parquet      embeddings + <alias>.meta.json (notebook 02)

Uso:
  python scripts/index_embeddings.py
  python scripts/index_embeddings.py --models bge rexbert
  python scripts/index_embeddings.py --overwrite --es-url https://localhost:9200 --insecure

Autenticação: defina a variável de ambiente ES_PASSWORD (usuário padrão: elastic).
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

import polars as pl
from elasticsearch import Elasticsearch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.elasticsearch.indexer import Indexer  # noqa: E402
from src.embeddings import check_compatibility, is_complete, read_embeddings  # noqa: E402
from src.models.registry import get_model_config, list_models  # noqa: E402
from src.text import prepare_dataframe  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("elastic_transport").setLevel(logging.WARNING)
logger = logging.getLogger("index_embeddings")

DEFAULT_PRODUCTS = PROJECT_ROOT / "data" / "processed" / "products_us.parquet"
DEFAULT_EMBEDDINGS_DIR = PROJECT_ROOT / "data" / "embeddings"
DEFAULT_ES_URL = [{"host": "localhost", "port": 9200, "scheme": "http"}]


def parse_args() -> argparse.Namespace:
    aliases = [cfg.alias for cfg in list_models()]
    parser = argparse.ArgumentParser(
        description="Indexa produtos no Elasticsearch a partir de embeddings pré-calculados."
    )
    parser.add_argument(
        "--products",
        type=Path,
        default=DEFAULT_PRODUCTS,
        help="Parquet de produtos (padrão: %(default)s)",
    )
    parser.add_argument(
        "--embeddings-dir",
        type=Path,
        default=DEFAULT_EMBEDDINGS_DIR,
        help="Diretório dos embeddings (padrão: %(default)s)",
    )
    parser.add_argument(
        "--es-url",
        default=DEFAULT_ES_URL,
        help="URL do Elasticsearch (padrão: %(default)s)",
    )
    parser.add_argument(
        "--user", default="elastic", help="Usuário (a senha vem de ES_PASSWORD)"
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Não verifica o certificado TLS (certificado autoassinado do Docker)",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=aliases,
        default=None,
        help="Modelos a indexar (padrão: todos com embeddings gerados)",
    )
    parser.add_argument(
        "--skip-bm25", action="store_true", help="Não cria o índice BM25"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Apaga e recria índices existentes"
    )
    parser.add_argument(
        "--bulk-chunk-size",
        type=int,
        default=500,
        help="Documentos por chamada à bulk API (padrão: %(default)s)",
    )
    return parser.parse_args()


def connect(args: argparse.Namespace) -> Elasticsearch:
    password = os.environ.get("ES_PASSWORD", "meutcc")
    kwargs: dict = {"request_timeout": 120, "retry_on_timeout": True, "max_retries": 3}
    if password:
        kwargs["basic_auth"] = (args.user, password)
    if args.insecure:
        kwargs["verify_certs"] = False
    es = Elasticsearch(args.es_url, **kwargs)
    try:
        version = es.info()["version"]["number"]
    except Exception as exc:
        logger.error("Falha ao conectar em %s: %s", args.es_url, exc)
        sys.exit(1)
    logger.info("Elasticsearch %s conectado em %s", version, args.es_url)
    return es


def format_elapsed(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return (
        f"{hours:02d}h{minutes:02d}m{secs:02d}s"
        if hours
        else f"{minutes:02d}m{secs:02d}s"
    )


def main() -> None:
    args = parse_args()

    if not args.products.exists():
        logger.error("Arquivo de produtos não encontrado: %s", args.products)
        sys.exit(1)

    if args.models:
        targets = args.models
    else:
        targets = [
            cfg.alias
            for cfg in list_models()
            if is_complete(args.embeddings_dir, cfg.alias)
        ]
        if not targets:
            logger.error(
                "Nenhum embedding encontrado em %s. Execute o notebook 02_generate_embeddings.",
                args.embeddings_dir,
            )
            sys.exit(1)
    logger.info("Modelos a indexar: %s", targets)

    es = connect(args)
    prepared = prepare_dataframe(pl.read_parquet(args.products))
    logger.info("Catálogo: %d produtos", prepared.height)

    indexer = Indexer(
        es=es,
        batch_size=1000,
        bulk_chunk_size=args.bulk_chunk_size,
        overwrite=args.overwrite,
    )
    summary: list[tuple[str, str, str]] = []
    total_start = time.perf_counter()

    if not args.skip_bm25:
        started = time.perf_counter()
        try:
            indexer.index_bm25(prepared)
            summary.append(
                ("bm25", "ok", format_elapsed(time.perf_counter() - started))
            )
        except Exception as exc:
            logger.error("Falha no BM25: %s", exc, exc_info=True)
            summary.append(
                ("bm25", f"erro: {exc}", format_elapsed(time.perf_counter() - started))
            )

    for alias in targets:
        started = time.perf_counter()
        try:
            embeddings_df, meta = read_embeddings(alias, args.embeddings_dir)
            problems = check_compatibility(
                meta, get_model_config(alias), n_docs=prepared.height
            )
            if problems:
                raise ValueError(
                    "embeddings incompatíveis: "
                    + "; ".join(problems)
                    + ". Gere-os novamente."
                )
            logger.info(
                "%s: max_seq_length usado na geração = %d", alias, meta.max_seq_length
            )
            indexer.index_from_embeddings(alias, prepared, embeddings_df)
            status = "ok"
        except Exception as exc:
            logger.error("Falha ao indexar %s: %s", alias, exc)
            status = f"erro: {exc}"
        summary.append((alias, status, format_elapsed(time.perf_counter() - started)))

    logger.info(
        "=== Resumo (tempo total %s) ===",
        format_elapsed(time.perf_counter() - total_start),
    )
    for name, status, elapsed in summary:
        logger.info("  %-12s %-8s %s", name, elapsed, status)

    if any(status != "ok" for _, status, _ in summary):
        sys.exit(1)


if __name__ == "__main__":
    main()
