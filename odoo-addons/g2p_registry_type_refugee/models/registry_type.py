from enum import Enum

from odoo.addons.g2p_registry_type_addon import models as g2p_registry_type_models
from odoo.addons.g2p_registry_type_addon.models import registry_type as base_rt


class G2PRegistryType(Enum):
    FARMER = "farmer"
    HOUSEHOLDS = "households"
    REFUGEES = "refugees"

    @classmethod
    def selection(cls):
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]


base_rt.G2PTargetModelMapping.MODEL_MAPPING["refugees"] = "g2p.register.refugees"
base_rt.G2PRegistryType = G2PRegistryType
g2p_registry_type_models.G2PRegistryType = G2PRegistryType
