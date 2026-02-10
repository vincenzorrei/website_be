"""Re-ingest all files in doc_uploaded/.

Usage:
    python scripts/ingest_all.py              # ingest all files
    python scripts/ingest_all.py --clean      # delete all + re-ingest
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingestion.pipeline import ingest_file
from app.vectordb.utils import delete_all

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}
DOC_DIR = Path(__file__).resolve().parent.parent / "doc_uploaded"


def main():
    p = argparse.ArgumentParser(description="Ingest all files from doc_uploaded/")
    p.add_argument("--clean", action="store_true", help="Delete all documents before re-ingesting")
    p.add_argument("--tenant", default="default", help="Tenant ID")
    args = p.parse_args()

    if not DOC_DIR.exists():
        print(f"Directory not found: {DOC_DIR}")
        sys.exit(1)

    files = [f for f in sorted(DOC_DIR.iterdir()) if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not files:
        print("No supported files found in doc_uploaded/")
        return

    if args.clean:
        count = delete_all(args.tenant)
        print(f"Cleaned: deleted {count} existing chunks\n")

    total_chunks = 0
    for f in files:
        print(f"Ingesting {f.name} ... ", end="", flush=True)
        result = ingest_file(str(f), tenant_id=args.tenant)
        chunks = result["chunks"]
        total_chunks += chunks
        print(f"{chunks} chunks")

    print(f"\nDone: {len(files)} files, {total_chunks} total chunks")


if __name__ == "__main__":
    main()
