#!/usr/bin/env bash
set -euo pipefail
TAG="${1:-1.0.0}"
: "${DOCKERHUB_USER:?Set DOCKERHUB_USER to your Docker Hub username}"
for svc in ingestion detection intelligence incident; do
  image="$DOCKERHUB_USER/sentinelmesh-$svc:$TAG"
  docker build -f "services/$svc/Dockerfile" -t "$image" .
  docker push "$image"
done

frontend_image="$DOCKERHUB_USER/sentinelmesh-frontend:$TAG"
docker build -t "$frontend_image" ./frontend
docker push "$frontend_image"

gateway_image="$DOCKERHUB_USER/sentinelmesh-gateway:$TAG"
docker build -f gateway/Dockerfile -t "$gateway_image" .
docker push "$gateway_image"
