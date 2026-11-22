"""
searcher.py
-----------
Executa buscas no Elasticsearch e retorna resultados padronizados.

Estratégias suportadas:
  - BM25     : busca lexical via multi_match nos campos de texto
  - KNN      : busca por vizinhança aproximada via dense_vector (HNSW)
  - Hybrid   : combinação de BM25 + KNN via Reciprocal Rank Fusion (RRF)
               requer Elasticsearch >= 8.9

Uso típico
----------
    from elasticsearch import Elasticsearch
    from src.elasticsearch.searcher import Searcher, SearchStrategy

    es = Elasticsearch("http://localhost:9200")
    searcher = Searcher(es, device="cuda")

    hits = searcher.search("bge", "wireless headphones", strategy=SearchStrategy.KNN, k=10)
    for hit in hits:
        print(hit.product_id, hit.score)
"""

from __future__ import annotations

import logging

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Final, Protocol

from elasticsearch import Elasticsearch
import numpy as np

from src.models.core import load_model, unload_model as _unload_model
from src.models.registry import BM25_INDEX_NAME, get_model_config

logger = logging.getLogger(__name__)

# Type aliases nativos do Python 3.12+ (PEP 695)
type RawHit = dict[str, Any]
type QueryPayload = dict[str, Any]


class QueryEncoder(Protocol):
    """Contrato estrutural esperado para modelos de encoding de queries."""

    def encode(
        self,
        sentences: str,
        *,
        normalize_embeddings: bool = ...,
        convert_to_numpy: bool = ...,
    ) -> np.ndarray: ...


# ---------------------------------------------------------------------------
# Tipos públicos
# ---------------------------------------------------------------------------


class SearchStrategy(StrEnum):
    BM25 = "bm25"
    KNN = "knn"
    HYBRID = "hybrid"


@dataclass(frozen=True, slots=True)
class SearchHit:
    """Resultado normalizado e imutável de uma busca, independente da estratégia."""

    product_id: str
    score: float
    rank: int  # 1-indexed, posição no resultado retornado pelo ES
    product_title: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Campos usados na busca BM25 e retorno
# ---------------------------------------------------------------------------

_BM25_FIELDS: Final[list[str]] = [
    "product_title^3",  # título tem peso maior
    "product_text",  # fallback (mesmo conteúdo que product_title)
    # "product_bullet_point^2",
    # "product_brand^1.5",
    # "product_description",
]

_SOURCE_FIELDS: Final[list[str]] = ["product_id", "product_title"]


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------


