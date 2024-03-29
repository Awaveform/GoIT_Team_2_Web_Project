from typing import Type

from sqlalchemy.orm import Session

from src.database.models import Rate


async def create_rate_photo(
    photo_id: int,
    grade: int,
    user_id: int,
    db: Session
) -> Rate:
    """
    Creates a new rate for a photo.

    :param photo_id: The identifier of the photo for which the rate is created.
    :type photo_id: int
    :param grade: The rate given to the photo.
    :type grade: RateModel
    :param user_id: The identifier of the user creating the rate.
    :type user_id: int
    :param db: The database session object.
    :type db: Session
    :return: The newly created Rate object.
    :rtype: Rate
    """
    new_rate = Rate(
        grade=grade,
        photo_id=photo_id,
        created_by=user_id
    )
    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)
    return new_rate


async def get_rates(db: Session, **kw) -> list[Type[Rate]]:
    """
    Retrieves rates based on provided filters.

    :param db: The database session object.
    :type db: Session
    :param **kw: Filtering criteria.
    :type **kw: dict
    :return: List of filtered rates.
    :rtype: list[Type[Rate]]
    """
    rates = db.query(Rate)
    
    try:
        for key, value in kw.items():
            if value:
                rates = rates.filter(getattr(Rate, key) == value)
    except AttributeError:
        pass
    
    return rates.all()
