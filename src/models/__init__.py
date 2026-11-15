"""Pacote de modelos de embedding.

O registro (``src.models.registry``) não depende de torch. O carregamento
de modelos fica em ``src.models.core`` e é importado explicitamente.
"""

from src.models.registry import (
    BM25_INDEX_NAME,
    ModelConfig,
    ModelRegistry,
    filter_models,
    get_model_config,
    list_models,
    registry,
)

__all__ = [
    "BM25_INDEX_NAME",
    "ModelConfig",
    "ModelRegistry",
    "filter_models",
    "get_model_config",
    "list_models",
    "registry",
]
