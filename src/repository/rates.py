from typing import Type

from sqlalchemy.orm import Session

from src.database.models import Rate


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
