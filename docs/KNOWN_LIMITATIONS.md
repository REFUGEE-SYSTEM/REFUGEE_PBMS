# Known Limitations

1. **No Keycloak OIDC**: PBMS Odoo uses native Odoo authentication (`admin` / Odoo users) and `pbms-staff-api` runs with `STAFF_PORTAL_API_AUTH_ENABLED=false` for local/demo isolation.
2. **No G2P Bridge / SPAR**: Entitlements are computed and stored inside PBMS (`pbmsdb` / `bgtaskdb`), but disbursement envelopes and payouts via G2P Bridge / SPAR are not included in this standalone stack.
3. **Read-Only Registry Access**: `pbms_reader` must be granted explicitly via `./scripts/grant-registry-readonly.sh` before running an enrollment cycle against `refugee_registry_db`.
