INPUT_FILE=

.PHONY: all process

#all: poetry install-dev fmt lint run

all: examples

process: install-dev
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

test-meta: poetry
	@$(MAKE) process INPUT_FILE='scripts/my-test-script.json'
ifeq ($(shell uname),Darwin)
	@open -a Preview 'pdfs/I am a list name.pdf'
endif

all-scripts: install-dev
	@find scripts -type f -exec $(MAKE) process INPUT_FILE="{}" \;

optimise-pdf: install-dev
	@find pdfs -type f -not -name "*.opt.pdf" -exec $(POETRY) run python3 -m botcpdf.optimise_pdf "{}" \;

# this is just a quick helper for my own use - Chisel
refresh-json:
	@curl -so gameinfo/roles-bra1n.json https://raw.githubusercontent.com/bra1n/townsquare/develop/src/roles.json
	@curl -so gameinfo/roles-bra1n-fabled.json https://raw.githubusercontent.com/bra1n/townsquare/develop/src/fabled.json
	@curl -so gameinfo/nightsheet.json https://script.bloodontheclocktower.com/data/nightsheet.json
	@curl -so gameinfo/jinx.json https://script.bloodontheclocktower.com/data/jinx.json
	@changie new -k "Changed" -b "Update gameinfo/*.json from assets"
	@git add gameinfo/*.json .changes/unreleased/Changed-*.yaml
	@git commit --no-verify -m "Update *.json from assets"

next-version:
	@poetry version patch
	@git commit --no-verify -m "bump pyproject version to $$(poetry version --short)" pyproject.toml

# another helper for my own use - Chisel
changelog: next-version
	@changie batch $$(poetry version --short)
	@changie merge
	@git add CHANGELOG.md README.md .changes/
	@git commit --no-verify -m "changie updates for $$(poetry version --short)" CHANGELOG.md README.md .changes/
	@git push

release: fmt lint changelog
	@git tag v$$(poetry version --no-ansi --short)
	@git push --tags

grab-some-scripts:
# Reptiles! Played it. It's fun. It's also a good test of the pdf generation
	@curl -Ls -o scripts/Reptiles.json https://botc-scripts.azurewebsites.net/script/140/1.4.1/download
# No Roles Barred - the first "pretty custom script" I saw, that started me on this journey (nometa)
	@curl -Ls -o 'scripts/No Roles Barred.json' https://botc-scripts.azurewebsites.net/script/258/1.0.1/download
# No Greater Joy - an official teensyville script (nometa)
	@curl -Ls -o 'scripts/No Greater Joy.json' https://botc-scripts.azurewebsites.net/script/77/1.0.0/download
# Trouble Brewing - the intro script, so we can see how a generated version of it looks (nometa)
	@curl -Ls -o 'scripts/Trouble Brewing.json' https://botc-scripts.azurewebsites.net/script/133/1.0.0/download
# Trouble Distilled - my first custom script; might as well sneak in some awareness that it exists
	@curl -Ls -o 'scripts/Trouble Distilled.json' https://botc-scripts.azurewebsites.net/script/303/1.0.0/download
