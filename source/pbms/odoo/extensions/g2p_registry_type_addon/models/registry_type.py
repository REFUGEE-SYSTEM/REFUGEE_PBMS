from enum import Enum
from odoo import models, fields


class G2PTargetModelMapping:

    MODEL_MAPPING = {
        "refugee": "g2p.refugee",
        "farmer": "g2p.register.farmer",
        "households": "g2p.register.households",
        "refugee_individual": "g2p.register.refugee_individual",
        "refugee_group": "g2p.register.refugee_group",
    }

    @classmethod
    def get_target_model_name(cls, key):
        return cls.MODEL_MAPPING.get(key)


class G2PRegistryType(Enum):
    REFUGEE = "refugee"
    FARMER = "farmer"
    HOUSEHOLDS = "households"
    REFUGEE_INDIVIDUAL = "refugee_individual"
    REFUGEE_GROUP = "refugee_group"

    @classmethod
    def selection(cls):
        return [("refugee", "Refugee Registry")]
