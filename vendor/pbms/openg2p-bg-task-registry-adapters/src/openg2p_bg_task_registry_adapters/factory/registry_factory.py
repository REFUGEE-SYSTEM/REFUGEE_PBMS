from ..computations import RegisterHousehold, RegisterRefugee, RegistryFarmer
from ..interface import RegistryInterface
from ..models import G2PRegistryType


class RegistryFactory:
    @staticmethod
    def get_registry_class(target_registry: str) -> RegistryInterface:
        if target_registry == G2PRegistryType.FARMER.value:
            return RegistryFarmer()
        elif target_registry == G2PRegistryType.HOUSEHOLDS.value:
            return RegisterHousehold()
        elif target_registry == G2PRegistryType.REFUGEES.value:
            return RegisterRefugee()
        else:
            raise ValueError(f"Unsupported registry type: {target_registry}")
