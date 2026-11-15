"""
indexer.py
----------
Responsável por criar índices e indexar produtos no Elasticsearch.

Fluxo principal:
  1. Criar o índice com o mapping correto (embedding ou BM25)
  2. Iterar sobre os produtos em batches
  3. Gerar embeddings para cada batch (somente para índices KNN)
  4. Enviar documentos via bulk API
  5. Restaurar refresh_interval e forçar merge ao final

Uso típico
----------
    from elasticsearch import Elasticsearch
    from src.elasticsearch.indexer import Indexer

    es = Elasticsearch("http://localhost:9200")
    indexer = Indexer(es, device="cuda")

    # Indexar com embeddings de um modelo
    indexer.index_model("bge", products_df)

    # Indexar índice BM25 puro
    indexer.index_bm25(products_df)
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
import logging
from typing import Any, Protocol
import warnings

import numpy as np
import polars as pl
from elasticsearch import Elasticsearch
from elasticsearch.helpers import BulkIndexError, bulk
from tqdm import tqdm

from src.elasticsearch.mappings import (
    build_bm25_mapping,
    build_embedding_mapping,
    restore_refresh_interval,
)
from src.models.registry import (
    BM25_INDEX_NAME,
    ModelConfig,
    get_model_config,
    list_models,
)
from src.text import EMBEDDING_FIELDS as _EMBEDDING_FIELDS
from src.text import FIELD_SEPARATOR as _FIELD_SEPARATOR
from src.text import FrameLike, prepare_dataframe

# torch e src.models.core (que carrega sentence-transformers) são importados apenas em
# `index_model`, para que `index_from_embeddings` rode sem essas dependências.

logger = logging.getLogger(__name__)

# Type alias nativo do Python 3.12+ (PEP 695)
type ESDocument = dict[str, Any]


class EmbeddingModel(Protocol):
    """Contrato estrutural esperado para modelos de embedding."""

    max_seq_length: int

    def encode(
        self,
        sentences: list[str],
        *,
        batch_size: int = ...,
        normalize_embeddings: bool = ...,
        show_progress_bar: bool = ...,
        convert_to_numpy: bool = ...,
    ) -> np.ndarray: ...


# ---------------------------------------------------------------------------
# Configuração de campos
# ---------------------------------------------------------------------------

_BASE_DOC_FIELDS: tuple[str, ...] = (
    "product_id",
    "product_title",
    "product_text",
    "product_locale",
)


# ---------------------------------------------------------------------------
# Helpers de texto e preparação de dados
# ---------------------------------------------------------------------------


def build_product_text(row: dict[str, Any]) -> str:
    """
    Concatena os campos textuais de um produto em uma única string.

    .. deprecated::
        Use `prepare_dataframe()` para construção vetorizada via Polars.
    """
    warnings.warn(
        "build_product_text() está obsoleta; use prepare_dataframe().",
        DeprecationWarning,
        stacklevel=2,
    )
    parts = [
        val.strip()
        for field in _EMBEDDING_FIELDS
        if isinstance((val := row.get(field)), str) and val.strip()
    ]
    return _FIELD_SEPARATOR.join(parts)


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------


class Indexer:
    """
    Gerencia a criação de índices e a indexação de produtos no Elasticsearch.

    Parameters
    ----------
    es:
        Instância conectada do cliente Elasticsearch.
    device:
        Dispositivo PyTorch para inferência: "cpu", "cuda", "cuda:0", etc.
    batch_size:
        Número de documentos processados por vez na geração de embeddings.
    bulk_chunk_size:
        Número de documentos enviados por chamada à bulk API.
    overwrite:
        Se True, apaga o índice existente antes de recriar.
    """

    def __init__(
        self,
        es: Elasticsearch,
        device: str = "cpu",
        batch_size: int = 128,
        bulk_chunk_size: int = 256,
        overwrite: bool = False,
    ) -> None:
        self.es = es
        self.device = device
        self.batch_size = batch_size
        self.bulk_chunk_size = bulk_chunk_size
        self.overwrite = overwrite

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def index_model(
        self,
        alias: str,
        products_df: FrameLike,
        max_seq_length_override: int | None = None,
    ) -> None:
        """
        Cria o índice e indexa todos os produtos US com embeddings do modelo.
        """
        import torch

        from src.models.core import load_model, unload_model

        config = get_model_config(alias)
        df = self._ensure_prepared(products_df)
        total_docs = df.height

        if self._should_skip_indexing(config.es_index_name, total_docs):
            return

        logger.info(
            "Iniciando indexação — modelo: %s | índice: %s | docs: %d",
            alias,
            config.es_index_name,
            total_docs,
        )

        self._prepare_index(config.es_index_name, build_embedding_mapping(config))

        model: EmbeddingModel = load_model(
            alias, device=self.device, max_seq_length_override=max_seq_length_override
        )

        try:
            n_batches = (total_docs + self.batch_size - 1) // self.batch_size
            logger.info(
                "Gerando embeddings: %d docs em %d batches de %d (max_seq_length=%d, device=%s, threads=%d)",
                total_docs,
                n_batches,
                self.batch_size,
                model.max_seq_length,
                self.device,
                torch.get_num_threads(),
            )

            self._bulk_index(
                doc_generator=self._embedding_doc_generator(df, config, model),
            )

            self._finalize_index(config.es_index_name)
            logger.info("Indexação concluída — %s", config.es_index_name)
        finally:
            # Garante liberação da VRAM/RAM mesmo se ocorrer erro no meio do processo
            unload_model(alias, device=self.device)
            logger.debug("Modelo %s liberado da memória.", alias)

    def index_from_embeddings(
        self,
        alias: str,
        products_df: FrameLike,
        embeddings_df: pl.DataFrame,
    ) -> None:
        """
        Cria o índice e indexa os produtos US usando embeddings já calculados
        (colunas `product_id` e `embedding`), sem carregar nenhum modelo.

        Raises
        ------
        ValueError
            Se algum produto não tiver embedding correspondente.
        """
        config = get_model_config(alias)
        df = self._ensure_prepared(products_df)
        total_docs = df.height

        if self._should_skip_indexing(config.es_index_name, total_docs):
            return

        joined = df.join(embeddings_df.select("product_id", "embedding"), on="product_id", how="left")
        missing = joined["embedding"].null_count()
        if missing:
            raise ValueError(f"{missing} produtos sem embedding para o modelo '{alias}'. Gere os embeddings novamente.")

        logger.info(
            "Iniciando indexação — modelo: %s | índice: %s | docs: %d (embeddings pré-calculados)",
            alias,
            config.es_index_name,
            total_docs,
        )
        self._prepare_index(config.es_index_name, build_embedding_mapping(config))
        self._bulk_index(doc_generator=self._precomputed_doc_generator(joined, config))
        self._finalize_index(config.es_index_name)
        logger.info("Indexação concluída — %s", config.es_index_name)

    def index_bm25(self, products_df: FrameLike) -> None:
        """
        Cria o índice BM25 puro e indexa todos os produtos US (sem embeddings).
        """
        df = self._ensure_prepared(products_df)
        total_docs = df.height

        if self._should_skip_indexing(BM25_INDEX_NAME, total_docs):
            return

        logger.info(
            "Iniciando indexação BM25 | índice: %s | docs: %d",
            BM25_INDEX_NAME,
            total_docs,
        )

        self._prepare_index(BM25_INDEX_NAME, build_bm25_mapping())
        self._bulk_index(
            doc_generator=self._bm25_doc_generator(df),
        )

        self._finalize_index(BM25_INDEX_NAME)
        logger.info("Indexação BM25 concluída — %s", BM25_INDEX_NAME)

    def index_all_models(
        self,
        products_df: FrameLike,
        aliases: Sequence[str] | None = None,
    ) -> None:
        """
        Indexa todos os modelos registrados (ou apenas os da sequência `aliases`).
        """
        df = self._ensure_prepared(products_df)
        targets = aliases or [cfg.alias for cfg in list_models()]
        for alias in targets:
            self.index_model(alias, df)

    # ------------------------------------------------------------------
    # Generators de documentos
    # ------------------------------------------------------------------

    def _embedding_doc_generator(
        self,
        df: pl.DataFrame,
        config: ModelConfig,
        model: EmbeddingModel,
    ) -> Iterator[ESDocument]:
        """
        Gera documentos com embedding para a bulk API usando slices nativos do Polars.
        """
        needed_cols = [c for c in _BASE_DOC_FIELDS if c in df.columns]
        sliced_df = df.select(needed_cols)

        with tqdm(
            total=df.height,
            desc=f"Indexando {config.es_index_name}",
            unit="doc",
        ) as pbar:
            for batch_df in sliced_df.iter_slices(n_rows=self.batch_size):
                batch_texts = batch_df["product_text"].to_list()

                embeddings = model.encode(
                    batch_texts,
                    batch_size=self.batch_size,
                    normalize_embeddings=config.normalize_embeddings,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                )

                # .tolist() no ndarray 2D inteiro em C é muito mais rápido
                # do que chamar embeddings[i].tolist() dentro do loop Python
                embeddings_list: list[list[float]] = embeddings.tolist()

                for row, emb in zip(
                    batch_df.iter_rows(named=True), embeddings_list, strict=True
                ):
                    yield {
                        "_index": config.es_index_name,
                        "_id": row["product_id"],
                        "_source": {
                            **self._base_doc(row),
                            "embedding": emb,
                        },
                    }
                pbar.update(batch_df.height)

    def _precomputed_doc_generator(self, df: pl.DataFrame, config: ModelConfig) -> Iterator[ESDocument]:
        """
        Gera documentos para a bulk API a partir de um DataFrame que já contém a coluna `embedding`.
        """
        needed_cols = [c for c in _BASE_DOC_FIELDS if c in df.columns] + ["embedding"]
        sliced_df = df.select(needed_cols)

        with tqdm(total=df.height, desc=f"Indexando {config.es_index_name}", unit="doc") as pbar:
            for batch_df in sliced_df.iter_slices(n_rows=self.batch_size):
                for row in batch_df.iter_rows(named=True):
                    embedding = row.pop("embedding")
                    yield {
                        "_index": config.es_index_name,
                        "_id": row["product_id"],
                        "_source": {**self._base_doc(row), "embedding": embedding},
                    }
                pbar.update(batch_df.height)

    def _bm25_doc_generator(self, df: pl.DataFrame) -> Iterator[ESDocument]:
        """
        Gera documentos sem embedding para o índice BM25 sem materializar batches inteiros.
        """
        needed_cols = [c for c in _BASE_DOC_FIELDS if c in df.columns]
        sliced_df = df.select(needed_cols)

        with tqdm(
            total=df.height,
            desc=f"Indexando {BM25_INDEX_NAME}",
            unit="doc",
        ) as pbar:
            for batch_df in sliced_df.iter_slices(n_rows=self.batch_size):
                for row in batch_df.iter_rows(named=True):
                    yield {
                        "_index": BM25_INDEX_NAME,
                        "_id": row["product_id"],
                        "_source": self._base_doc(row),
                    }
                pbar.update(batch_df.height)

    @staticmethod
    def _base_doc(row: dict[str, Any]) -> ESDocument:
        """
        Constrói o documento base enviado ao ES.
        """
        return {
            field: (
                row.get(field, "us")
                if field == "product_locale"
                else (row.get(field) or "")
            )
            for field in _BASE_DOC_FIELDS
        }

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_prepared(products_df: FrameLike) -> pl.DataFrame:
        if (
            isinstance(products_df, pl.DataFrame)
            and "product_text" in products_df.columns
        ):
            return products_df
        return prepare_dataframe(products_df)

    def _should_skip_indexing(self, index_name: str, expected_docs: int) -> bool:
        """Verifica se o índice já existe com a contagem exata de documentos."""
        if self.overwrite or not self.es.indices.exists(index=index_name):
            return False

        try:
            existing_count: int = self.es.count(index=index_name)["count"]
        except Exception as exc:
            logger.debug(
                "Falha ao verificar contagem do índice %s: %s", index_name, exc
            )
            return False

        if existing_count == expected_docs:
            logger.info(
                "Índice %s já tem %d docs — pulando indexação.",
                index_name,
                existing_count,
            )
            return True

        logger.info(
            "Índice %s tem %d docs (esperado %d) — reindexando.",
            index_name,
            existing_count,
            expected_docs,
        )
        return False

    def _prepare_index(self, index_name: str, mapping: dict[str, Any]) -> None:
        """Cria o índice; apaga se já existir e overwrite=True."""
        if self.es.indices.exists(index=index_name):
            if self.overwrite:
                logger.warning("Apagando índice existente: %s", index_name)
                self.es.indices.delete(index=index_name)
            else:
                logger.info(
                    "Índice já existe e overwrite=False, pulando criação: %s",
                    index_name,
                )
                return

        self.es.indices.create(
            index=index_name,
            mappings=mapping.get("mappings"),
            settings=mapping.get("settings"),
        )
        logger.debug("Índice criado: %s", index_name)

    def _bulk_index(self, doc_generator: Iterator[ESDocument]) -> None:
        """Executa a indexação bulk."""
        try:
            success, errors = bulk(
                self.es,
                doc_generator,
                chunk_size=self.bulk_chunk_size,
                raise_on_error=False,
                stats_only=False,
            )
        except BulkIndexError as exc:
            logger.error("BulkIndexError: %d erros", len(exc.errors))
            success, errors = 0, exc.errors

        logger.info("Bulk finalizado — sucesso: %d | erros: %d", success, len(errors))
        if errors:
            logger.warning("Primeiros 5 erros: %s", errors[:5])

    def _finalize_index(self, index_name: str) -> None:
        """Restaura o refresh_interval e força um merge para otimizar a busca."""
        self.es.indices.put_settings(
            index=index_name,
            settings=restore_refresh_interval().get(
                "settings", restore_refresh_interval()
            ),
        )
        self.es.indices.refresh(index=index_name)
        self.es.indices.forcemerge(
            index=index_name, max_num_segments=1, wait_for_completion=False
        )
        logger.debug(
            "Índice finalizado (refresh + forcemerge agendado): %s", index_name
        )
