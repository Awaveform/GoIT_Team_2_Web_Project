from typing import Type

from sqlalchemy.orm import Session, Query

from src.database.models.rate import Rate


async def _filter_by(query: Query[Type[Rate]], **kw) -> Query[Type[Rate]]:
    """
    Filters a query for Rate objects based on provided criteria.
    Filtering criteria can be provided either as single values or as lists of values.

    :param query: The query object to be filtered.
    :type query: Query[Type[Rate]]
    :param **kw: Filtering criteria.
    :type **kw: dict
    :return: The filtered query.
    :rtype: Query[Type[Rate]]
    """
    filter_by_data = {
        "id": kw.get("id"),
        "photo_id": kw.get("photo_id"),
        "created_by": kw.get("created_by")
    }

    for key, value in filter_by_data.items():
        if value is not None:
            if type(value) is list:
                query = query.filter(getattr(Rate, key).in_(value))
            else:
                query = query.filter(getattr(Rate, key) == value)

    return query


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
    query = db.query(Rate)
    rates = await _filter_by(query=query, **kw)
    return rates.all()


async def delete_rates(rates_id: list[int], db: Session) -> None:
    """
    Deletes rates from the database by their IDs.

    :param rates_id: List of rate IDs to be deleted.
    :type rates_id: list[int]
    :param db: The database session object.
    :type db: Session
    """
    db.query(Rate).filter(Rate.id.in_(rates_id)).delete(synchronize_session=False)
    db.commit()
