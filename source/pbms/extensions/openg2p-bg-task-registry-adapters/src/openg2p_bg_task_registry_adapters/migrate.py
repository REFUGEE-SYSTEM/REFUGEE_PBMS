from .models import (
    BeneficiaryListSummaryFarmer,
    BeneficiaryListSummaryHousehold,
    BeneficiaryListSummaryRefugeeGroup,
    BeneficiaryListSummaryRefugeeIndividual,
)


def get_models():
    return [
        BeneficiaryListSummaryFarmer,
        BeneficiaryListSummaryHousehold,
        BeneficiaryListSummaryRefugeeIndividual,
        BeneficiaryListSummaryRefugeeGroup,
    ]
