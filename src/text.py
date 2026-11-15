"""
text.py
-------
Montagem do texto do produto usado para gerar embeddings e indexar no Elasticsearch.

Módulo leve (apenas Polars), compartilhado entre a geração de embeddings (Colab) e a
indexação (máquina local), para que os dois lados usem exatamente o mesmo texto.
"""

from __future__ import annotations

import polars as pl

type FrameLike = pl.DataFrame | pl.LazyFrame

# Campos concatenados para formar `product_text`. Mudar esta tupla invalida embeddings já gerados.
EMBEDDING_FIELDS: tuple[str, ...] = (
    "product_title",
    # "product_brand",
    # "product_color",
    # "product_bullet_point",
    # "product_description",
)

FIELD_SEPARATOR = " | "


def prepare_dataframe(df: FrameLike) -> pl.DataFrame:
    """
    Garante que o DataFrame tenha a coluna `product_text` e retorna um
    DataFrame eager pronto para gerar embeddings ou indexar.

    Utiliza `pl.concat_str` nativo do Polars para concatenar colunas em Rust
    sem materializar dicionários Python na memória.
    """
    lf = df.lazy() if isinstance(df, pl.DataFrame) else df
    schema_names = lf.collect_schema().names()

    if "product_locale" in schema_names:
        lf = lf.filter(pl.col("product_locale") == "us")

    text_exprs = [
        pl.col(field).cast(pl.String).fill_null("") if field in schema_names else pl.lit("")
        for field in EMBEDDING_FIELDS
    ]

    return lf.with_columns(pl.concat_str(text_exprs, separator=FIELD_SEPARATOR).alias("product_text")).collect()
