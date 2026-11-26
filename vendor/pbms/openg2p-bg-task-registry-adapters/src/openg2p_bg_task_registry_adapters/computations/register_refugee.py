import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastapi_cache.decorator import cache
from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    RegistrantDetails,
)
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ..cache import beneficiary_count_key_builder
from ..interface import RegistryInterface
from ..models import (
    BeneficiaryListSummaryRefugee as BeneficiaryListSummaryRefugeeModel,
)
from ..models import G2PRegisterRefugee
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryRefugee,
    BeneficiaryListSummaryRefugeePayload,
    G2PRegisterRefugeePayload,
)

_logger = logging.getLogger("app")


class RegisterRefugee(RegistryInterface):
    """Fetches refugee data and computes summary statistics"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryRefugeePayload:
        result = await bg_task_session.execute(
            select(BeneficiaryListSummaryRefugeeModel).where(
                BeneficiaryListSummaryRefugeeModel.beneficiary_list_id
                == beneficiary_list_id
            )
        )
        summary_row = result.scalars().first()
        return self._build_summary_payload(summary_row)

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryRefugeePayload:
        summary_row = (
            bg_task_session.query(BeneficiaryListSummaryRefugeeModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )
        return self._build_summary_payload(summary_row)

    def _build_summary_payload(self, row) -> BeneficiaryListSummaryRefugeePayload:
        return BeneficiaryListSummaryRefugeePayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=row.id,
                program_id=row.program_id,
                program_mnemonic=row.program_mnemonic,
                target_registry=row.target_registry,
                beneficiary_list_id=row.beneficiary_list_id,
                number_of_registrants=row.number_of_registrants,
                date_created=row.date_created,
                total_disbursement_quantity=row.total_disbursement_quantity,
                average_entitlement_per_registrant=row.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryRefugee(
                entitlement_amount_q1=row.entitlement_amount_q1,
                entitlement_amount_q2=row.entitlement_amount_q2,
                entitlement_amount_q3=row.entitlement_amount_q3,
            ),
        )

    # ==============================
    # Beneficiary Search API Methods
    # ==============================
    async def search_beneficiaries(
        self,
        bg_task_session: AsyncSession,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        target_registry: str,
        search_query,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "internal_record_id asc",
    ) -> Tuple[BeneficiarySearchResponsePayload, int]:
        registrant_details_result = await bg_task_session.execute(
            select(BeneficiaryListDetails.registrant_details).where(
                BeneficiaryListDetails.beneficiary_list_id == beneficiary_list_id
            )
        )
        registrant_details = registrant_details_result.scalars().all()
        registrant_ids = []
        for registrant_detail in registrant_details:
            for registrant in registrant_detail:
                registrant_ids.append(registrant["registrant_id"])

        if not registrant_ids:
            return BeneficiarySearchResponsePayload(
                beneficiary_count=0, beneficiaries=[]
            ), 0

        (
            refugee_search_query,
            refugee_search_params,
        ) = self.construct_beneficiary_search_sql_query(
            registrant_ids,
            target_registry,
            search_query,
            order_by,
            page_size,
            page,
        )

        refugee_search_results = (
            (await sr_session.execute(refugee_search_query, refugee_search_params))
            .mappings()
            .all()
        )

        total_beneficiary_count: int = await self._get_total_beneficiary_count(
            sr_session, beneficiary_list_id, registrant_ids, search_query
        )

        beneficiaries = [
            G2PRegisterRefugeePayload(
                internal_record_id=row["internal_record_id"],
                functional_record_id=row["functional_record_id"],
                foundational_id=row["foundational_id"],
                record_name=row["record_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                last_name=row["last_name"],
                gender=row["gender"],
                birth_date=row["birth_date"],
                nationality=row["nationality"],
                country_of_origin=row["country_of_origin"],
                legal_status=row["legal_status"],
                presence_status=row["presence_status"],
                record_status=row["record_status"],
                arrival_date=row["arrival_date"],
                address_line_1=row["address_line_1"],
                country_code=row["country_code"],
            )
            for row in refugee_search_results
        ]

        return (
            BeneficiarySearchResponsePayload(
                beneficiary_count=len(beneficiaries),
                beneficiaries=beneficiaries,
            ),
            total_beneficiary_count,
        )

    @cache(expire=120, key_builder=beneficiary_count_key_builder)
    async def _get_total_beneficiary_count(
        self,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        registrant_ids: List[str],
        search_query: Optional[str] = None,
    ) -> int:
        if not registrant_ids:
            return 0
        (
            beneficiary_count_query,
            beneficiary_count_params,
        ) = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, "refugees", search_query
        )
        return (
            await sr_session.execute(beneficiary_count_query, beneficiary_count_params)
        ).scalar_one()

    # =================================
    # Eligibility Celery Worker Methods
    # =================================
    def compute_eligibility_statistics(
        self,
        beneficiary_list_details: List[BeneficiaryListDetails],
        base_summary,
        sr_session: Session,
        bg_task_session: Session,
    ):
        refugee_summary = BeneficiaryListSummaryRefugeeModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )
        bg_task_session.add(refugee_summary)

    def get_registrants_by_ids(
        self, registrant_ids, sr_session
    ) -> List[G2PRegisterRefugee]:
        if not registrant_ids:
            return []
        refugees = sr_session.query(G2PRegisterRefugee).filter(
            G2PRegisterRefugee.internal_record_id.in_(registrant_ids)
        )
        return list(refugees.yield_per(500))

    # =================================
    # Entitlement Celery Worker Methods
    # =================================
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        sql_query_with_registrant_id = (
            self.construct_get_is_registrant_entitled_sql_query(
                registrant_id, "refugees", sql_query
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
            multiplier, target_registry="refugees"
        )
        params = {"registrant_id": registrant_id}
        result = sr_session.execute(sql_query, params).fetchone()
        multiplier_value: int = (
            int(result[0]) if result and result[0] is not None else 1
        )
        return multiplier_value

    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        beneficiary_list_details = (
            bg_task_session.query(BeneficiaryListDetails)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .all()
        )

        entitlements: Dict[Any, List[float]] = {}

        for beneficiary_list_detail in beneficiary_list_details:
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail = RegistrantDetails(**registrant_detail)
                for benefit_code_id, value in registrant_detail.entitlement.items():
                    entitlements.setdefault(benefit_code_id, []).append(value)

        entitlement_stats = self.compute_stats_dict(entitlements)

        bg_task_session.execute(
            update(BeneficiaryListSummaryRefugeeModel)
            .where(
                BeneficiaryListSummaryRefugeeModel.beneficiary_list_id
                == beneficiary_list_id
            )
            .values(
                total_disbursement_quantity=dict(entitlement_stats["total"]),
                average_entitlement_per_person=dict(entitlement_stats["average"]),
                entitlement_amount_q1=dict(entitlement_stats["q1"]),
                entitlement_amount_q2=dict(entitlement_stats["q2"]),
                entitlement_amount_q3=dict(entitlement_stats["q3"]),
            )
        )

    def compute_stats_dict(
        self, entitlements_dict: Dict[Any, List[float]]
    ) -> Dict[str, Dict[Any, float]]:
        stats: Dict[str, Dict[Any, float]] = {
            "average": {},
            "q1": {},
            "q2": {},
            "q3": {},
            "total": {},
        }
        for benefit_code_id, values in entitlements_dict.items():
            if not values:
                stats["average"][benefit_code_id] = 0.0
                stats["q1"][benefit_code_id] = 0.0
                stats["q2"][benefit_code_id] = 0.0
                stats["q3"][benefit_code_id] = 0.0
                stats["total"][benefit_code_id] = 0.0
            else:
                arr = np.array(values)
                stats["average"][benefit_code_id] = round(float(np.mean(arr)), 2)
                stats["q1"][benefit_code_id] = round(
                    float(np.percentile(arr, 25, method="midpoint")), 2
                )
                stats["q2"][benefit_code_id] = round(
                    float(np.percentile(arr, 50, method="midpoint")), 2
                )
                stats["q3"][benefit_code_id] = round(
                    float(np.percentile(arr, 75, method="midpoint")), 2
                )
                stats["total"][benefit_code_id] = float(np.sum(arr))
        return stats
