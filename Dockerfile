### IMPORTANT!
# we can not use the usual lambda/python image because there's no sane way to
# install the version of pango we need for weasyprint
#
# huge thanks to this page for the solution used here:
# - https://www.slim.ai/blog/containerized-lambda-in-python-language/
# notes about pango and weasyprint:
# - https://github.com/kotify/cloud-print-utils/pull/7/files
# - https://github.com/Kozea/WeasyPrint/issues/1384#issuecomment-902620644

ARG FUNCTION_DIR="/function"
FROM python:3.10-bullseye as build-image
RUN apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        g++=4\* \
        make=4\* \
        cmake=3.\* \
        unzip=6\* \
        libcurl4-openssl-dev=7\* \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip~=23.1 \
 && pip3 install --no-cache-dir poetry~=1.4 \
 && poetry config virtualenvs.in-project true

ARG FUNCTION_DIR
RUN mkdir -p ${FUNCTION_DIR}

WORKDIR /src
COPY README.md ./
COPY pyproject.toml ./
COPY botcpdf ./botcpdf/

# install our deps into the function dir
RUN poetry export -f requirements.txt --output requirements.txt \
 &&  pip3 install --no-cache-dir --target "${FUNCTION_DIR}" -r requirements.txt \
 &&  pip3 install --no-cache-dir --target "${FUNCTION_DIR}" awslambdaric==2.0.4

# we didn't install ourself yet
RUN poetry build \
 && pip3 install --no-cache-dir --no-deps dist/*.whl --target "${FUNCTION_DIR}"

FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpango1.0-dev=1.46.\* \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}

COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENV APP_VERSION=1.0.0

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "botcpdf.lambda.render" ]

#COPY app.py ./
COPY data ./data/
COPY templates ./templates/
COPY icons ./icons/

RUN touch /opt/disable-extensions-jwigqn8j
