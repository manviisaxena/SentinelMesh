# python:3.12-slim: identical base to other services to prevent environment drift
# while keeping this service independently buildable and deployable. The slim
# variant omits test tools and documentation, reducing the final image surface area.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
# Copy requirements before source so this layer is cached when only app code changes.
COPY services/intelligence/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared ./shared
COPY services/intelligence/app ./app
USER appuser
EXPOSE 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
