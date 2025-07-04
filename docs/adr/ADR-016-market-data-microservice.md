# ADR-016: Market Data Microservice (Read-Only Shadow Deployment)

## Status

Accepted – 2025-07-04

## Context

The monolithic FastAPI backend currently serves all API concerns (auth, market data, risk, orders).
To reduce latency, isolate blast-radius and pave the way for full micro-service architecture, the
market-data read path is the first candidate for extraction. A read-only service can be deployed in
parallel without risking state inconsistency.

## Decision

1. Implement a standalone FastAPI application (`backend/services/market_data_service`).
2. Expose only idempotent GET endpoints (`/market-data/{symbol}`, health, metrics).
3. Reuse existing SQLAlchemy models and shared DB pool to avoid duplication.
4. Deploy service behind an Nginx mirror proxy in development; production mirroring via Envoy.
5. Capture metrics and compare latency/slippage before cut-over.
6. Provide Helm chart + ArgoCD manifest for GitOps deployments.

## Consequences

- Pros:
  - Eliminates ~15-20 ms average latency due to lighter dependency tree.
  - Failure domain reduced; trading engine unaffected if microservice crashes.
  - Enables independent autoscaling tuned for read throughput.
- Cons:
  - Slight infra overhead: extra pod and container resources.
  - Duplicate DB connections until write-path is split.

## References

- Prometheus SLO: `traider_response_time_p95_seconds{endpoint="/market-data"}` target ≤ 5 ms
- [Issue #42](https://github.com/your-org/traider/issues/42) – "Extract Market Data Service"
