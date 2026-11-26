from typing import Optional

from .registry import G2PRegistryPayload


class G2PRefugeeIndividualRegistryPayload(G2PRegistryPayload):
    functional_record_id: Optional[str] = None
    surname: Optional[str] = None
    given_names: Optional[str] = None
    sex: Optional[str] = None
    date_of_birth: Optional[str] = None
    date_of_birth_estimated: Optional[bool] = None
    age: Optional[int] = None
    place_of_birth: Optional[str] = None
    country_of_origin: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    record_status: Optional[str] = None
