# Patch Management Guide

## Classification of Customizations

1. **Patches to Original OpenG2P / PBMS Source:**
   - `customizations/patches/def03_beneficiary_list_worker.patch` -> targets `source/pbms/core/openg2p-bg-task-celery-workers/src/openg2p_bg_task_celery_workers/tasks/beneficiary_list_worker.py` (OpenG2P PBMS `3.1.0`, baseline `4c0173a1d5e2`).
2. **Independently Developed / Extension Addon:**
   - `extensions/g2p_registry_addon/` (Odoo 17 addon, version `3.1.1`) — deployed via Odoo `addons_path` precedence rather than source patching.
3. **Odoo 17 Core:**
   - No patches required (`source/odoo17/` is unmodified).

## Git Baseline Note

In this standalone repository (`refugee-pbms-standalone`), commit `ed54ddd7` (Gate 3) contained only the project skeleton, and commit `d4b679d5` added `source/pbms/` with the DEF-03 fix already applied. Consequently, `git diff ed54ddd7..d4b679d5` reports `beneficiary_list_worker.py` as newly added (`A`). The unified diff in `customizations/patches/def03_beneficiary_list_worker.patch` isolates the exact DEF-03 hunk against the upstream PBMS `3.1.0` `construct_disbursement_sql_query()` logic.

## Reviewing the Patch

```bash
cat customizations/patches/def03_beneficiary_list_worker.patch
```

## Applying Safely (Dry-Run First)

> [!IMPORTANT]
> Do **not** apply this patch to the current working tree if `d4b679d5` is already checked out, as the fix is already present. Use this procedure when integrating into a clean upstream PBMS `3.1.0` (`4c0173a1d5e2`) environment.

From the target repository root:

```bash
git apply --check customizations/patches/def03_beneficiary_list_worker.patch
git apply customizations/patches/def03_beneficiary_list_worker.patch
```

## Verifying After Applying

```bash
python3 -m py_compile source/pbms/core/openg2p-bg-task-celery-workers/src/openg2p_bg_task_celery_workers/tasks/beneficiary_list_worker.py
python3 -m unittest discover -s source/pbms/core/openg2p-bg-task-celery-workers/tests -v
```

## Reverting Safely

To test or revert the patch cleanly from a patched tree:

```bash
git apply --reverse --check customizations/patches/def03_beneficiary_list_worker.patch
git apply --reverse customizations/patches/def03_beneficiary_list_worker.patch
```
