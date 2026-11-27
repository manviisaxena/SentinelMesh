#!/usr/bin/env bash
set -euo pipefail
kubectl get pods -l app=ingestion -w
# In a second terminal: kubectl delete pod <one-pod-name>
# Keep posting through the gateway while the ReplicaSet creates the replacement.
