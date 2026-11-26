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
    BeneficiaryListSummaryRefugeeGroup as BeneficiaryListSummaryRefugeeGroupModel,
)
from ..models import G2PRegisterRefugeeGroup
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryRefugeeGroup,
    BeneficiaryListSummaryRefugeeGroupPayload,
    G2PRegisterRefugeeGroupPayload,
)

_logger = logging.getLogger("app")


class RegisterRefugeeGroup(RegistryInterface):
    """Fetches refugee group/household data and computes summary statistics"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryRefugeeGroupPayload:
        result = await bg_task_session.execute(
            select(BeneficiaryListSummaryRefugeeGroupModel).where(
                BeneficiaryListSummaryRefugeeGroupModel.beneficiary_list_id
                == beneficiary_list_id
            )
        )
        summary_row = result.scalars().first()
        return self._build_summary_payload(summary_row)

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryRefugeeGroupPayload:
        summary_row = (
            bg_task_session.query(BeneficiaryListSummaryRefugeeGroupModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )
        return self._build_summary_payload(summary_row)

    def _build_summary_payload(
        self, row
    ) -> BeneficiaryListSummaryRefugeeGroupPayload:
        def fmt(value, units):
            return f"{value} {units}" if value is not None else None

        if not row:
            return None

        return BeneficiaryListSummaryRefugeeGroupPayload(
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
            registry_summary=BeneficiaryListSummaryRefugeeGroup(
                household_size_mean=fmt(row.household_size_mean, row.household_size_units),
                household_size_q1=fmt(row.household_size_q1, row.household_size_units),
                household_size_q2=fmt(row.household_size_q2, row.household_size_units),
                household_size_q3=fmt(row.household_size_q3, row.household_size_units),
                dependency_ratio_mean=fmt(row.dependency_ratio_mean, row.dependency_ratio_units),
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

        (
            search_sql_query,
            search_params,
        ) = self.construct_beneficiary_search_sql_query(
            registrant_ids,
            target_registry,
            search_query,
            order_by,
            page_size,
            page,
        )

        search_results = (
            (await sr_session.execute(search_sql_query, search_params))
            .mappings()
            .all()
        )

        total_beneficiary_count: int = await self._get_total_beneficiary_count(
            sr_session, beneficiary_list_id, registrant_ids, search_query
        )

        beneficiaries = []
        if search_results:
            beneficiaries = [
                G2PRegisterRefugeeGroupPayload(
                    internal_record_id=row.get("internal_record_id"),
                    functional_record_id=row.get("functional_record_id"),
                    household_head_name=row.get("household_head_name"),
                    household_size=row.get("household_size"),
                    dependency_ratio=row.get("dependency_ratio"),
                    female_headed_household=row.get("female_headed_household"),
                    child_headed_household=row.get("child_headed_household"),
                    address_line_1=row.get("address_line_1"),
                    address_line_2=row.get("address_line_2"),
                    country_code=row.get("country_code"),
                    record_status=row.get("record_status"),
                )
                for row in search_results
            ]

        response_payload = BeneficiarySearchResponsePayload(
            beneficiary_count=len(beneficiaries),
            beneficiaries=beneficiaries,
        )

        return response_payload, total_beneficiary_count

    @cache(expire=120, key_builder=beneficiary_count_key_builder)
    async def _get_total_beneficiary_count(
        self,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        registrant_ids: List[str],
        search_query: str,
    ) -> int:
        (
            count_query,
            count_params,
        ) = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, "refugee_group", search_query
        )
        total_count = (
            await sr_session.execute(count_query, count_params)
        ).scalar_one()
        return total_count

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
        summary = BeneficiaryListSummaryRefugeeGroupModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )

        sizes: List[int] = []
        ratios: List[float] = []

        for detail in beneficiary_list_details:
            registrant_ids = [
                RegistrantDetails(**d).registrant_id for d in detail.registrant_details
            ]
            registrants = self.get_registrants_by_ids(registrant_ids, sr_session)
            for reg in registrants:
                if reg.household_size is not None:
                    sizes.append(reg.household_size)
                if reg.dependency_ratio is not None:
                    ratios.append(float(reg.dependency_ratio))

        self._apply_quartiles(summary, "household_size", sizes)
        if ratios:
            summary.dependency_ratio_mean = round(float(np.mean(ratios)), 2)

        bg_task_session.add(summary)

    @staticmethod
    def _apply_quartiles(summary_obj, prefix: str, values: List[float]) -> None:
        if not values:
            return
        arr = np.array(values)
        setattr(summary_obj, f"{prefix}_mean", round(float(np.mean(arr)), 2))
        setattr(
            summary_obj,
            f"{prefix}_q1",
            round(float(np.percentile(arr, 25, method="midpoint")), 2),
        )
        setattr(
            summary_obj,
            f"{prefix}_q2",
            round(float(np.percentile(arr, 50, method="midpoint")), 2),
        )
        setattr(
            summary_obj,
            f"{prefix}_q3",
            round(float(np.percentile(arr, 75, method="midpoint")), 2),
        )

    def get_registrants_by_ids(
        self, registrant_ids, sr_session
    ) -> List[G2PRegisterRefugeeGroup]:
        groups = sr_session.query(G2PRegisterRefugeeGroup).filter(
            G2PRegisterRefugeeGroup.internal_record_id.in_(registrant_ids)
        )
        return list(groups.yield_per(500))

    # =================================
    # Entitlement Celery Worker Methods
    # =================================
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        sql_query_with_registrant_id = (
            self.construct_get_is_registrant_entitled_sql_query(
                registrant_id, "refugee_group", sql_query
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
            multiplier, target_registry="refugee_group"
        )
        params = {"registrant_id": registrant_id}
        result = sr_session.execute(sql_query, params).fetchone()
        return int(result[0]) if result and result[0] is not None else 1

    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        beneficiary_list_details = (
            bg_task_session.query(BeneficiaryListDetails)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .all()
        )

        entitlements: Dict[Any, List[float]] = {}
        for detail in beneficiary_list_details:
            for d in detail.registrant_details:
                reg_detail = RegistrantDetails(**d)
                for code_id, val in reg_detail.entitlement.items():
                    entitlements.setdefault(code_id, []).append(val)

        stats = self.compute_stats_dict(entitlements)
        bg_task_session.execute(
            update(BeneficiaryListSummaryRefugeeGroupModel)
            .where(
                BeneficiaryListSummaryRefugeeGroupModel.beneficiary_list_id
                == beneficiary_list_id
            )
            .values(
                total_disbursement_quantity=dict(stats["total"]),
                average_entitlement_per_person=dict(stats["average"]),
                entitlement_amount_q1=dict(stats["q1"]),
                entitlement_amount_q2=dict(stats["q2"]),
                entitlement_amount_q3=dict(stats["q3"]),
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
        for code_id, values in entitlements_dict.items():
            if not values:
                for k in ("average", "q1", "q2", "q3", "total"):
                    stats[k][code_id] = 0.0
            else:
                arr = np.array(values)
                stats["average"][code_id] = round(float(np.mean(arr)), 2)
                stats["q1"][code_id] = round(float(np.percentile(arr, 25, method="midpoint")), 2)
                stats["q2"][code_id] = round(float(np.percentile(arr, 50, method="midpoint")), 2)
                stats["q3"][code_id] = round(float(np.percentile(arr, 75, method="midpoint")), 2)
                stats["total"][code_id] = float(np.sum(arr))
        return stats
