# python:3.12-slim: Debian-based slim image provides the exact Python minor version
# needed by FastAPI, psycopg and pika without bundling a compiler or dev headers.
# Chosen over alpine because psycopg[binary] ships a pre-built wheel for Debian glibc;
# alpine would require compiling from source, adding build time and image size.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
# Copy requirements before source so this layer is cached when only app code changes.
COPY services/ingestion/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared ./shared
COPY services/ingestion/app ./app
USER appuser
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
