from openg2p_bg_task_models.errors import BGTaskErrorCodes, BGTaskException

from ..computations import (
    RegisterHousehold,
    RegisterRefugeeGroup,
    RegistryFarmer,
    RegistryRefugeeIndividual,
)
from ..interface import RegistryInterface
from ..models import G2PRegistryType


class RegistryFactory:
    """Get the appropriate summary computation class based on the registrant type"""

    @staticmethod
    def get_registry_class(
        target_registry,
    ) -> RegistryInterface:
        if target_registry == G2PRegistryType.FARMER.value:
            return RegistryFarmer()
        elif target_registry == G2PRegistryType.HOUSEHOLDS.value:
            return RegisterHousehold()
        elif target_registry == G2PRegistryType.REFUGEE_INDIVIDUAL.value:
            return RegistryRefugeeIndividual()
        elif target_registry == G2PRegistryType.REFUGEE_GROUP.value:
            return RegisterRefugeeGroup()
        else:
            raise BGTaskException(code=BGTaskErrorCodes.INVALID_REQUEST)
