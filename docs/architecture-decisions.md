# Architecture decisions (include these in the report)

## AD-1: Database per service
Each microservice has a dedicated PostgreSQL database and credentials/configuration boundary. This prevents shared-table coupling and allows each service to evolve its schema independently. No service reads another service's database; all cross-service information travels through an API or event.

## AD-2: RabbitMQ for workflow events
Ingestion publishes `log.received` and Detection publishes `threat.detected`. Consumers process asynchronously, so ingestion does not need to wait for risk scoring or incident creation. Durable exchanges/queues and manual consumer acknowledgements reduce loss during consumer restarts. The prototype does not yet include an outbox or dead-letter policy; document this limitation.

## AD-3: REST for immediate threat enrichment
Detection needs a reputation response before it calculates the event's final score, so it calls Intelligence synchronously. A 2-second timeout bounds waiting. PyBreaker opens after 3 consecutive failures and resets after 10 seconds. The fallback uses `unknown` enrichment, not a false “clean” verdict.

## AD-4: Kubernetes DNS for discovery
Services address dependencies by stable Kubernetes Service DNS names rather than pod IPs. Deployments may replace pods without requiring callers to learn new addresses.

## AD-5: NGINX as a single entry point
The dashboard calls one origin and NGINX routes API paths to their owning service. This keeps internal service addresses out of browser code and centralizes routing.
