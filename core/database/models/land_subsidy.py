from sqlalchemy import Column, String

from .._base import Base


class LandSubsidy(Base):
    __tablename__ = "land_subsidy"

    id = Column(String, primary_key=True)
    person_id = Column(String, default="")
    id_card = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    subsidy_year = Column(String, default="")
    certified_area = Column(String, default="")
    subsidy_area = Column(String, default="")
    base_standard = Column(String, default="")
    rape_area = Column(String, default="")
    rape_amount = Column(String, default="")
    total_amount = Column(String, default="")
    import_time = Column(String, default="")
