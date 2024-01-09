ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION} as builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

COPY . .

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install \
        --upgrade \
        pip \
        poetry \
        setuptools \
        wheel

RUN --mount=type=cache,mode=0755,target=/root/.cache/pypoetry \
    poetry install \
        --without dev \
        --no-root

##################
# runtime
##################

FROM python:${PYTHON_VERSION} as runtime

ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends libcairo2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app /app

# Run the container unprivileged
RUN mkdir static && \
    addgroup www && \
    useradd --home-dir /app --gid www www  && \
    chown -R www:www /app
USER www

EXPOSE 8000

# Increase the timeout since these PDFs take a long time to generate
CMD ["gunicorn", "--timeout", "120", "--bind", ":8000", "--workers", "2", "config.wsgi"]
