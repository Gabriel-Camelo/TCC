"""
mappings.py
-----------
Definição dos mapeamentos (index mappings) do Elasticsearch para cada modelo.

Responsabilidades:
  - Gerar o mapping correto para índices de embedding (dense_vector + campos de texto)
  - Gerar o mapping para o índice BM25 puro (sem vetor)
  - Centralizar parâmetros do HNSW (m, ef_construction) para facilitar ablation studies

Os campos de texto usam o analyzer "english" (stemming + stopwords) para maximizar
a qualidade do BM25. O campo `product_text` é a concatenação usada para gerar o
embedding e também serve como fallback na busca BM25 do índice KNN.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Final, Literal, TypedDict

from src.models.registry import ModelConfig

# ---------------------------------------------------------------------------
# Tipagem estruturada (PEP 695 & TypedDict)
# ---------------------------------------------------------------------------

type SimilarityMetric = Literal["cosine", "dot_product", "l2_norm"]
type FieldProperties = MappingProxyType[str, dict[str, Any]]


class IndexSettings(TypedDict):
    number_of_shards: int
    number_of_replicas: int
    refresh_interval: str


class IndexDefinition(TypedDict):
    mappings: dict[str, dict[str, Any]]
    settings: IndexSettings


# ---------------------------------------------------------------------------
# Parâmetros HNSW — ajuste aqui para todos os índices de uma vez
# ---------------------------------------------------------------------------

HNSW_M: Final[int] = 16  # número de conexões por nó — maior = mais recall, mais memória
HNSW_EF_CONSTRUCTION: Final[int] = (
    100  # tamanho da fila durante a construção — maior = mais preciso, mais lento
)


# ---------------------------------------------------------------------------
# Campos de texto compartilhados entre todos os índices (Imutável)
# ---------------------------------------------------------------------------

_TEXT_FIELDS: Final[FieldProperties] = MappingProxyType(
    {
        "product_id": {"type": "keyword"},
        "product_title": {
            "type": "text",
            "analyzer": "english",
            # sub-campo keyword para agregações e sorting
            "fields": {"raw": {"type": "keyword"}},
        },
        "product_description": {"type": "text", "analyzer": "english"},
        "product_bullet_point": {"type": "text", "analyzer": "english"},
        "product_brand": {
            "type": "text",
            "analyzer": "english",
            "fields": {"raw": {"type": "keyword"}},
        },
        "product_color": {"type": "keyword"},
        "product_locale": {"type": "keyword"},
        # Concatenação completa usada para gerar o embedding e busca BM25 no índice KNN
        "product_text": {"type": "text", "analyzer": "english"},
    }
)


# ---------------------------------------------------------------------------
# Builders de mapping
# ---------------------------------------------------------------------------


def build_embedding_mapping(
    config: ModelConfig,
    *,
    m: int = HNSW_M,
    ef_construction: int = HNSW_EF_CONSTRUCTION,
    similarity: SimilarityMetric = "cosine",
) -> IndexDefinition:
    """
    Retorna o mapping completo para um índice de embedding KNN.

    O campo `embedding` usa dense_vector com índice HNSW e similaridade
    coseno por padrão. Como os embeddings são normalizados (L2=1), coseno
    e dot-product produzem resultados equivalentes, mas coseno é mais explícito.

    Parameters
    ----------
    config:
        ModelConfig do modelo — usado para extrair `embedding_dim`.
    m:
        Número de conexões bidirecionais por nó no grafo HNSW.
    ef_construction:
        Tamanho da lista dinâmica de candidatos durante a construção do grafo.
    similarity:
        Métrica de similaridade vetorial ("cosine", "dot_product" ou "l2_norm").
    """
    return {
        "mappings": {
            "properties": {
                **_TEXT_FIELDS,
                "embedding": {
                    "type": "dense_vector",
                    "dims": config.embedding_dim,
                    "index": True,
                    "similarity": similarity,
                    "index_options": {
                        "type": "hnsw",
                        "m": m,
                        "ef_construction": ef_construction,
                    },
                },
            }
        },
        "settings": _index_settings(),
    }


def build_bm25_mapping() -> IndexDefinition:
    """
    Retorna o mapping para o índice BM25 puro (sem campo de vetor).

    Usa BM25 com parâmetros padrão do Elasticsearch (k1=1.2, b=0.75).
    Para tunar, adicione "similarity" nas settings do índice.
    """
    return {
        "mappings": {
            "properties": dict(_TEXT_FIELDS),
        },
        "settings": _index_settings(),
    }


# ---------------------------------------------------------------------------
# Settings comuns
# ---------------------------------------------------------------------------


def _index_settings() -> IndexSettings:
    """
    Configurações base do índice.

    number_of_shards=1 é suficiente para o volume do ESCI US (~482k docs).
    Aumentar para experimentos com réplicas em cluster multi-node.
    """
    return {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        # Desabilita refresh automático durante a indexação em bulk;
        # lembrar de chamar es.indices.refresh() ao final.
        "refresh_interval": "-1",
    }


def restore_refresh_interval() -> dict[str, dict[str, str]]:
    """
    Payload para restaurar o refresh_interval após a indexação bulk.
    Chamar via es.indices.put_settings() no indexer.
    """
    return {"index": {"refresh_interval": "1s"}}
