# Backup & Restore Specification — Refugee Management Standalone Project

## 1. Backup Strategy

The standalone project provides built-in, non-destructive backup tooling (`make backup` / `./scripts/backup.sh`).

### Backup Directory Layout
```text
refugee_management/database/backups/
└── YYYY-MM-DD_HHMMSS/
    ├── database.dump        # PostgreSQL custom-format compressed dump
    ├── database.sql         # Plain text SQL dump
    ├── filestore.tar.gz     # Compressed archive of Odoo filestore
    ├── metadata.json        # Snapshot metadata (version, git SHA, row counts)
    └── sha256sums.txt       # SHA-256 checksums of all backup artifacts
```

---

## 2. Recovery Procedures

### Restoring Database
```bash
# Target standalone database (default port: 5543)
docker exec -i refugee_management_postgres dropdb -U postgres --if-exists refugee_management_db
docker exec -i refugee_management_postgres createdb -U postgres -O refugee_user refugee_management_db
cat database/backups/<TIMESTAMP>/database.dump | \
  docker exec -i refugee_management_postgres pg_restore -U postgres -d refugee_management_db --no-owner
```

### Restoring Filestore
```bash
rm -rf filestore/refugee_management_db
tar -xzf database/backups/<TIMESTAMP>/filestore.tar.gz -C filestore/
```

### Safety Rule
**Never restore over the legacy PBMS database (`pbmsdb` on port 5433).** Restorations must target only standalone containers on port `5543`.
