"""Manage documents in the vector store.

Usage:
    python scripts/delete_docs.py --list                    # list documents
    python scripts/delete_docs.py --source doc_name         # delete specific source
    python scripts/delete_docs.py --all                     # delete everything
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.vectordb.utils import delete_by_source, delete_all, list_sources


def main():
    p = argparse.ArgumentParser(description="Manage vector store documents")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all documents")
    group.add_argument("--source", type=str, help="Delete a specific source_id")
    group.add_argument("--all", action="store_true", help="Delete all documents")
    p.add_argument("--tenant", default="default", help="Tenant ID")
    args = p.parse_args()

    if args.list:
        sources = list_sources(args.tenant)
        if not sources:
            print("No documents found.")
            return
        total = 0
        for s in sources:
            print(f"  {s['source_id']}  ({s['chunks']} chunks)")
            total += s["chunks"]
        print(f"\nTotal: {len(sources)} documents, {total} chunks")

    elif args.source:
        count = delete_by_source(args.tenant, args.source)
        print(f"Deleted {count} chunks for source '{args.source}'")

    elif args.all:
        count = delete_all(args.tenant)
        print(f"Deleted {count} chunks (all documents)")


if __name__ == "__main__":
    main()
