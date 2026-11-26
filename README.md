# Refugee-PBMS

Standalone OpenG2P Program & Benefit Management System (PBMS on Odoo 17) built as a sibling project to `Refugee-Registry`.

## Quick Start

```bash
./scripts/init-env.sh
./scripts/up.sh
./scripts/smoke-test.sh
```

## Connecting to Refugee-Registry (Read-Only)

Refugee-PBMS reads `g2p_register_refugees` from `refugee_registry_db` via `host.docker.internal:5535` using the least-privilege PostgreSQL role `pbms_reader`.

Grant access once against the running `refugee-registry` stack:

```bash
./scripts/grant-registry-readonly.sh
```

To revoke access:

```bash
./scripts/revoke-registry-readonly.sh
```

## Seeding the Demo Program

```bash
./scripts/seed-demo.sh
```

This idempotently creates the `UG_REF_CBI` program (`target_registry = refugees`), `UGX_CASH` benefit code, eligibility rule (`legal_status = 'RECOGNISED_REFUGEE'`, `record_status = 'ACTIVE'`), and flat `100,000 UGX` entitlement rule in PBMS Odoo.

## Endpoints & Ports

| Service | Host Port | URL |
|---|---|---|
| PBMS Odoo | `8369` | `http://localhost:8369/web/login` |
| PBMS Staff Portal API | `8350` | `http://localhost:8350/docs` |
| PBMS Postgres (`pbmsdb`, `bgtaskdb`) | `5635` | `localhost:5635` |
| PBMS Redis | `6581` | `localhost:6581` |

## Operations

- `./scripts/status.sh` — container status and endpoints
- `./scripts/logs.sh [service]` — tail logs
- `./scripts/down.sh` — stop containers (preserves volumes)
- `./scripts/reset.sh [--yes]` — stop containers and delete `refugee_pbms_*` volumes only
