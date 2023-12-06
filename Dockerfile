ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION}

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends git libcairo2 && \
    mkdir -p /code

WORKDIR /code

COPY . .

RUN pip install \
        --no-cache-dir \
        --disable-pip-version-check \
        --upgrade \
        pip \
        pipenv \
        setuptools \
        wheel && \
    pipenv install --deploy --system

RUN python manage.py collectstatic --noinput

# Run the container unprivileged
RUN addgroup www && \
    useradd -g www www && \
    chown -R www:www /code
USER www

# Output information about the build
# These files can be read by the application
RUN git log -n 1 --pretty=format:"%h" > GIT_COMMIT && \
    date -u +'%Y-%m-%dT%H:%M:%SZ' > BUILD_DATE

EXPOSE 8000

# Increase the timeout since these PDFs take a long time to generate
CMD ["gunicorn", "--timeout", "120", "--bind", ":8000", "--workers", "2", "config.wsgi"]
