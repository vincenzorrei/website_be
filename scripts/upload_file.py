"""Upload a single file to the vector store.

Usage:
    python scripts/upload_file.py doc_uploaded/file.pdf
    python scripts/upload_file.py doc_uploaded/file.pdf --source custom-name --tenant default
"""
import argparse
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingestion.pipeline import ingest_file


def main():
    p = argparse.ArgumentParser(description="Upload a file to the vector store")
    p.add_argument("file", help="Path to the file to upload")
    p.add_argument("--source", default=None, help="Custom source_id (default: filename)")
    p.add_argument("--tenant", default="default", help="Tenant ID")
    args = p.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    print(f"Uploading {path.name} ...")
    result = ingest_file(str(path), tenant_id=args.tenant, source_id=args.source)
    print(f"Done: {result['chunks']} chunks ingested (source_id={result.get('source_id', args.source or path.name)})")


if __name__ == "__main__":
    main()
