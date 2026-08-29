from collections.abc import Callable, Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

type SessionFactory = sessionmaker[Session]


def create_database_engine(
    database_url: str,
) -> Engine:
    url = make_url(database_url)
    sqlalchemy_url = url.set(drivername="postgresql+psycopg")

    return create_engine(
        sqlalchemy_url,
        pool_pre_ping=True,
    )


def create_session_factory(
    engine: Engine,
) -> SessionFactory:
    return sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )


def create_session_dependency(
    session_factory: SessionFactory,
) -> Callable[[], Generator[Session, None, None]]:
    def get_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    return get_session
