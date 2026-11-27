# python:3.12-slim: same pinned runtime as the other services ensures the pika
# RabbitMQ consumer and psycopg PostgreSQL client use identical wheel builds.
# Runs as unprivileged appuser (UID 10001); no root process in the container.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
# Copy requirements before source so this layer is cached when only app code changes.
COPY services/incident/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared ./shared
COPY services/incident/app ./app
USER appuser
EXPOSE 8004
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
