.PHONY: run

POETRY=poetry
POETRY_OK:=$(shell command -v $(POETRY) 2> /dev/null)
PYSRC=botcpdf

poetry:
ifndef POETRY_OK
	python3 -m pip install poetry
endif

install-dev: poetry
	$(POETRY) config virtualenvs.in-project true
	$(POETRY) install

fmt: install-dev
	$(POETRY) run black -t py311 $(PYSRC)

lint: install-dev
	$(POETRY) run pylint $(PYSRC)

run: poetry
	poetry run python -m botcpdf.main
