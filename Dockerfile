FROM python:3.11

RUN pip3 install --no-cache-dir poetry==1.4.2
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN poetry config virtualenvs.create false

WORKDIR /app

COPY Makefile ./
COPY fonts ./fonts/
COPY gameinfo ./gameinfo/
COPY icons ./icons/
COPY templates ./templates/

COPY pyproject.toml ./

COPY README.md ./
COPY botcpdf ./botcpdf/

RUN poetry install --only main
