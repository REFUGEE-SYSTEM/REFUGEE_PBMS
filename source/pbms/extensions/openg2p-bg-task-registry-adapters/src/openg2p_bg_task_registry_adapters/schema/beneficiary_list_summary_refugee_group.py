from typing import Optional

from pydantic import BaseModel

from .beneficiary_list_summary import BeneficiaryListSummaryPayload


class BeneficiaryListSummaryRefugeeGroup(BaseModel):
    household_size_mean: Optional[str] = None
    household_size_q3: Optional[str] = None
    household_size_q2: Optional[str] = None
    household_size_q1: Optional[str] = None
    dependency_ratio_mean: Optional[str] = None
    entitlement_amount_q3: Optional[dict] = None
    entitlement_amount_q2: Optional[dict] = None
    entitlement_amount_q1: Optional[dict] = None


class BeneficiaryListSummaryRefugeeGroupPayload(BeneficiaryListSummaryPayload):
    registry_summary: BeneficiaryListSummaryRefugeeGroup
