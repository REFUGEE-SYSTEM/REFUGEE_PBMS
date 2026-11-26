from datetime import date
from typing import Optional

from .registry import G2PRegistryPayload


class G2PRegisterRefugeePayload(G2PRegistryPayload):
    functional_record_id: Optional[str] = None
    foundational_id: Optional[str] = None
    record_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None
    country_of_origin: Optional[str] = None
    legal_status: Optional[str] = None
    presence_status: Optional[str] = None
    record_status: Optional[str] = None
    arrival_date: Optional[date] = None
    address_line_1: Optional[str] = None
    country_code: Optional[str] = None
