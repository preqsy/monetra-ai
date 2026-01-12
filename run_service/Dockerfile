FROM python:3.11.9-slim

WORKDIR /app

COPY poetry.lock pyproject.toml /
RUN pip install --upgrade pip && pip install poetry

COPY . .
RUN poetry install --no-root

CMD ["poetry", "run", "python", "run_service/run.py"]
