from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import mapped_column


class BeneficiaryListSummaryRefugeeIndividual(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_refugee_individual"

    age_q1 = mapped_column(Float, nullable=True, default=0)
    age_q2 = mapped_column(Float, nullable=True, default=0)
    age_q3 = mapped_column(Float, nullable=True, default=0)
    age_mean = mapped_column(Float, nullable=True, default=0)
    age_units = mapped_column(String, nullable=False, default="years")

    entitlement_amount_q1 = mapped_column(JSON, nullable=True)
    entitlement_amount_q2 = mapped_column(JSON, nullable=True)
    entitlement_amount_q3 = mapped_column(JSON, nullable=True)
    entitlement_units = mapped_column(JSON, nullable=True)
