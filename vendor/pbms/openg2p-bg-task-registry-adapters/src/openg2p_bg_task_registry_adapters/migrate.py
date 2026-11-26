from .models import (
    BeneficiaryListSummaryFarmer,
    BeneficiaryListSummaryHousehold,
    BeneficiaryListSummaryRefugee,
)


def get_models():
    return [
        BeneficiaryListSummaryFarmer,
        BeneficiaryListSummaryHousehold,
        BeneficiaryListSummaryRefugee,
    ]
