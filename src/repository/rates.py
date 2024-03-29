from typing import Type

from sqlalchemy.orm import Session, Query

from src.database.models import Rate


async def _filter_by(query: Query[Type[Rate]], **kw) -> Query[Type[Rate]]:
    """
    Filters a query for Rate objects based on provided criteria.

    :param query: The query object to be filtered.
    :type query: Query[Type[Rate]]
    :param **kw: Filtering criteria.
    :type **kw: dict
    :return: The filtered query.
    :rtype: Query[Type[Rate]]
    """
    filter_by_data = {
        "id": kw.get("id"),
        "grade": kw.get("grade"),
        "created_at": kw.get("created_at"),
        "updated_at": kw.get("updated_at"),
        "photo_id": kw.get("photo_id"),
        "created_by": kw.get("created_by")
    }

    for key, value in filter_by_data.items():
        if value is not None:
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
