from production_app.database.session import (
    create_database_engine,
    create_session_factory,
)

DATABASE_URL = "postgresql://user:password@localhost:5432/app"


def test_create_database_engine_uses_psycopg_driver() -> None:
    engine = create_database_engine(DATABASE_URL)

    try:
        assert engine.url.drivername == "postgresql+psycopg"
        assert engine.dialect.driver == "psycopg"
    finally:
        engine.dispose()


def test_create_session_factory_configures_sessions() -> None:
    engine = create_database_engine(DATABASE_URL)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            assert session.bind is engine
            assert session.autoflush is False
            assert session.expire_on_commit is False
    finally:
        engine.dispose()
