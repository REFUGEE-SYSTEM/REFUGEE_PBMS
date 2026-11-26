from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class G2PRegisterRefugeeGroup(G2PRegistry):
    __tablename__ = "g2p_register_refugee_group"

    # Base Registry Fields
    functional_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_internal_record_id: Mapped[str] = mapped_column(String, nullable=True)
    record_name: Mapped[str] = mapped_column(String, nullable=True)
    record_status: Mapped[str] = mapped_column(String, nullable=True)
    record_status_reason: Mapped[str] = mapped_column(String, nullable=True)

    # [F01] Household Head
    head_of_household_internal_record_id: Mapped[str] = mapped_column(String, nullable=True)
    household_head_name: Mapped[str] = mapped_column(String, nullable=True)

    # [F03] Household Size
    household_size: Mapped[int] = mapped_column(Integer, nullable=True)

    # [F04] Dependency Ratio
    dependency_ratio: Mapped[float] = mapped_column(Float, nullable=True)

    # [F05] Female Headed Household
    female_headed_household: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # [F06] Child Headed Household
    child_headed_household: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Location
    latitude: Mapped[str] = mapped_column(String, nullable=True)
    longitude: Mapped[str] = mapped_column(String, nullable=True)
    address_line_1: Mapped[str] = mapped_column(String, nullable=True)
    address_line_2: Mapped[str] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
