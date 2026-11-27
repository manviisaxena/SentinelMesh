# Evidence checklist — capture after actually running the project

- [ ] Compose startup showing `docker compose up --build` and all containers healthy.
- [ ] Dashboard with events, threats and incidents populated.
- [ ] Four service `/health` endpoints.
- [ ] RabbitMQ management page showing durable queues / message flow.
- [ ] Threat Intelligence healthy, then stopped; detection logs show circuit opening and unknown fallback.
- [ ] Threat Intelligence restarted; breaker recovers after reset window.
- [ ] Docker Hub repository pages showing version-tagged images.
- [ ] `kubectl get pods -o wide` showing all workloads Ready.
- [ ] `kubectl delete pod ...` followed by replacement pod and requests continuing.
- [ ] Actual before/after deployment time measurements.
- [ ] API request/response screenshots with sensitive credentials hidden.
