# pull official base image
FROM python:3.13.2-slim-bullseye AS python-base


ENV APP_HOME=/home/python_user

WORKDIR $APP_HOME

ENV TZ 'America/Denver'
RUN echo $TZ > /etc/timezone && apt-get update && \
    apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME=$APP_HOME/poetry
ENV POETRY_VENV=$APP_HOME/poetry-venv

# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=$APP_HOME/.poetry-cache

# install container needeed packages
RUN apt-get update && apt-get install tree

# Upgrade pip
RUN pip install --upgrade pip

FROM python-base AS poetry-base

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv $POETRY_VENV \
	&& $POETRY_VENV/bin/pip install -U pip setuptools \
	&& $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Create a new stage from the base python image
FROM python-base AS example-app-base

# Copy Poetry to django_core image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

# copy dependency
COPY ./pyproject.toml ./README.md $APP_HOME

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

RUN apt-get update && apt-get install -y \
    libpq-dev gcc build-essential python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN poetry lock && poetry export -f requirements.txt --without-hashes > requirements.txt
RUN pip install --timeout=120 -r requirements.txt
# Install Dependencies
# RUN poetry install --no-interaction --no-cache
RUN poetry install --no-interaction --no-cache --no-root
RUN poetry run playwright install --with-deps chromium 


FROM example-app-base AS example-app-final

COPY src/ $APP_HOME/src/
COPY .env $APP_HOME/.env
