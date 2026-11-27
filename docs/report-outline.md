# SentinelMesh assignment report — fill in measured evidence before submission

Target length: 10–12 pages. This is an outline, not a claim that deployment tests have passed.

1. **Domain and objectives** — defensive SOC workflow; synthetic logs; IOC enrichment; incident triage.
2. **Core principle (four lines)** — use the four-line statement in README.
3. **Architecture diagram** — insert `architecture.mmd` rendered to PNG/PDF; explain service ownership and event flow.
4. **Service table** — reproduce README table and add exact endpoints from OpenAPI `/docs`.
5. **Communication table** — reproduce README communication table and discuss failure behavior.
6. **Architectural components** — NGINX gateway, RabbitMQ, PyBreaker, Kubernetes DNS.
7. **At least three architecture decisions** — use `architecture-decisions.md`.
8. **Docker** — base image rationale: `python:3.12-slim` gives a small Debian-based Python runtime and broad wheel compatibility; non-root user reduces container privilege. Multi-stage frontend uses Node build stage and NGINX runtime stage. Explain Compose health checks and named volumes.
9. **Registry** — add your Docker Hub namespace, pushed image tags, and screenshots. Do not submit placeholders.
10. **Before/after Docker** — fill actual manual setup steps and elapsed minutes; time Compose start with a stopwatch.
11. **Kubernetes** — describe Deployments/Services, ConfigMap/Secret, probes, resources, PVCs, image tags and DNS discovery. Add `kubectl get pods` evidence.
12. **Failure demos** — include circuit-breaker and self-healing screenshots/recording with command and timestamps visible. State observed outcome, not expected outcome.
13. **Conclusion and limitations** — discuss prototype scope, no live threat feeds, no production auth/TLS, no outbox/DLQ.
