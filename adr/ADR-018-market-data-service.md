# ADR-018: Market Data Service v1 (Coinbase Advanced Trade)

**Status**: Proposed  
**Date**: 2025-07-05  
**Deciders**: TRAIDER Core Engineering Leads (Quant Infra, Backend, SRE)  
**Technical Story**: Phase-1 MVP requirement – real-time Coinbase market data ingestion (see [docs/phases/phase-1-mvp.md](../phases/phase-1-mvp.md#market-data-integration))

---

## Context

### Background
- Phase 0 delivered an institutional-grade foundation but no live market data.  
- Phase 1 KPI: P95 ≤ 500 ms signal-to-order, requires <150 ms end-to-end tick ingestion.  
- Coinbase Advanced Trade offers WebSocket channels (`ticker`, `level2`) needed for BTC-USD & ETH-USD.  
- Data must be **validated**, **persisted** (TimescaleDB) and **fanned-out** to downstream feature-gen & dashboard services.  
- Stakeholders: Alpha Team (strategy dev), Risk Engine, Frontend Dashboard, SRE (monitoring).

### Technical Context
- Backend is FastAPI (async) with SQLAlchemy + TimescaleDB.  
- ADR-016 defines microservice split; we are still monolith in Phase 1 but want clear service boundaries.  
- Latency budget: <50 ms ingestion → validation, <20 ms DB write, <80 ms broadcast.  
- Timescale hypertable partitioning required for 2 assets @ 1 Hz avg tick.  
- Operational: connection drop/reconnect, auth token rotation, exponential back-off.

---

## Decision

### Chosen Solution
- **Dedicated async task** inside backend `services/market_data_service` (monolith for now).  
- Use `websockets` + `aiohttp` fallback for Coinbase WS connection.  
- Parse JSON, validate schema (Pydantic `TickerMessage`).  
- Persist raw ticks to Timescale hypertable `market_data` partitioned by day.  
- Publish tick via `asyncio.Queue` to:  
  1. Feature Engine workers  
  2. Socket.IO broadcaster for dashboard  
- Observability: record
  - `market_data.ws_latency_ms` (receive lag)  
  - `market_data.write_latency_ms`  
  - `market_data.dropped_msgs_total`
  Exposed via Prometheus & OTEL traces.
- Resilience:
  - Auto-reconnect with jittered exponential back-off (max 60 s).  
  - Circuit-breaker trips after 5 consecutive failures → alerts.
- Config via ENV (`COINBASE_WS_URL`, `COINBASE_PRODUCTS` list).

### Alternative Solutions Considered
1. **External Go service** – superior perf, but premature micro-service split; Phase 1 stays Python.  
2. **Kafka ingestion first** – adds infra complexity; will adopt in Phase 2.  
3. **REST polling** – violates latency budget.

---

## Consequences

### Positive
- Fast path to live ticks; minimal new infra.  
- Clear handler boundaries enable later extraction into microservice.  
- Metrics & tracing baked in from day 1.  

### Negative
- Python WS loop limits raw throughput (~10 k msg/s) – acceptable for 2 assets but will require refactor in Phase 2.  
- Tight coupling to monolith until extraction.  

### Risks & Mitigation
- **WS throttling / disconnection** → implement heartbeat & back-off.  
- **Schema changes by Coinbase** → versioned Pydantic models + alert on parse failure.  
- **DB write amplification** → batch inserts in 100 ms windows.

---

## Implementation

### Action Items
- [ ] Scaffold `backend/services/market_data/websocket_client.py` with connection & message handler (Owner: @backend-engineer-1)  
- [ ] Create Pydantic models `TickerMessage`, `Level2Message` (Owner: @backend-engineer-1)  
- [ ] Timescale hypertable migration `market_data` (Owner: @db-eng)  
- [ ] Prometheus metric registration & OTEL spans (Owner: @sre)  
- [ ] Integration tests with recorded WS fixtures (Owner: @qa)  
- [ ] Update `docs/architecture/market_data_service.md` (Owner: @tech-writer)

### Timeline
- **Week 1**: Scaffold & local integration tests  
- **Week 2**: DB migration, observability hooks, e2e test  
- **Week 3**: Run 24 h endurance test & ADR review  

### Success Criteria
- WS client uptime ≥99 % over 24 h test  
- Ingestion latency P95 <50 ms  
- 0 data validation errors in 24 h  
- Dashboard receives ≥99 % of ticks  

---

## Monitoring & Review
- Metrics: `market_data.ws_latency_ms`, `market_data.write_latency_ms`, `market_data.dropped_msgs_total`  
- Review Schedule: **30 days** post-deploy, then quarterly.

---

## Related Decisions

- Relates to [ADR-016: Market-Data Microservice Extraction](ADR-016-market-data-microservice.md)

---

## References
- Coinbase Advanced Trade WS docs  
- TimescaleDB hypertable best practices  
- Google SRE golden signals 