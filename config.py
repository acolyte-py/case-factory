import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager, closing
from dotenv import load_dotenv

from models import Base


load_dotenv()

IP = os.getenv("IP")
PORT = os.getenv("PORT")
USER = os.getenv("USER")
PASSWD = os.getenv("PASSWD")
NAME_DB = os.getenv("NAME")

JWT_TOKEN = os.getenv("TOKEN")
HEADERS = {"Authorization": f"Bearer {JWT_TOKEN}", "Content-Type": "application/json"}

SQLALCHEMY_DATABASE_URL = f'postgresql://{USER}:{PASSWD}@{IP}:{PORT}/{NAME_DB}'
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_timeout=10)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autoflush=False, bind=engine)


@contextmanager
def _get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        with closing(db):
            pass
