import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models.drug import Drug
from app.models.drug_alias import DrugAlias
from app.models.substance import Substance


@pytest.fixture
def db() -> Session:
    """Izolyatsiyalangan in-memory SQLite — faqat normalize_and_match uchun
    kerakli jadvallar (Geography ustunli Pharmacy jadvali SQLite'da
    ishlamaydi, shuning uchun uni yaratmaymiz)."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine, tables=[Substance.__table__, Drug.__table__, DrugAlias.__table__]
    )
    session = Session(engine)

    amoksiklav_substance = Substance(name_inn="Amoxicillin+Clavulanate", name_uz="Amoksitsillin+Klavulanat")
    paracetamol_substance = Substance(name_inn="Paracetamol", name_uz="Paratsetamol")
    session.add_all([amoksiklav_substance, paracetamol_substance])
    session.flush()

    amoksiklav = Drug(
        trade_name="Amoksiklav", substance_id=amoksiklav_substance.id,
        manufacturer="Sandoz", dosage_form="tabletka", dosage_strength="625mg",
        reference_price=42000,
    )
    panadol = Drug(
        trade_name="Panadol", substance_id=paracetamol_substance.id,
        manufacturer="GSK", dosage_form="tabletka", dosage_strength="500mg",
        reference_price=12000,
    )
    session.add_all([amoksiklav, panadol])
    session.flush()

    session.add_all(
        [
            DrugAlias(drug_id=amoksiklav.id, alias_text="Амоксиклав"),
            DrugAlias(drug_id=amoksiklav.id, alias_text="amoxiclav"),
            DrugAlias(drug_id=panadol.id, alias_text="панадол"),
        ]
    )
    session.commit()

    yield session
    session.close()
