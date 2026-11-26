from typing import Optional

from pydantic import BaseModel

from .beneficiary_list_summary import BeneficiaryListSummaryPayload


class BeneficiaryListSummaryRefugeeIndividual(BaseModel):
    age_mean: Optional[str] = None
    age_q3: Optional[str] = None
    age_q2: Optional[str] = None
    age_q1: Optional[str] = None
    entitlement_amount_q3: Optional[dict] = None
    entitlement_amount_q2: Optional[dict] = None
    entitlement_amount_q1: Optional[dict] = None


class BeneficiaryListSummaryRefugeeIndividualPayload(BeneficiaryListSummaryPayload):
    registry_summary: BeneficiaryListSummaryRefugeeIndividual
