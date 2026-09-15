PYTHON ?= python3
PIP ?= pip

.PHONY: setup fetch-model convert-model run frontend test battery demo-cache verify-demo-cache integrity offline export-report lint

setup: ## create venv and install pinned deps (requires network ONCE)
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt
	.venv/bin/pip install -r backend/requirements-dev.txt

fetch-model: ## ONE-TIME network step: download the CellML artefact (build only)
	$(PYTHON) scripts/fetch_model.py

convert-model: ## CellML -> models/ord_cipa_v1.mmt + audits (offline afterwards)
	$(PYTHON) scripts/convert_model.py

run: ## run the FastAPI backend (single worker, offline)
	.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8001 --workers 1

frontend: ## install + build the React frontend
	cd frontend && npm install && npm run build

frontend-dev: ## run the frontend dev server
	cd frontend && npm run dev

test: ## CI gate: unit + api + failure + repro + contract
	.venv/bin/pytest tests/unit tests/api tests/failure tests/repro tests/contract -q

test-all: ## everything, including numerics + validation (pre-demo gate)
	.venv/bin/pytest -q

battery: ## run the §16 verification battery
	.venv/bin/python scripts/run_verification.py

demo-cache: ## precompute demo grids (§22.3)
	.venv/bin/python scripts/build_demo_cache.py

verify-demo-cache: ## live re-check of 10% of cached demo values
	.venv/bin/python scripts/verify_demo_cache.py

integrity: ## provenance + forbidden-manifest checks
	.venv/bin/python scripts/verify_data_integrity.py

offline: ## assert no runtime network access
	.venv/bin/python scripts/check_offline.py

export-report: ## CLI report generation
	.venv/bin/python scripts/export_report.py

lint: ## ruff check + format
	.venv/bin/ruff check backend scripts tests
	.venv/bin/ruff format --check backend scripts tests
