# python:3.12-slim: pinned minor version keeps PyBreaker, HTTPX and psycopg behaviour
# consistent with the other services. Slim Debian base avoids the native-wheel
# compilation that alpine would require for the binary database and HTTP dependencies.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
# Copy requirements before source so this layer is cached when only app code changes.
COPY services/detection/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared ./shared
COPY services/detection/app ./app
USER appuser
EXPOSE 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
