"""
device.py
---------
Seleção única de dispositivo (CPU/GPU) para todo o pipeline.

Os notebooks definem apenas ``DEVICE = "cpu"``, ``"cuda"`` ou ``"auto"`` e
usam :func:`build_runtime_config` para derivar o restante:

- PyTorch (embeddings): ``RuntimeConfig.device``
- Polars: :func:`collect` usa o motor GPU (cudf-polars) quando o dispositivo
  é ``cuda`` e a dependência está instalada; caso contrário cai para CPU.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import polars as pl

logger = logging.getLogger(__name__)

type DeviceChoice = Literal["auto", "cpu", "cuda"]


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    """Parâmetros de execução derivados do dispositivo escolhido."""

    device: str
    batch_size: int
    max_seq_length: int


def _cuda_available() -> bool:
    try:
        import torch
    except ImportError:
        return False
    return torch.cuda.is_available()


def resolve_device(choice: DeviceChoice = "auto") -> str:
    """Converte a escolha do usuário em um dispositivo válido.

    Se ``cuda`` for pedido e não houver GPU, cai para ``cpu`` com aviso.
    """
    if choice == "cpu":
        return "cpu"

    has_cuda = _cuda_available()
    if choice == "cuda" and not has_cuda:
        logger.warning("DEVICE='cuda' solicitado, mas nenhuma GPU foi encontrada. Usando CPU.")
        return "cpu"
    return "cuda" if has_cuda else "cpu"


def build_runtime_config(choice: DeviceChoice = "auto") -> RuntimeConfig:
    """Retorna defaults de batch/sequência adequados ao dispositivo."""
    device = resolve_device(choice)
    if device == "cuda":
        return RuntimeConfig(device=device, batch_size=256, max_seq_length=256)
    return RuntimeConfig(device=device, batch_size=32, max_seq_length=128)


def collect(lf: pl.LazyFrame, device: str = "cpu") -> pl.DataFrame:
    """Materializa um LazyFrame, usando o motor GPU do Polars se possível."""
    if device.startswith("cuda"):
        try:
            return lf.collect(engine="gpu")
        except Exception as exc:  # cudf-polars ausente ou consulta não suportada
            logger.warning("Motor GPU do Polars indisponível (%s). Usando CPU.", exc)
    return lf.collect()
