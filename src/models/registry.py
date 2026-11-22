"""
registry.py
-----------
Metadados, configuração e registro de modelos de embedding.

Este módulo centraliza o registro de modelos disponíveis para o pipeline
de indexação e busca, substituindo o antigo ``model_registry.py``.

API pública
-----------
- ``BM25_INDEX_NAME``: nome do índice ES puramente lexical
- ``ModelConfig``: dataclass com metadados de cada modelo
- ``ModelRegistry``: classe que gerencia o registro
- ``registry``: singleton já carregado com ``models.json``
- ``get_model_config(alias)``: atalho para ``registry.get_model_config``
- ``list_models()``: atalho para ``registry.list_models``
- ``filter_models(*tags)``: atalho para ``registry.filter_models``
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Nome do índice Elasticsearch que contém apenas BM25 (sem embeddings).
BM25_INDEX_NAME = "esci-bm25-us"

# Diretório base para arquivos de configuração (mesma pasta deste arquivo).
_MODELS_DIR = os.path.dirname(os.path.abspath(__file__))


# =========================================================
# Model Configurations
# =========================================================


@dataclass(frozen=True)
class ModelConfig:
    """Metadados e configuração de um modelo de embedding."""

    # Apelido curto usado em todo o pipeline (nome do índice ES, chave nos resultados)
    alias: str

    # Nome do modelo no HuggingFace Hub (ou caminho local)
    hf_name: str

    # Dimensão do vetor de saída — precisa bater com o mapeamento do índice ES
    embedding_dim: int

    # Comprimento máximo de tokens que o modelo suporta
    max_seq_length: int

    # Normalizar embeddings para L2=1 antes de indexar/buscar (necessário para cosine no ES)
    normalize_embeddings: bool = True

    # Estratégia de pooling explícita, se precisar sobrescrever o padrão do modelo
    # Exemplos: "mean", "cls", "max"  |  None = usar o pooling padrão da config do modelo
    pooling_mode: str | None = None

    # Prefixo aplicado apenas às queries na busca (modelos com instrução, ex.: Qwen3-Embedding).
    # Os documentos são indexados sem prefixo. None = sem prefixo.
    query_prompt: str | None = None

    # Converte o modelo para float16 quando roda em GPU ("float16" | None). Na CPU permanece float32.
    # Necessário para modelos maiores caberem/rodarem rápido numa T4 (que não suporta bfloat16).
    gpu_dtype: str | None = None

    # Rótulo legível para tabelas e gráficos
    display_name: str = ""

    # Tags livres para filtrar modelos em experimentos seletivos
    tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # Preenche display_name com alias caso não seja informado
        if not self.display_name:
            object.__setattr__(self, "display_name", self.alias.upper())
        # Converte tags (lista do JSON) para tuple
        if not isinstance(self.tags, tuple):
            object.__setattr__(self, "tags", tuple(self.tags))

    @property
    def es_index_name(self) -> str:
        """Nome do índice Elasticsearch para o locale US."""
        return f"esci-{self.alias}-us"


# =========================================================
# Registry
# =========================================================


class ModelRegistry:
    """Registro de modelos disponíveis para uso."""

    def __init__(self, model_config_path: str | None = None) -> None:
        self._registry: dict[str, ModelConfig] = {}
        if model_config_path:
            self.load_from_json(model_config_path)

    def load_from_json(self, path: str) -> None:
        """Carrega modelos de um arquivo JSON.

        Aceita tanto um array puro ``[...]`` quanto ``{"models": [...]}``.
        """
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "models" in data:
            data = data["models"]

        for cfg in data:
            self.register_model(ModelConfig(**cfg))

    def register_model(self, config: ModelConfig) -> None:
        """Registra um modelo no registro."""
        self._registry[config.alias] = config

    def list_models(self) -> list[ModelConfig]:
        """Retorna todos os modelos registrados, na ordem de declaração."""
        return list(self._registry.values())

    def get_model_config(self, alias: str) -> ModelConfig:
        """
        Retorna a configuração de um modelo pelo alias.

        Raises
        ------
        KeyError
            Se o alias não estiver registrado.
        """
        if alias not in self._registry:
            available = ", ".join(self._registry.keys())
            raise KeyError(f"Modelo '{alias}' não encontrado. Disponíveis: {available}")
        return self._registry[alias]

    def filter_models(self, *tags: str) -> list[ModelConfig]:
        """
        Retorna modelos que possuem **todos** os tags informados.

        Exemplo
        -------
        >>> filter_models("long-context")
        [ModelConfig(alias='modernbert', ...), ModelConfig(alias='rexbert', ...)]
        """
        return [
            cfg
            for cfg in self._registry.values()
            if all(tag in cfg.tags for tag in tags)
        ]


# =========================================================
# Singleton e funções de conveniência
# =========================================================

registry = ModelRegistry(os.path.join(_MODELS_DIR, "models.json"))


def get_model_config(alias: str) -> ModelConfig:
    """Atalho para ``registry.get_model_config(alias)``."""
    return registry.get_model_config(alias)


def list_models() -> list[ModelConfig]:
    """Atalho para ``registry.list_models()``."""
    return registry.list_models()


def filter_models(*tags: str) -> list[ModelConfig]:
    """Atalho para ``registry.filter_models(*tags)``."""
    return registry.filter_models(*tags)


__all__ = [
    "BM25_INDEX_NAME",
    "ModelConfig",
    "ModelRegistry",
    "filter_models",
    "get_model_config",
    "list_models",
    "registry",
]
