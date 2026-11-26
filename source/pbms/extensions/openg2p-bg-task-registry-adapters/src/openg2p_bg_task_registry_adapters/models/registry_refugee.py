from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import JSON, Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class G2PRefugeeRegistry(G2PRegistry):
    __tablename__ = "g2p_refugee"

    # Base Registry Fields
    functional_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_internal_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_foundational_id: Mapped[str] = mapped_column(String, nullable=True)
    record_status: Mapped[str] = mapped_column(String, nullable=True)
    record_status_reason: Mapped[str] = mapped_column(String, nullable=True)

    # [B01] Surname / Family Name
    surname: Mapped[str] = mapped_column(String, nullable=True)

    # [B02] Given Name(s)
    given_names: Mapped[str] = mapped_column(String, nullable=True)

    # [B04] Sex
    sex: Mapped[str] = mapped_column(String, nullable=True)

    # [B05] Date of Birth
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=True)

    # [B06] Date of Birth Estimated
    date_of_birth_estimated: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    # [B07] Place of Birth
    place_of_birth: Mapped[str] = mapped_column(String, nullable=True)

    # [B08] Country of Origin
    country_of_origin: Mapped[str] = mapped_column(String, nullable=True)
    country_of_origin_code: Mapped[str] = mapped_column(String, nullable=True)

    # [B09] Nationality / Citizenship
    nationality: Mapped[str] = mapped_column(String, nullable=True)

    # [B10] Marital Status
    marital_status: Mapped[str] = mapped_column(String, nullable=True)

    # [B11] Preferred Languages
    preferred_languages: Mapped[list] = mapped_column(JSON, nullable=True)
    preferred_languages_display: Mapped[str] = mapped_column(String, nullable=True)

    # Computed age
    age: Mapped[int] = mapped_column(Integer, nullable=True)

    # Household & Location Fields
    case_number: Mapped[str] = mapped_column(String, nullable=True)
    is_head_of_household: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    household_size: Mapped[int] = mapped_column(Integer, nullable=True, default=1)
    relationship_to_head: Mapped[str] = mapped_column(String, nullable=True)
    host_district: Mapped[str] = mapped_column(String, nullable=True)
    settlement_name: Mapped[str] = mapped_column(String, nullable=True)
    zone_cluster: Mapped[str] = mapped_column(String, nullable=True)
    village_block: Mapped[str] = mapped_column(String, nullable=True)
    plot_number: Mapped[str] = mapped_column(String, nullable=True)
