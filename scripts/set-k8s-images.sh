#!/usr/bin/env bash
set -euo pipefail
USER_NAME="${1:-${DOCKERHUB_USER:-}}"
TAG="${2:-1.0.0}"
if [[ -z "$USER_NAME" ]]; then echo "Usage: $0 <dockerhub-username> [tag]" >&2; exit 2; fi
if [[ ! "$TAG" =~ ^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$ ]]; then echo "Invalid image tag: $TAG" >&2; exit 2; fi
sed -i.bak "s|YOUR_DOCKERHUB_USER|$USER_NAME|g; s|sentinelmesh-ingestion:[^[:space:]]*|sentinelmesh-ingestion:$TAG|g; s|sentinelmesh-detection:[^[:space:]]*|sentinelmesh-detection:$TAG|g; s|sentinelmesh-intelligence:[^[:space:]]*|sentinelmesh-intelligence:$TAG|g; s|sentinelmesh-incident:[^[:space:]]*|sentinelmesh-incident:$TAG|g; s|sentinelmesh-frontend:[^[:space:]]*|sentinelmesh-frontend:$TAG|g; s|sentinelmesh-gateway:[^[:space:]]*|sentinelmesh-gateway:$TAG|g" k8s/applications.yaml k8s/gateway.yaml
rm -f k8s/applications.yaml.bak k8s/gateway.yaml.bak
echo "Updated Kubernetes manifests to $USER_NAME/sentinelmesh-*:$TAG"
