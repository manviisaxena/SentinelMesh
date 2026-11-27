# 10–12 minute presentation outline

1. **Problem and objective (1 min):** why a small SOC pipeline benefits from separated ingestion, detection, intelligence and incident response. State that all events and IOCs are synthetic.
2. **Architecture (2 min):** walk through the diagram; identify the four services and their independent PostgreSQL stores.
3. **Core principle (1 min):** loose coupling through service ownership and event-driven communication; explain RabbitMQ events versus synchronous REST enrichment.
4. **Architecture components (1 min):** NGINX gateway, RabbitMQ, PyBreaker and Kubernetes DNS.
5. **Docker (1 min):** four backend Dockerfiles, frontend multi-stage build, Compose health ordering, volumes and versioned images. Show actual startup time.
6. **Kubernetes (1 min):** Deployments, Services, ConfigMap, Secret, probes, resources and PVCs.
7. **Circuit-breaker demo (1.5 min):** normal enrichment, stop Intelligence, show open state / unknown fallback, restart and show recovery.
8. **Self-healing demo (1 min):** delete one Ingestion pod, watch replacement, show requests still succeeding through the remaining replica.
9. **Conclusion and limitations (0.5 min):** summarize loose coupling and disclose synthetic IOC data, no production authentication/TLS, and the missing transactional outbox / DLQ.

Keep a recorded backup of both failure demos in case live infrastructure fails. Reserve remaining time for questions.
