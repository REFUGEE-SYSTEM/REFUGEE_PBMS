from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column


class G2PRegisterRefugee(G2PRegistry):
    __tablename__ = "g2p_register_refugees"

    functional_record_id: Mapped[str] = mapped_column(String, nullable=True)
    foundational_id: Mapped[str] = mapped_column(String, nullable=True)
    record_name: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    middle_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=True)
    nationality: Mapped[str] = mapped_column(String, nullable=True)
    country_of_origin: Mapped[str] = mapped_column(String, nullable=True)
    legal_status: Mapped[str] = mapped_column(String, nullable=True)
    presence_status: Mapped[str] = mapped_column(String, nullable=True)
    record_status: Mapped[str] = mapped_column(String, nullable=True)
    arrival_date: Mapped[Date] = mapped_column(Date, nullable=True)
    address_line_1: Mapped[str] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
