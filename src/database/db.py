from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.conf.config import settings


engine = create_engine(settings.sqlalchemy_database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db() -> Session:
    """
    Method to generate the DB session.

    :return: Db session object
    :rtype: Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
