INPUT_FILE=

.PHONY: all

#all: poetry install-dev fmt lint run

all: script-nrb script-tb script-gmv script-cs

variations: install-dev
	@basename="$(shell basename "$(INPUT_FILE)" .json)" && \
	poetry run python3 -m botcpdf.cli_make_many "$(INPUT_FILE)"

clean:
	@find . -type f \( -iname "*.pdf" -o -iname "*.html" \) -exec rm -vf {} \;

POETRY=poetry
POETRY_OK:=$(shell command -v $(POETRY) 2> /dev/null)
PYSRC=botcpdf
MAKE_PDF=bin/make-pdf --format sample

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

test: install-dev
	@$(POETRY) run poetry run py.test -v botcpdf/tests/


# some quick helpers to (quickly) generate some pdfs
script-tb: TARGET:="Trouble Brewing"
script-nrb: TARGET:="No Roles Barred"
script-gmv: TARGET:="Grind My Viz"
script-cs: TARGET:="Clean Sweep"

script-tb script-nrb script-gmv script-cs: poetry
	$(MAKE_PDF) scripts/$(TARGET).json
ifeq ($(shell uname),Darwin)
	@open -a Preview "pdfs/just-baked.pdf"
endif

script-gmv-variations: TARGET:="Grind My Viz"

script-gmv-variations: poetry
# open the most recently generated pdf
	$(MAKE_PDF) scripts/$(TARGET).json
	open-pdf-to-page pdfs/just-baked.pdf 2
# bog standard options ("sample")
	$(MAKE_PDF) scripts/$(TARGET).json --format regular
	open-pdf-to-page pdfs/just-baked.pdf 2
# go for an easyprint layout, no other changes
# should look pretty much like "sample"
	$(MAKE_PDF) scripts/$(TARGET).json --format easyprint
	open-pdf-to-page pdfs/just-baked.pdf 2
# go for an easyprint layout, but with a non-sample village size
	$(MAKE_PDF) scripts/$(TARGET).json --format easyprint --village-size ravenswood_regular
	open-pdf-to-page pdfs/just-baked.pdf 2
# go for an easyprint layout, but with a non-sample village size, show the night order to players
	$(MAKE_PDF) scripts/$(TARGET).json --format easyprint --village-size ravenswood_regular --player-night-order
	open-pdf-to-page pdfs/just-baked.pdf 2

# this is slightly different to the above, in that it generates a pdf for each
# file in the scripts directory
all-scripts: install-dev
	@find scripts -type f -name '*.json' -exec bin/make-pdf {} --village-size sample \;

# needs bundling into a script, or botcpdf.cli
variations-newchars: poetry
	@time $(MAKE) variations INPUT_FILE="scripts/Grind My Viz.json"
ifeq ($(shell uname),Darwin)
	@open -a Preview "pdfs/just-baked.pdf"
endif

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

fetch-combined-json:
	@curl --silent --create-dirs -o data/imported/roles-combined.json https://raw.githubusercontent.com/chizmw/json-on-the-clocktower/main/data/generated/roles-combined.json

grab-some-scripts:
# make certain we have a scripts directory
	@mkdir -p scripts

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
# 34 Jinxes - a script with a lot of jinxes (nometa)
	@curl -Ls -o 'scripts/34 Jinxes.json' https://botc-scripts.azurewebsites.net/script/544/1.0.0/download

docker-test: grab-some-scripts
	@$(eval CONTAINER := "test$(shell date +%s)")
	@$(eval IMAGE := "hello-world:latest")
	@docker build -t $(IMAGE) .
	@docker run -d -v ~/.aws-lambda-rie:/aws-lambda -p 9000:8080 --entrypoint /aws-lambda/aws-lambda-rie --name $(CONTAINER) $(IMAGE) /usr/local/bin/python -m awslambdaric botcpdf.lambda.render
	@sleep 3
	@curl -s -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '@scripts/No Roles Barred.json' -O
	@echo
	docker logs $(CONTAINER)
	@docker stop $(CONTAINER) >/dev/null || true
	@docker rm $(CONTAINER) >/dev/null || true

prerelease: poetry
	@git commit -m "$$(poetry version prerelease)" pyproject.toml
	poetry install


preminor: poetry
	@git commit -m "$$(poetry version preminor)" pyproject.toml
	poetry install
