from __future__ import annotations

import gc
import os

import torch
from sentence_transformers import SentenceTransformer

from src.models.registry import ModelConfig, registry

# Usa todos os núcleos de CPU disponíveis para inferência do PyTorch
torch.set_num_threads(os.cpu_count() or 1)

_MODEL_CACHE: dict[str, SentenceTransformer] = {}


def _cache_key(alias: str, device: str) -> str:
    return f"{alias}:{device}"


def load_model(
    alias: str, device: str = "cpu", max_seq_length_override: int | None = None
) -> SentenceTransformer:
    """
    Carrega e cacheia um SentenceTransformer pelo alias.

    O cache evita recarregar o mesmo modelo se for solicitado novamente na
    mesma sessão. Use unload_model() para liberar a memória quando o modelo
    não for mais necessário (ex.: entre modelos consecutivos num loop).

    Parameters
    ----------
    alias:
        Apelido do modelo conforme registrado em models.json.
    device:
        "cpu", "cuda", "cuda:0", "mps", etc.
    max_seq_length_override:
        Se informado, sobrescreve o max_seq_length do config. Valores menores
        aceleram a inferência (menos tokens por texto) — útil em CPU.

    Returns
    -------
    SentenceTransformer
        Instância pronta para encode().
    """
    key = _cache_key(alias, device)
    if key in _MODEL_CACHE:
        model = _MODEL_CACHE[key]
        if max_seq_length_override is not None:
            model.max_seq_length = max_seq_length_override
        return model

    cfg = registry.get_model_config(alias)

    try:
        model = SentenceTransformer(cfg.hf_name, device=device)
    except (OSError, ValueError):
        # Modelo base do HuggingFace sem config sentence-transformers:
        # constrói manualmente Transformer + Pooling.
        from sentence_transformers import models

        word_model = models.Transformer(cfg.hf_name)
        pooling_mode = cfg.pooling_mode or "mean"
        pooling = models.Pooling(
            word_model.get_word_embedding_dimension(), pooling_mode
        )
        model = SentenceTransformer(modules=[word_model, pooling], device=device)

    # Aplica max_seq_length: override tem precedência sobre o config registrado
    if max_seq_length_override is not None:
        model.max_seq_length = max_seq_length_override
    else:
        model.max_seq_length = cfg.max_seq_length

    _MODEL_CACHE[key] = model
    return model


def unload_model(alias: str, device: str = "cpu") -> None:
    """
    Remove um modelo do cache e libera toda a memória associada.

    Deleta a referência do modelo, roda gc.collect() e esvazia o cache CUDA
    (se aplicável). Use entre modelos consecutivos para evitar acúmulo de RAM.
    """
    key = _cache_key(alias, device)
    model = _MODEL_CACHE.pop(key, None)
    if model is not None:
        del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def unload_all_models() -> None:
    """
    Remove todos os modelos do cache e libera a memória.
    Útil ao final de um script ou antes de uma nova fase de processamento.
    """
    _MODEL_CACHE.clear()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def encode(
    alias: str,
    texts: list[str],
    batch_size: int = 128,
    device: str = "cpu",
    show_progress_bar: bool = False,
    unload_after: bool = False,
) -> list[list[float]]:
    """
    Atalho para carregar o modelo e gerar embeddings em uma chamada só.

    Retorna uma lista de listas (compatível com JSON / bulk do ES).

    Parameters
    ----------
    unload_after:
        Se True, remove o modelo do cache após gerar os embeddings,
        liberando a memória RAM. Útil em scripts que processam múltiplos
        modelos sequencialmente.
    """
    cfg = registry.get_model_config(alias)
    model = load_model(alias, device=device)

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=cfg.normalize_embeddings,
        show_progress_bar=show_progress_bar,
    )

    if unload_after:
        unload_model(alias, device=device)

    return embeddings.tolist()
