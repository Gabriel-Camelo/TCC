"""
download.py
-----------
Baixa os arquivos do Amazon Shopping Queries Dataset (ESCI) do repositório oficial
(https://github.com/amazon-science/esci-data/tree/main/shopping_queries_dataset).

Os arquivos ``.parquet`` ficam no Git LFS: a URL ``raw.githubusercontent.com`` devolve só um
ponteiro de ~130 bytes, então eles são baixados de ``media.githubusercontent.com``. O CSV não usa LFS.
Usa apenas a biblioteca padrão.

Uso típico
----------
    from pathlib import Path
    from src.download import download_esci

    download_esci(Path("data/raw"))
"""

from __future__ import annotations

import shutil
import time
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError

_REPO_PATH = "amazon-science/esci-data/main/shopping_queries_dataset"
LFS_BASE_URL = f"https://media.githubusercontent.com/media/{_REPO_PATH}"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{_REPO_PATH}"

PARQUET_MAGIC = b"PAR1"
_CHUNK_SIZE = 1024 * 1024
_TIMEOUT_SECONDS = 60
_USER_AGENT = "esci-downloader"


@dataclass(frozen=True, slots=True)
class EsciFile:
    """Arquivo do dataset e a URL de onde ele deve ser baixado."""

    name: str
    url: str

    @property
    def is_parquet(self) -> bool:
        return self.name.endswith(".parquet")


ESCI_FILES: tuple[EsciFile, ...] = (
    EsciFile(
        "shopping_queries_dataset_products.parquet",
        f"{LFS_BASE_URL}/shopping_queries_dataset_products.parquet",
    ),
    EsciFile(
        "shopping_queries_dataset_examples.parquet",
        f"{LFS_BASE_URL}/shopping_queries_dataset_examples.parquet",
    ),
    EsciFile(
        "shopping_queries_dataset_sources.csv",
        f"{RAW_BASE_URL}/shopping_queries_dataset_sources.csv",
    ),
)


def _request(url: str, method: str = "GET") -> urllib.request.Request:
    return urllib.request.Request(url, method=method, headers={"User-Agent": _USER_AGENT})


def _remote_size(url: str) -> int | None:
    """Tamanho do arquivo remoto em bytes, ou None se o servidor não informar."""
    with urllib.request.urlopen(_request(url, "HEAD"), timeout=_TIMEOUT_SECONDS) as response:
        length = response.headers.get("Content-Length")
    return int(length) if length else None


def _validate(file: EsciFile, path: Path, expected_size: int | None) -> None:
    size = path.stat().st_size
    if expected_size is not None and size != expected_size:
        raise ValueError(f"{file.name}: tamanho {size:,} B difere do esperado ({expected_size:,} B).")
    if file.is_parquet:
        with path.open("rb") as handle:
            head = handle.read(len(PARQUET_MAGIC))
            handle.seek(-len(PARQUET_MAGIC), 2)
            tail = handle.read(len(PARQUET_MAGIC))
        if head != PARQUET_MAGIC or tail != PARQUET_MAGIC:
            raise ValueError(
                f"{file.name} não é um parquet válido (possível ponteiro Git LFS ou download incompleto)."
            )


def _stream_to(url: str, target: Path, total: int | None, label: str, progress: bool) -> None:
    received = 0
    next_report = 0.0
    with urllib.request.urlopen(_request(url), timeout=_TIMEOUT_SECONDS) as response, target.open("wb") as out:
        while chunk := response.read(_CHUNK_SIZE):
            out.write(chunk)
            received += len(chunk)
            if progress and total and received / total >= next_report:
                print(f"  {label}: {received / 1024**2:,.0f} / {total / 1024**2:,.0f} MB ({received / total:.0%})")
                next_report += 0.1
    if progress:
        print(f"  {label}: concluído ({received / 1024**2:,.1f} MB)")


def download_file(
    file: EsciFile,
    dest_dir: Path,
    *,
    overwrite: bool = False,
    retries: int = 3,
    progress: bool = True,
) -> Path:
    """Baixa um arquivo para ``dest_dir`` e valida o resultado.

    Pula o download se o arquivo já existir com o tamanho remoto (use ``overwrite=True`` para forçar).
    Grava em um arquivo ``.part`` e só renomeia depois de validar.

    Raises
    ------
    ValueError
        Se o arquivo baixado estiver incompleto ou não for um parquet válido.
    OSError
        Se faltar espaço em disco ou a rede falhar depois de todas as tentativas.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    final = dest_dir / file.name
    partial = final.with_name(final.name + ".part")

    expected = _remote_size(file.url)
    if final.exists() and not overwrite and (expected is None or final.stat().st_size == expected):
        if progress:
            print(f"{file.name}: já existe, pulando.")
        return final

    if expected is not None:
        free = shutil.disk_usage(dest_dir).free
        if free < expected:
            raise OSError(
                f"Espaço insuficiente para {file.name}: necessário {expected / 1024**3:.2f} GB, "
                f"livre {free / 1024**3:.2f} GB."
            )

    if progress:
        size_text = f"{expected / 1024**2:,.0f} MB" if expected else "tamanho desconhecido"
        print(f"{file.name}: baixando ({size_text})")

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            _stream_to(file.url, partial, expected, file.name, progress)
            _validate(file, partial, expected)
            partial.replace(final)
            return final
        except ValueError:
            partial.unlink(missing_ok=True)
            raise
        except (URLError, TimeoutError, ConnectionError, OSError) as exc:
            last_error = exc
            partial.unlink(missing_ok=True)
            if attempt < retries:
                wait = 2**attempt
                print(f"  falha ({exc}); nova tentativa em {wait}s ({attempt}/{retries})")
                time.sleep(wait)

    raise OSError(f"Falha ao baixar {file.name} após {retries} tentativas: {last_error}")


def download_esci(
    dest_dir: Path,
    *,
    files: Sequence[EsciFile] = ESCI_FILES,
    overwrite: bool = False,
    progress: bool = True,
) -> list[Path]:
    """Baixa os arquivos do ESCI (parquets e CSV) para ``dest_dir`` e retorna os caminhos."""
    return [download_file(f, Path(dest_dir), overwrite=overwrite, progress=progress) for f in files]
