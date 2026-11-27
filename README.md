# SentinelMesh — Distributed Cyber Threat Intelligence & Incident Response

A deadline-friendly, defensive cybersecurity demonstration platform. It ingests simulated security logs, detects suspicious patterns, enriches source IPs with a local IOC database, and creates incidents asynchronously.

> **Important:** This is an educational prototype, not a production SOC/SIEM. It uses synthetic events and a local threat-intelligence dataset. Do not expose it to the public internet or treat its scores as proof of compromise.

## Architecture and core principle

**Core principle:** loose coupling through independent service ownership and event-driven communication.

1. **Principle:** Each service owns its data and communicates through explicit APIs or durable events.
2. **Domain relevance:** Security monitoring must continue ingesting and processing events even when an enrichment or response component is temporarily unavailable.
3. **Implementation:** four FastAPI services, four isolated PostgreSQL databases, RabbitMQ events, REST enrichment, NGINX API gateway, and Kubernetes DNS.
4. **Demonstration:** stop Threat Intelligence; Detection's circuit breaker opens and marks enrichment as unavailable/unknown; separately delete an Ingestion pod and observe its Deployment replace it.

## Services

| Service | Single responsibility | Store | Key API |
|---|---|---|---|
| Log Ingestion | Validate, normalize and persist incoming security events; publish `LogReceived` | `ingestion_db` | `POST /api/logs`, `GET /api/logs`, `/health` |
| Threat Detection | Consume logs, apply deterministic rules, score risk, enrich IPs, publish `ThreatDetected` | `detection_db` | `GET /api/threats`, `/health` |
| Threat Intelligence | Return local IOC reputation/category for an IP | `intelligence_db` | `GET /api/intelligence/ip/{ip}`, `/health` |
| Incident Management | Consume detections and manage incident status | `incident_db` | `GET /api/incidents`, `PATCH /api/incidents/{id}/status`, `/health` |

## Communication

| From → To | Style | Sync? | Reason | Failure behavior |
|---|---|---|---|---|
| Dashboard → NGINX → APIs | REST | Sync | User needs immediate response | Gateway returns service error; retry manually |
| Ingestion → Detection | RabbitMQ `LogReceived` | Async | Detection can scale independently of ingestion | Durable queue retains messages while consumer is unavailable; publisher confirms are not enabled in this prototype |
| Detection → Intelligence | REST + circuit breaker | Sync | Risk calculation needs reputation now | 2 s HTTP timeout; after 3 failures breaker opens; fallback is `unknown`, never “safe” |
| Detection → Incident | RabbitMQ `ThreatDetected` | Async | Incident creation should not block detection | Durable queue; consumer acknowledges after processing; see limitations below |

## Architecture components

- **API Gateway:** NGINX reverse proxy; browser uses one origin.
- **Message Queue:** RabbitMQ durable topic exchange and durable queues.
- **Circuit Breaker:** PyBreaker in Detection; 3 failures, 10 s reset; HTTP timeout 2 s.
- **Service discovery:** Kubernetes DNS service names (for example `intelligence:8000`), not pod IPs.

## Quick start (Docker Compose)

Prerequisites: Docker Engine/Desktop with Compose v2; ports 8080 and 15672 available.

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8080` for the dashboard and `http://localhost:15672` for RabbitMQ management (`sentinel` / `sentinel-local` in local development only). API contracts and endpoint paths are documented in this README; FastAPI generates interactive `/docs` pages inside each service container.

Submit a sample event:

```bash
curl -X POST http://localhost:8080/api/logs \
  -H 'Content-Type: application/json' \
  -d '{"source_ip":"198.51.100.23","username":"admin","event_type":"login_failed","message":"failed login","timestamp":"2026-11-16T10:00:00Z"}'
```

`198.51.100.23` is a documentation/test IP; the local IOC seed includes it as a simulated malicious source. Generate at least five failed logins from the same source within ten minutes to trigger the brute-force rule.

Useful endpoints:

```bash
curl http://localhost:8080/api/logs
curl http://localhost:8080/api/threats
curl http://localhost:8080/api/incidents
curl http://localhost:8080/health
```

## Local development / tests

Each service is independently runnable with Python 3.12 and its own `.env` values. For the integrated stack, Compose is the supported path.

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

The test suite validates rule scoring and API contract helpers without requiring live infrastructure. Integration behavior must additionally be verified with Compose.

## Docker image registry

Set `DOCKERHUB_USER` in your shell and run:

