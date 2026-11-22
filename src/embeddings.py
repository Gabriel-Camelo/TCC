"""
embeddings.py
-------------
Geração e leitura de embeddings pré-calculados, para separar a parte cara (modelos, GPU no Colab)
da indexação no Elasticsearch (máquina local).

Para cada modelo são gravados dois arquivos em um diretório:
  <alias>.parquet     colunas `product_id` (String) e `embedding` (Array[Float32, dim])
  <alias>.meta.json   configuração usada na geração (modelo, dimensão, texto, tamanho...)

O `.meta.json` é gravado por último: se ele existe, o parquet está completo.

Uso típico
----------
    # No Colab
    from src.embeddings import generate_embeddings
    generate_embeddings("bge", prepared_df, Path("data/embeddings"), device="cuda")

    # Na máquina local (sem torch)
    from src.embeddings import check_compatibility, read_embeddings
    embeddings_df, meta = read_embeddings("bge", Path("data/embeddings"))
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from importlib import metadata as importlib_metadata
from pathlib import Path

import numpy as np
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

from src.models.registry import ModelConfig, get_model_config
from src.text import EMBEDDING_FIELDS, FIELD_SEPARATOR

logger = logging.getLogger(__name__)

NORM_TOLERANCE = 1e-3


@dataclass(frozen=True, slots=True)
class EmbeddingsMeta:
    """Configuração usada para gerar um arquivo de embeddings."""

    alias: str
    hf_name: str
    embedding_dim: int
    max_seq_length: int
    normalize_embeddings: bool
    n_docs: int
    device: str
    text_fields: list[str]
    field_separator: str
    dtype: str
    sentence_transformers_version: str
    created_at: str


def embeddings_path(directory: Path, alias: str) -> Path:
    return Path(directory) / f"{alias}.parquet"


def meta_path(directory: Path, alias: str) -> Path:
    return Path(directory) / f"{alias}.meta.json"


def is_complete(directory: Path, alias: str) -> bool:
    """True se o parquet e o `.meta.json` do modelo existem."""
    return embeddings_path(directory, alias).exists() and meta_path(directory, alias).exists()


def read_meta(directory: Path, alias: str) -> EmbeddingsMeta:
    return EmbeddingsMeta(**json.loads(meta_path(directory, alias).read_text(encoding="utf-8")))


def read_embeddings(alias: str, directory: Path) -> tuple[pl.DataFrame, EmbeddingsMeta]:
    """Lê o parquet e os metadados de um modelo."""
    if not is_complete(directory, alias):
        raise FileNotFoundError(f"Embeddings de '{alias}' não encontrados (ou incompletos) em {directory}.")
    return pl.read_parquet(embeddings_path(directory, alias)), read_meta(directory, alias)


def check_compatibility(meta: EmbeddingsMeta, config: ModelConfig, *, n_docs: int | None = None) -> list[str]:
    """Lista de divergências entre o arquivo de embeddings e a configuração atual (vazia se compatível)."""
    problems: list[str] = []
    if meta.hf_name != config.hf_name:
        problems.append(f"modelo do arquivo é '{meta.hf_name}', mas models.json usa '{config.hf_name}'")
    if meta.embedding_dim != config.embedding_dim:
        problems.append(f"dimensão do arquivo é {meta.embedding_dim}, mas models.json usa {config.embedding_dim}")
    if meta.normalize_embeddings != config.normalize_embeddings:
        problems.append("normalize_embeddings difere do models.json")
    if meta.text_fields != list(EMBEDDING_FIELDS) or meta.field_separator != FIELD_SEPARATOR:
        problems.append(f"texto do produto mudou (arquivo: {meta.text_fields}, atual: {list(EMBEDDING_FIELDS)})")
    if n_docs is not None and meta.n_docs != n_docs:
        problems.append(f"arquivo tem {meta.n_docs} produtos, mas o catálogo tem {n_docs}")
    return problems


def _validate_vectors(vectors: np.ndarray, config: ModelConfig, n_docs: int) -> None:
    expected = (n_docs, config.embedding_dim)
    if vectors.shape != expected:
        raise ValueError(
            f"Formato dos embeddings de '{config.alias}' é {vectors.shape}, esperado {expected}. "
            "Corrija 'embedding_dim' em models.json."
        )
    if not np.isfinite(vectors).all():
        raise ValueError(f"Embeddings de '{config.alias}' contêm NaN ou infinito.")
    if config.normalize_embeddings:
        deviation = float(np.abs(np.linalg.norm(vectors, axis=1) - 1.0).max())
        if deviation > NORM_TOLERANCE:
            raise ValueError(f"Embeddings de '{config.alias}' não estão normalizados (desvio máximo da norma: {deviation:.4f}).")


def generate_embeddings(
    alias: str,
    prepared_df: pl.DataFrame,
    out_dir: Path,
    *,
    device: str = "cpu",
    batch_size: int = 128,
    max_seq_length: int | None = None,
    overwrite: bool = False,
    show_progress: bool = True,
) -> Path:
    """
    Gera os embeddings de ``product_text`` com o modelo ``alias`` e grava parquet + metadados em ``out_dir``.

    Pula o modelo se já existir um arquivo compatível (use ``overwrite=True`` para refazer).
    ``max_seq_length=None`` usa o limite de tokens do próprio modelo (``models.json``).

    Raises
    ------
    ValueError
        Se a dimensão dos vetores diferir de ``embedding_dim`` ou se os vetores forem inválidos.
    """
    from src.models.core import load_model, unload_model

    config = get_model_config(alias)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    final = embeddings_path(out_dir, alias)
    n_docs = prepared_df.height

    if not overwrite and is_complete(out_dir, alias):
        problems = check_compatibility(read_meta(out_dir, alias), config, n_docs=n_docs)
        if not problems:
            logger.info("%s: embeddings já existem e são compatíveis, pulando.", alias)
            return final
        logger.warning("%s: arquivo existente incompatível (%s); regenerando.", alias, "; ".join(problems))

    meta_path(out_dir, alias).unlink(missing_ok=True)  # sem meta, o arquivo conta como incompleto

    model = load_model(alias, device=device, max_seq_length_override=max_seq_length)
    try:
        vectors = model.encode(
            prepared_df["product_text"].to_list(),
            batch_size=batch_size,
            normalize_embeddings=config.normalize_embeddings,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        ).astype(np.float32, copy=False)
        effective_max_seq_length = int(model.max_seq_length)
    finally:
        unload_model(alias, device=device)

    if config.normalize_embeddings:
        # Modelos em float16 (GPU) normalizam com pouca precisão; renormaliza em float32.
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors /= np.where(norms > 0, norms, 1.0)

    _validate_vectors(vectors, config, n_docs)

    # Tabela Arrow com FixedSizeList construída sem copiar a matriz (importa com o catálogo completo,
    # em que a matriz tem vários GB). O parquet resultante é lido normalmente como Array[Float32, dim].
    table = pa.table(
        {
            "product_id": prepared_df["product_id"].to_arrow(),
            "embedding": pa.FixedSizeListArray.from_arrays(
                pa.array(np.ascontiguousarray(vectors).reshape(-1)), config.embedding_dim
            ),
        }
    )
    temporary = final.with_name(final.name + ".tmp")
    pq.write_table(table, temporary, compression="zstd")
    del table, vectors
    temporary.replace(final)

    try:
        st_version = importlib_metadata.version("sentence-transformers")
    except importlib_metadata.PackageNotFoundError:
        st_version = "desconhecida"
    meta = EmbeddingsMeta(
        alias=alias,
        hf_name=config.hf_name,
        embedding_dim=config.embedding_dim,
        max_seq_length=effective_max_seq_length,
        normalize_embeddings=config.normalize_embeddings,
        n_docs=n_docs,
        device=device,
        text_fields=list(EMBEDDING_FIELDS),
        field_separator=FIELD_SEPARATOR,
        dtype="float32",
        sentence_transformers_version=st_version,
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )
    meta_path(out_dir, alias).write_text(json.dumps(asdict(meta), indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("%s: %d embeddings (dim=%d) gravados em %s", alias, n_docs, config.embedding_dim, final)
    return final
