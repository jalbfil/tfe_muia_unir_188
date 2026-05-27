"""Descarga el corpus normativo CyL definido en manifest.yaml.

Uso:
    python scripts/download_corpus.py             # descarga todas las normas activas v0.1.0
    python scripts/download_corpus.py --check     # sólo verifica URLs (HEAD) sin descargar
    python scripts/download_corpus.py --norma LEY_17_2015   # descarga una sola

Por cada norma activa crea una subcarpeta en resources/corpus_normativo/<norma_id>/
y guarda el PDF + un metadata.json. Las normas diferidas a v0.2.0 se omiten.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    sys.stderr.write("Falta pyyaml. Instala con: pip install pyyaml\n")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = REPO_ROOT / "resources" / "corpus_normativo"
MANIFEST = CORPUS_DIR / "manifest.yaml"

USER_AGENT = "TFM188-CorpusFetcher/0.1 (+academic; CyL emergency RAG)"
TIMEOUT_S = 30


def _load_manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _http(url: str, method: str = "GET") -> tuple[int, bytes]:
    req = Request(url, headers={"User-Agent": USER_AGENT}, method=method)
    with urlopen(req, timeout=TIMEOUT_S) as resp:
        return resp.status, resp.read() if method == "GET" else b""


def _save(norma: dict, payload: bytes) -> Path:
    folder = CORPUS_DIR / norma["norma_id"]
    folder.mkdir(parents=True, exist_ok=True)
    pdf_path = folder / f"{norma['norma_id']}.pdf"
    pdf_path.write_bytes(payload)
    meta_path = folder / "metadata.json"
    meta_path.write_text(
        json.dumps(norma, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return pdf_path


def _process(norma: dict, *, check_only: bool, deferred: set[str]) -> str:
    nid = norma["norma_id"]
    if nid in deferred:
        return f"[skip] {nid}: diferida a v0.2.0"

    url = norma.get("url_pdf")
    if not url or url == "TBD":
        return f"[todo] {nid}: url_pdf pendiente de localizar"

    try:
        if check_only:
            status, _ = _http(url, method="HEAD")
            return f"[ok]   {nid}: HEAD {status}"
        status, payload = _http(url, method="GET")
        if status != 200 or not payload:
            return f"[fail] {nid}: status={status} bytes={len(payload)}"
        path = _save(norma, payload)
        return f"[ok]   {nid}: {len(payload):>9d} B → {path.relative_to(REPO_ROOT)}"
    except (HTTPError, URLError, TimeoutError) as exc:
        return f"[fail] {nid}: {type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Sólo verifica URLs (HEAD).")
    parser.add_argument("--norma", help="Descarga una única norma por norma_id.")
    args = parser.parse_args()

    manifest = _load_manifest()
    deferred = set(manifest.get("defer_to_v020", []))
    normas = manifest["normas"]
    if args.norma:
        normas = [n for n in normas if n["norma_id"] == args.norma]
        if not normas:
            sys.stderr.write(f"norma_id desconocido: {args.norma}\n")
            return 2

    failed = 0
    for norma in normas:
        line = _process(norma, check_only=args.check, deferred=deferred)
        print(line)
        if line.startswith("[fail]"):
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
