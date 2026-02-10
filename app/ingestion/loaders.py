from pathlib import Path


def load_file(path: str) -> str:
    """Load a file and return its text content. Supports .pdf, .txt, .md."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = p.suffix.lower()

    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(p))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()

    if suffix in (".txt", ".md"):
        return p.read_text(encoding="utf-8").strip()

    raise ValueError(f"Unsupported file type: {suffix}")
