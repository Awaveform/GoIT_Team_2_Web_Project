from typing import Type

from sqlalchemy.orm import Session

from src.database.models import Rate
from src.schemas import RateModel


async def create_rate_photo(
    photo_id: int,
    grade: RateModel,
    user_id: int,
    db: Session
) -> Type[Rate]:
    """
    """
    
    new_rate = Rate(
        grade = grade,
        photo_id = photo_id,
        created_by = user_id
    )
    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)
    return new_rate


async def get_rates(db: Session, **kw) -> list[Type[Rate]]:
    """
    """
    rates = db.query(Rate)
    
    try:
        for key, value in kw.items():
            if value:
                rates = rates.filter(getattr(Rate, key) == value)
    except AttributeError:
        pass
    
    return rates.all()
