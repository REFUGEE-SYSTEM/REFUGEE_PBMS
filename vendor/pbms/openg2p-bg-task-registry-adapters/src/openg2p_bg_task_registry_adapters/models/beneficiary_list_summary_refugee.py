from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import JSON
from sqlalchemy.orm import mapped_column


class BeneficiaryListSummaryRefugee(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_refugee"

    entitlement_amount_q1 = mapped_column(JSON, nullable=True)
    entitlement_amount_q2 = mapped_column(JSON, nullable=True)
    entitlement_amount_q3 = mapped_column(JSON, nullable=True)
    entitlement_units = mapped_column(JSON, nullable=True)
