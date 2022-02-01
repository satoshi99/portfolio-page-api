FROM python:3.9 as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    POETRY_VERSION=1.1.12 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

FROM python-base as init

RUN apt update  \
    && apt install -y default-mysql-client \
    && apt install --no-install-recommends -y tzdata  \
    && apt clean \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python \
    && cd /usr/local/bin \
    && ln -s $POETRY_HOME/bin/poetry

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./

FROM init as development

RUN poetry install

FROM init as product-builder

RUN poetry install --no-dev

FROM python-base as production

COPY --from=product-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
