
# Docker base-image and build-strategy justification

The four backend services each have their own Dockerfile and use `python:3.12-slim`.

- **Log Ingestion:** the slim Debian-based Python image supplies the supported Python runtime and standard-library networking needed by FastAPI, psycopg and pika without bundling a full development toolchain.
- **Threat Detection:** the same pinned Python minor version keeps behavior consistent for FastAPI, HTTPX and PyBreaker. A Debian slim base is less likely than Alpine to require compiling native wheels for database/network dependencies.
- **Threat Intelligence:** the image is intentionally identical in base/runtime to the other APIs, but installs only its declared service requirements; this reduces environment drift while preserving independent build and deployment.
- **Incident Management:** the slim Python image provides the same runtime and wheel compatibility for the RabbitMQ consumer and PostgreSQL client. The container runs as an unprivileged `appuser`.

Each backend Dockerfile installs pinned dependencies before copying source so Docker can cache the dependency layer when application code changes. It runs as UID 10001, exposes only its service port, and starts Uvicorn as the container process. The frontend uses a multi-stage build: `node:22-alpine` compiles the React/Vite app, then `nginx:1.27-alpine` serves only the static build artifacts. This avoids shipping Node and development dependencies in the runtime image.

Infrastructure images use explicit version tags in Compose and Kubernetes (`postgres:16-alpine`, `rabbitmq:3.13-management-alpine`, `nginx:1.27-alpine`). For a production submission, pin images by digest as well.


The **API gateway** uses `nginx:1.27-alpine` as its runtime base. Its Dockerfile copies the reviewed reverse-proxy configuration into the image, so the exact gateway configuration is versioned and promoted as the `sentinelmesh-gateway` image instead of relying on a host bind mount in Kubernetes.
