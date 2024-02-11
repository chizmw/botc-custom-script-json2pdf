FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.11 AS base

RUN pip3 install --no-cache poetry

WORKDIR /opt/extensions
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy function code
COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --output requirements.txt \
    && pip3 install --verbose --no-cache -r requirements.txt \
    && rm requirements.txt

COPY botcpdf botcpdf
COPY templates templates
COPY data data
COPY README.md README.md

RUN poetry build --verbose
RUN pip3 install --verbose --no-cache dist/botc_json2pdf-*.tar.gz

FROM base AS test

RUN yum install -y \
    libffi \
    libffi-devel \
    cairo \
    pango \
    glibc

CMD [ "botcpdf.demolambda.render" ]


FROM base AS runtime

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "botcpdf.demolambda.render" ]
