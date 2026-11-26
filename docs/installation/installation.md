# Installation Guide — Refugee Management Standalone Project

## 1. Prerequisites Check

Before beginning installation, verify system requirements and port availability:
```bash
cd ~/refugee_management
make check
```

The script will confirm that Docker, Git, Python 3, and all proposed ports (`8169`, `5543`, `6389`, `8150`, etc.) are free.

---

## 2. Environment Configuration

Copy the example environment configuration:
```bash
cp .env.example .env
```
Edit `.env` to configure your preferred database credentials and service endpoints.

---

## 3. Installation Roadmap (Gates 4 through 6)

The standalone project installation follows an approval-gated roadmap:

1. **Gate 4 (Source Migration)**:
   - Self-contained copies of `odoo17`, `pbms`, `openg2p-odoo-commons`, and `g2p_registry_addon` will be populated into `source/` and `extensions/`.
2. **Gate 5 (Infrastructure Provisioning)**:
   - Standalone Docker Compose (`deployment/docker-compose.yml`) will be created and launched on dedicated ports (`5543`, `6389`, etc.).
3. **Gate 6 (Database & Application Installation)**:
   - New database `refugee_management_db` will be initialized.
   - Odoo modules and Refugee Registry extensions will be loaded and verified.

---

## 4. Verifying Coexistence

During all phases of installation:
- The legacy PBMS at `http://localhost:8069` must remain accessible and unchanged.
- The new Refugee Management instance will be available at `http://localhost:8169`.
