FROM python:3.11.9-slim


WORKDIR /app

COPY poetry.lock pyproject.toml /

RUN pip install --upgrade pip && \
    pip install poetry

COPY . .

RUN poetry install --without dev --no-root --no-cache


COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]