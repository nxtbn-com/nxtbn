FROM python:3.10-slim-buster


COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    netcat \
 && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -q 'pipenv==2020.11.15' && pipenv install --deploy --system


RUN mkdir /backend
COPY ./ /backend
WORKDIR /backend


RUN chmod +x /backend/scripts/entrypoint.sh
RUN chmod +x /backend/media


CMD ["/backend/scripts/entrypoint.sh"]