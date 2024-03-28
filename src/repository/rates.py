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


async def delete_rates(rates: list[Type[Rate]], db: Session) -> None:
    """
    Deletes a list of rates from the database.

    :param rates: The list of rate objects to be deleted.
    :type rates: list[Type[Rate]]
    :param db: The database session object.
    :type db: Session
    """
    for rate in rates:
        db.delete(rate)
        db.commit()
