"""
model_registry.py
------------------
API pública do registro de modelos de embedding.

Centraliza o acesso a configurações de modelos, carregamento e cache de
SentenceTransformers, de forma que notebooks e scripts importem apenas
deste módulo::

    from src.models.model_registry import (
        BM25_INDEX_NAME,
        list_models,
        get_model_config,
        load_model,
        unload_model,
        unload_all_models,
        encode,
    )
"""

from __future__ import annotations

from src.models.core import encode, load_model, unload_all_models, unload_model
from src.models.registry import ModelConfig, ModelRegistry

# Nome do índice Elasticsearch que contém apenas BM25 (sem embeddings).
BM25_INDEX_NAME = "esci-bm25-us"

# Singleton do registro — já carregado com models.json em ``core.py``.
from src.models.core import registry as _registry  # noqa: E402


def get_model_config(alias: str) -> ModelConfig:
    """Retorna a configuração de um modelo pelo alias.

    Raises
    ------
    KeyError
        Se o alias não estiver registrado.
    """
    return _registry.get_model_config(alias)


def list_models() -> list[ModelConfig]:
    """Retorna todos os modelos registrados, na ordem de declaração."""
    return _registry.list_models()


def filter_models(*tags: str) -> list[ModelConfig]:
    """Filtra modelos que possuem **todas** as tags informadas."""
    return _registry.filter_models(*tags)


__all__ = [
    "BM25_INDEX_NAME",
    "ModelConfig",
    "ModelRegistry",
    "encode",
    "filter_models",
    "get_model_config",
    "list_models",
    "load_model",
    "unload_all_models",
    "unload_model",
]
