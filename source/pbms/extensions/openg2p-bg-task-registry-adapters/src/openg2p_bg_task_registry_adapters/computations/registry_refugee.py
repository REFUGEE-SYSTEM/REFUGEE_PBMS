import logging
from typing import List
from sqlalchemy.orm import Session

from ..models import G2PRefugeeRegistry
from .registry_refugee_individual import RegistryRefugeeIndividual

_logger = logging.getLogger("app")


class RegistryRefugee(RegistryRefugeeIndividual):
    """Fetches unified refugee data and computes summary statistics"""

    def get_registrants_by_ids(
        self, registrant_ids, sr_session
    ) -> List[G2PRefugeeRegistry]:
        registrants = sr_session.query(G2PRefugeeRegistry).filter(
            G2PRefugeeRegistry.internal_record_id.in_(registrant_ids)
        )
        return list(registrants.yield_per(500))

    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        sql_query_with_registrant_id = (
            self.construct_get_is_registrant_entitled_sql_query(
                registrant_id, "refugee", sql_query
            )
        )
        result = sr_session.execute(sql_query_with_registrant_id).fetchone()
        return result is not None

    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        if not multiplier or multiplier == "none":
            return 1

        sql_query = self.construct_multiplier_sql_query(
            multiplier, target_registry="refugee"
        )
        params = {"registrant_id": registrant_id}
        result = sr_session.execute(sql_query, params).fetchone()
        return int(result[0]) if result and result[0] is not None else 1
