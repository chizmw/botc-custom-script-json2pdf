INPUT_FILE=

.PHONY: all process

#all: poetry install-dev fmt lint run

all: examples

process:
	@basename="$(shell basename "$(INPUT_FILE)" .json)" && \
	poetry run python3 -m botcpdf.main "$(INPUT_FILE)"

clean:
	@find . -type f \( -iname "*.pdf" -o -iname "*.html" \) -exec rm -vf {} \;

POETRY=poetry
POETRY_OK:=$(shell command -v $(POETRY) 2> /dev/null)
PYSRC=botcpdf

poetry:
ifndef POETRY_OK
	python3 -m pip install poetry
endif

install-dev: poetry
	@$(POETRY) config virtualenvs.in-project true
	@$(POETRY) install --quiet

fmt: install-dev
	@$(POETRY) run black -t py311 $(PYSRC)

lint: install-dev
	@$(POETRY) run pylint $(PYSRC)

tb: poetry
	@$(MAKE) process INPUT_FILE="scripts/Trouble Brewing.json"
ifeq ($(shell uname),Darwin)
	@open -a Preview "pdfs/Trouble Brewing.pdf"
endif

nrb: poetry
	@$(MAKE) process INPUT_FILE="scripts/No Roles Barred.json"
ifeq ($(shell uname),Darwin)
	@open -a Preview "pdfs/No Roles Barred.pdf"
endif

all-scripts: install-dev
	@find scripts -type f -exec $(MAKE) process INPUT_FILE="{}" \;

optimise-pdf: install-dev
	@find pdfs -type f -not -name "*.opt.pdf" -exec $(POETRY) run python3 -m botcpdf.optimise_pdf "{}" \;

# this is just a quick helper for my own use - Chisel
refresh-json:
	@curl -so roles.json https://raw.githubusercontent.com/bra1n/townsquare/develop/src/roles.json
	@git add roles.json
	@git commit --no-verify -m "Update roles.json from bra1n/townsquare"

# another helper for my own use - Chisel
changelog:
	@changie batch $$(poetry version --short)
	@changie merge
	@git commit --no-verify -m "changie updates for $$(poetry version --short)" CHANGELOG.md
