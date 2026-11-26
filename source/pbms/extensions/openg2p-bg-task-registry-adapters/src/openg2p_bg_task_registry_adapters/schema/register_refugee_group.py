from typing import Optional

from .registry import G2PRegistryPayload


class G2PRegisterRefugeeGroupPayload(G2PRegistryPayload):
    functional_record_id: Optional[str] = None
    household_head_name: Optional[str] = None
    household_size: Optional[int] = None
    dependency_ratio: Optional[float] = None
    female_headed_household: Optional[bool] = None
    child_headed_household: Optional[bool] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    country_code: Optional[str] = None
    record_status: Optional[str] = None
