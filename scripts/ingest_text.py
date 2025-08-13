import argparse, json, sys
from app.models.ingest import IngestTextRequest
from app.ingestion.pipeline import ingest_text

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tenant", default="default")
    p.add_argument("--source", required=True)
    p.add_argument("--title", default=None)
    p.add_argument("--tags", nargs="*", default=[])
    p.add_argument("--text", required=True, help="Raw text to ingest")
    args = p.parse_args()
    req = IngestTextRequest(tenant_id=args.tenant, source_id=args.source, title=args.title, tags=args.tags, text=args.text)
    res = ingest_text(req)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