class Searcher:
    """
    Executa buscas no Elasticsearch para as três estratégias do benchmark.

    Parameters
    ----------
    es:
        Instância conectada do cliente Elasticsearch.
    device:
        Dispositivo PyTorch para geração do query embedding: "cpu", "cuda", etc.
    num_candidates_multiplier:
        Fator aplicado sobre k para definir num_candidates no KNN aproximado.
        Valor padrão 10x é um bom trade-off entre recall e latência.
    rrf_rank_constant:
        Constante de suavização do RRF (padrão 60, conforme literatura).
    """

    def __init__(
        self,
        es: Elasticsearch,
        device: str = "cpu",
        num_candidates_multiplier: int = 10,
        rrf_rank_constant: int = 60,
    ) -> None:
        self.es = es
        self.device = device
        self.num_candidates_multiplier = num_candidates_multiplier
        self.rrf_rank_constant = rrf_rank_constant

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def search(
        self,
        alias: str,
        query_text: str,
        strategy: SearchStrategy = SearchStrategy.KNN,
        k: int = 45,
    ) -> list[SearchHit]:
        """
        Executa uma busca e retorna lista de SearchHit ordenada por rank.

        Parameters
        ----------
        alias:
            Alias do modelo (para KNN e Hybrid) ou "bm25" para busca lexical pura.
            Quando strategy=BM25, o alias é ignorado e usa-se BM25_INDEX_NAME.
        query_text:
            Texto da query do usuário.
        strategy:
            Estratégia de busca: BM25, KNN ou HYBRID.
        k:
            Número máximo de resultados a retornar.
        """
        match strategy:
            case SearchStrategy.BM25:
                raw_hits = self._search_bm25(BM25_INDEX_NAME, query_text, k)
            case SearchStrategy.KNN:
                raw_hits = self._search_knn(alias, query_text, k)
            case SearchStrategy.HYBRID:
                raw_hits = self._search_hybrid(alias, query_text, k)
            case _:
                raise ValueError(f"Estratégia desconhecida: {strategy}")

        return self._parse_hits(raw_hits)

    def search_all_strategies(
        self,
        alias: str,
        query_text: str,
        k: int = 45,
    ) -> dict[SearchStrategy, list[SearchHit]]:
        """
        Executa as três estratégias para a mesma query e retorna um dict.

        Útil nos notebooks de avaliação para comparar estratégias lado a lado.
        """
        return {
            strategy: self.search(alias, query_text, strategy=strategy, k=k)
            for strategy in SearchStrategy
        }

    def unload_model(self, alias: str) -> None:
        """
        Libera o modelo do cache, removendo-o da RAM.

        Chamar após terminar todas as buscas de um modelo (ex.: entre
        iterações do loop de avaliação) para evitar acúmulo de memória.
        """
        _unload_model(alias, device=self.device)

    # ------------------------------------------------------------------
    # Estratégias de busca
    # ------------------------------------------------------------------

    def _search_bm25(self, index_name: str, query_text: str, k: int) -> list[RawHit]:
        """Busca lexical via multi_match com boost por campo."""
        response = self.es.search(
            index=index_name,
            size=k,
            query=self._bm25_query_clause(query_text),
            source=_SOURCE_FIELDS,
        )
        return response["hits"]["hits"]

    def _search_knn(self, alias: str, query_text: str, k: int) -> list[RawHit]:
        """Busca densa via KNN aproximado (HNSW) no índice do modelo."""
        config = get_model_config(alias)
        query_vector = self._encode_query(alias, query_text)

        response = self.es.search(
            index=config.es_index_name,
            size=k,
            knn=self._knn_clause(query_vector, k),
            source=_SOURCE_FIELDS,
        )
        return response["hits"]["hits"]

    def _search_hybrid(self, alias: str, query_text: str, k: int) -> list[RawHit]:
        """
        Busca híbrida BM25 + KNN via Reciprocal Rank Fusion (RRF).

        Requer Elasticsearch >= 8.9.
        Combina os dois retrievers sem necessidade de normalização manual de scores.
        """
        config = get_model_config(alias)
        query_vector = self._encode_query(alias, query_text)

        response = self.es.search(
            index=config.es_index_name,
            size=k,
            retriever={
                "rrf": {
                    "retrievers": [
                        {"standard": {"query": self._bm25_query_clause(query_text)}},
                        {"knn": self._knn_clause(query_vector, k)},
                    ],
                    "rank_window_size": k,
                    "rank_constant": self.rrf_rank_constant,
                }
            },
            source=_SOURCE_FIELDS,
        )
        return response["hits"]["hits"]

    # ------------------------------------------------------------------
    # Construtores de cláusulas e helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _bm25_query_clause(query_text: str) -> QueryPayload:
        return {
            "multi_match": {
                "query": query_text,
                "fields": _BM25_FIELDS,
                "type": "most_fields",  # soma os scores dos campos (tie_breaker não se aplica)
            }
        }

    def _knn_clause(self, query_vector: list[float], k: int) -> QueryPayload:
        return {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": k * self.num_candidates_multiplier,
        }

    def _encode_query(self, alias: str, query_text: str) -> list[float]:
        """Gera o vetor da query usando o mesmo modelo e normalização da indexação."""
        config = get_model_config(alias)
        model: QueryEncoder = load_model(alias, device=self.device)
        text = f"{config.query_prompt}{query_text}" if config.query_prompt else query_text
        embedding = model.encode(
            text,
            normalize_embeddings=config.normalize_embeddings,
            convert_to_numpy=True,
        )
        return embedding.astype(np.float32, copy=False).tolist()

    @staticmethod
    def _parse_hits(raw_hits: list[RawHit]) -> list[SearchHit]:
        """Converte os hits brutos do ES para SearchHit normalizados."""
        return [
            SearchHit(
                product_id=(source := hit.get("_source", {})).get(
                    "product_id", hit["_id"]
                ),
                score=hit.get("_score") or 0.0,
                rank=rank,
                product_title=source.get("product_title", ""),
            )
            for rank, hit in enumerate(raw_hits, start=1)
        ]
