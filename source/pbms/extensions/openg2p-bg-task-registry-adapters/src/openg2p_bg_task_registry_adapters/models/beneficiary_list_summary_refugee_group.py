from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import mapped_column


class BeneficiaryListSummaryRefugeeGroup(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_refugee_group"

    household_size_q1 = mapped_column(Float, nullable=True, default=0)
    household_size_q2 = mapped_column(Float, nullable=True, default=0)
    household_size_q3 = mapped_column(Float, nullable=True, default=0)
    household_size_mean = mapped_column(Float, nullable=True, default=0)
    household_size_units = mapped_column(String, nullable=False, default="persons")

    dependency_ratio_mean = mapped_column(Float, nullable=True, default=0)
    dependency_ratio_units = mapped_column(String, nullable=False, default="ratio")

    entitlement_amount_q1 = mapped_column(JSON, nullable=True)
    entitlement_amount_q2 = mapped_column(JSON, nullable=True)
    entitlement_amount_q3 = mapped_column(JSON, nullable=True)
    entitlement_units = mapped_column(JSON, nullable=True)
