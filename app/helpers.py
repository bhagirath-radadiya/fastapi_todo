from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def safe_commit(db: Session):
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
