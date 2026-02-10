run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

fmt:
	ruff check --fix .

typecheck:
	mypy app

ingest-all:
	python scripts/ingest_all.py --clean

upload:
	python scripts/upload_file.py $(file)

docs-list:
	python scripts/delete_docs.py --list

docs-delete:
	python scripts/delete_docs.py --all
