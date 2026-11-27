#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE_URL:-http://localhost:8080}"
echo '1) Check intelligence health:'
curl -fsS "$BASE/api/intelligence/ip/198.51.100.23" || true
echo '\n2) Stop intelligence in another terminal: docker compose stop intelligence'
echo '3) Submit enough failed logins to cause detection enrichment failures:'
for n in 1 2 3 4 5; do
  curl -sS -X POST "$BASE/api/logs" -H 'Content-Type: application/json' \
    -d '{"source_ip":"198.51.100.23","username":"admin","event_type":"login_failed","message":"breaker demo"}'
  echo
  sleep 1
done
echo '4) Inspect: curl -sS "$BASE/api/threats"'
echo '5) Restart: docker compose start intelligence; wait 11 seconds; send another event.'
