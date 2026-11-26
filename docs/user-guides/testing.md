# Testing & Quality Assurance Plan — Refugee Management Standalone Project

The `refugee_management` project mandates strict test verification across seven test disciplines prior to acceptance.

---

## 1. Test Disciplines

### A. Installation Tests (`tests/installation/`)
- Verifies clean startup of PostgreSQL (`:5543`), Redis (`:6389`), and Odoo 17 (`:8169`).
- Verifies HTTP 200 responses on `/web/login` and `/web/health`.
- Verifies database migrations and module loading.

### B. Refugee Registry Tests (`tests/refugee_registry/`)
- Individual refugee record creation, update, and deletion.
- Household / group creation and member assignment.
- Validation of all 100 Refugee Management Data Dictionary Attributes (Categories A–Q).
- Selection field validation, duplicate detection, and sensitive data masking.

### C. Business Logic & Calculations (`tests/refugee_registry/`)
- **F04 Dependency Ratio**:
  - Validates ratio calculation: Dependents (<15 or >=65) / Working-age (15-64).
  - Validates N/A behavior when zero working-age members exist.
  - Validates N/A behavior when no members are enrolled.
- **J01 Washington Group Short Set on Disability**:
  - 6 domains: Vision, Hearing, Mobility, Cognition/Memory, Self-care, Communication.
  - 4 response options per domain: No difficulty, Some difficulty, A lot of difficulty, Cannot do at all.
- **Household Ownership & Head of Household Validation**.

### D. PBMS Integration Tests (`tests/programme/`, `tests/payments/`)
- Program creation and eligibility rule assignment.
- Beneficiary list generation from refugee registry.
- Enrollment cycle progression.
- Entitlement calculations and disbursement cycle generation.

### E. Regression Tests (`tests/pbms_regression/`)
- Verification that existing non-refugee PBMS functionality remains operational.
- Verification that legacy database `pbmsdb` and original PBMS instance at `http://localhost:8069` are unaffected.

### F. Complete Technical Independence Acceptance Test (`tests/independence/`)
- Mandatory Gate 8 criteria:
  1. Start standalone `refugee_management`.
  2. Stop legacy `openg2p-developer` stack.
  3. Verify standalone application remains 100% operational.
  4. Restart standalone project and confirm data persistence.
  5. Verify zero runtime references to `~/openg2p-developer`.
