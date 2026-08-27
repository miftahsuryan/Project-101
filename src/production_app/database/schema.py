import psycopg


def ensure_asset_table(database_url: str) -> None:
    """Create the temporary D07 asset table when it does not exist."""
    with psycopg.connect(
        database_url,
        connect_timeout=5,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS assets (
                    id UUID PRIMARY KEY,
                    asset_code VARCHAR(100) NOT NULL UNIQUE,
                    name VARCHAR(200) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT assets_asset_code_not_blank
                        CHECK (BTRIM(asset_code) <> ''),
                    CONSTRAINT assets_name_not_blank
                        CHECK (BTRIM(name) <> '')
                )
                """
            )
