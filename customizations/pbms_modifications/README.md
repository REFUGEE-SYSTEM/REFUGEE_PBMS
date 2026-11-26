# PBMS Source Modifications (DEF-03)

## Modified File

- **Target Path:** `source/pbms/core/openg2p-bg-task-celery-workers/src/openg2p_bg_task_celery_workers/tasks/beneficiary_list_worker.py`
- **Modified Function:** `construct_disbursement_sql_query(pbms_session, bg_task_session, beneficiary_list)`
- **Corresponding Test File:** `source/pbms/core/openg2p-bg-task-celery-workers/tests/test_beneficiary_list_worker.py`

## Original Problem & Root Cause

In upstream PBMS `3.1.0`, `construct_disbursement_sql_query()` initialized `registrant_details_list = None` and only queried `BeneficiaryListDetails.registrant_details` if `latest_approved_final_enrollment_beneficiary_list_id` was truthy. When a disbursement beneficiary list was processed for a programme that had no `APPROVED_FINAL_ENROLMENT` beneficiary list, `registrant_details_list` remained `None`, causing `for registrant_details in registrant_details_list:` to crash with an uncontrolled `TypeError: 'NoneType' object is not iterable`.

## Implemented Correction

In `construct_disbursement_sql_query()` (lines 239–260):

1. Added an explicit prerequisite check immediately after resolving `latest_approved_final_enrollment_beneficiary_list_id`:
   ```python
   if not latest_approved_final_enrollment_beneficiary_list_id:
       raise ValueError(
           f"Cannot generate disbursement list {beneficiary_list.id}: "
           f"no approved final enrollment list exists for program {beneficiary_list.program_id}."
       )
   ```
2. Executed the `bg_task_session` query for `registrant_details_list` unconditionally after the guard.
3. Guarded the loop with `for registrant_details in registrant_details_list or []:`.

## Test Coverage

`source/pbms/core/openg2p-bg-task-celery-workers/tests/test_beneficiary_list_worker.py` contains 4 unit/regression tests in `TestConstructDisbursementSqlQuery`:

1. `test_a_missing_approved_final_enrollment_list_raises_value_error` — Verifies `ValueError` is raised with `beneficiary_list.id` and `program_id`, and neither `bg_task_session.execute` nor `construct_priority_query` is called.
2. `test_b_approved_final_enrollment_list_exists_processes_registrants` — Verifies valid approved final enrollment JSON extracts registrant IDs (`SYN-IND-001`, `SYN-IND-002`) and passes them to `construct_priority_query`.
3. `test_c_empty_registrant_details_no_none_iteration_error` — Verifies empty `registrant_details_list` (`[]`) completes without `TypeError`.
4. `test_d_worker_failure_handler_records_controlled_exception` — Verifies `beneficiary_list_worker(999)` catches `ValueError`, rolls back `pbms_session` and `bg_task_session`, increments `eligibility_number_of_attempts` to `1`, records the error message in `eligibility_latest_error_code`, sets status to `pending`, and re-raises `ValueError`.

**Latest Observed Execution:** `Ran 4 tests in 0.021s — OK` via `/Users/apple/refugee_management/venv/bin/python -m unittest discover -s /Users/apple/refugee_management/source/pbms/core/openg2p-bg-task-celery-workers/tests -v`.

## Remaining Limitations

1. **Mocked Test Harness:** `celery`, `openg2p_pbms_models`, and `openg2p_bg_task_registry_adapters` are stubbed in `test_beneficiary_list_worker.py`; live Celery worker daemon execution against PostgreSQL/Redis was **not tested**.
2. **Retry Handling Unchanged:** `beneficiary_list_worker()` catches all `Exception` subclasses uniformly and retries up to `_config.worker_max_attempts` via Celery Beat. Missing approved enrollment prerequisites will still be retried until `worker_max_attempts` is exhausted.
