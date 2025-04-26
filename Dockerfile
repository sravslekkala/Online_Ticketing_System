# Dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

EXPOSE 5000

CMD ["python", "run.py"]
