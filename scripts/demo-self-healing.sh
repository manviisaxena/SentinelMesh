#!/usr/bin/env bash
# Self-healing demonstration.
# Terminal 1: run this script (watches pods and fires continuous POST requests).
# Terminal 2: kubectl delete pod <one-ingestion-pod-name>
set -euo pipefail
BASE="${BASE_URL:-http://localhost:8080}"

echo "=== Current ingestion pods ==="
kubectl get pods -l app=ingestion

echo ""
echo "=== Starting continuous POST requests in background ==="
echo "    (requests will keep succeeding via the surviving replica)"
(
  n=0
  while true; do
    n=$((n+1))
    status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/logs" \
      -H 'Content-Type: application/json' \
      -d "{\"source_ip\":\"10.0.0.1\",\"username\":\"demo\",\"event_type\":\"login_failed\",\"message\":\"self-healing test $n\"}")
    echo "$(date +%H:%M:%S)  POST /api/logs → HTTP $status  (request #$n)"
    sleep 1
  done
) &
CURL_PID=$!
trap "kill $CURL_PID 2>/dev/null; exit" INT TERM EXIT

echo ""
echo "=== Watching pods — delete one now in another terminal: ==="
echo "    kubectl delete pod \$(kubectl get pods -l app=ingestion -o jsonpath='{.items[0].metadata.name}')"
echo ""
kubectl get pods -l app=ingestion -w