```bash
export DOCKERHUB_USER=your-dockerhub-username
./scripts/push-images.sh 1.0.0
./scripts/set-k8s-images.sh "$DOCKERHUB_USER" 1.0.0
```

The script builds and pushes all four backend images, the frontend image and the NGINX gateway image using explicit version tags. The second script updates the Kubernetes manifests to the same Docker Hub namespace and tag. PostgreSQL and RabbitMQ use pinned public upstream images; the NGINX gateway is built and pushed as a project image. Never use `latest` for submitted manifests.

## Kubernetes

Prerequisites: a running cluster, `kubectl`, and an image registry namespace you control. Update image names/tags and credentials first.

```bash
kubectl apply -k k8s/
kubectl get pods -w
```

Port-forward the gateway:

```bash
kubectl port-forward svc/gateway 8080:80
```

The manifests include four application Deployments/Services, a frontend and gateway, four PostgreSQL StatefulSets with PVC templates, RabbitMQ, ConfigMap, Secret, resource requests/limits, and liveness/readiness probes. Ingestion has two replicas for the self-healing demonstration. For a real cluster, replace the example Secret values and use a managed secret solution / TLS.

## Required failure demonstrations

### Circuit breaker

1. Start Compose and confirm normal enrichment: `curl http://localhost:8080/api/intelligence/ip/198.51.100.23`.
2. Stop Intelligence: `docker compose stop intelligence`.
3. Submit events or query a new detection flow repeatedly. The HTTP call times out/fails; after three failures the breaker opens. Detection stores a threat with `enrichment_status=unavailable` and `reputation=unknown` rather than incorrectly treating the IP as benign.
4. Check `GET /api/threats` and service logs for `circuit_open` / fallback details.
5. Restart Intelligence: `docker compose start intelligence`; wait more than 10 seconds and trigger another event. Verify the breaker permits a probe and enrichment recovers.

Threshold: 3 consecutive failures. HTTP timeout: 2 seconds. Reset timeout: 10 seconds. PyBreaker manages state; HTTPX enforces the request timeout.

### Kubernetes self-healing

```bash
kubectl get pods -w
kubectl get pods -l app=ingestion
kubectl delete pod <one-ingestion-pod-name>
kubectl get pods -l app=ingestion -w
```

Show that the deleted pod is replaced and two replicas return to Ready. Keep sending `POST /api/logs` requests through the gateway during the replacement and show successful responses. A Deployment owns a ReplicaSet; the ReplicaSet continuously reconciles actual pod count to the desired replica count. The Service routes to ready pods, so the surviving replica can continue receiving traffic during replacement.

**Evidence:** capture screenshots or a short screen recording with terminal commands and timestamps visible. Do not claim the demo passed until you have run it on your machine.

## Before / after Docker comparison (record actual times)

| Aspect | Without Docker | With Docker |
|---|---|---|
| Setup | Install Python, PostgreSQL, RabbitMQ and NGINX manually | Compose starts pinned service images and dependencies |
| Dependencies | Runtime / package versions may differ | Each image carries its runtime and dependencies |
| Start order | Start DB/broker before services manually | Compose health checks and `depends_on: service_healthy` |
| Consistency | Machine-specific setup; “works on my machine” risk | Same tagged images can be used in Compose and Kubernetes |
| Steps and time | Record your own steps and elapsed minutes | Record `docker compose up --build` elapsed time |

Do not fabricate the time values. Add measured results to your report after the run.

## Repository map

```text
services/              four independent FastAPI services
gateway/                NGINX API gateway Dockerfile
shared/                small shared DB and RabbitMQ helpers
frontend/               React dashboard
nginx/                  API gateway configuration
k8s/                    Kubernetes manifests (Kustomize)
scripts/                registry, image-tag and demo helpers
docs/                   report outline, architecture decisions, evidence checklist
 tests/                 unit tests
```

## Known prototype limitations to disclose

- RabbitMQ consumer delivery is at-least-once in intent, but the prototype does not implement a complete transactional outbox, deduplication key, retry policy, or dead-letter queue. For production, add those before claiming guaranteed exactly-once processing.
- Ingestion persists the event before publishing. If RabbitMQ is down, the API response indicates publication failure; the event remains stored but is not automatically replayed.
- The local IOC list is seeded synthetic data; there is no external threat feed.
- Demo credentials are intentionally simple and must be changed before any shared deployment.
- Dashboard is a compact operational view, not an authentication-hardened production console.
