from typing import cast
from uuid import UUID

import psycopg

from production_app.domain.entities import Asset

type AssetRow = tuple[UUID, str, str]


def _to_asset(row: AssetRow | None) -> Asset | None:
    if row is None:
        return None

    asset_id, asset_code, name = row

    return Asset(
        id=asset_id,
        asset_code=asset_code,
        name=name,
    )


class PostgresAssetRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def add(self, asset: Asset) -> None:
        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO assets (
                        id,
                        asset_code,
                        name
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        asset.id,
                        asset.asset_code,
                        asset.name,
                    ),
                )

    def get(self, asset_id: UUID) -> Asset | None:
        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, asset_code, name
                    FROM assets
                    WHERE id = %s
                    """,
                    (asset_id,),
                )
                row = cast(
                    AssetRow | None,
                    cursor.fetchone(),
                )

        return _to_asset(row)

    def get_by_code(
        self,
        asset_code: str,
    ) -> Asset | None:
        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, asset_code, name
                    FROM assets
                    WHERE asset_code = %s
                    """,
                    (asset_code,),
                )
                row = cast(
                    AssetRow | None,
                    cursor.fetchone(),
                )

        return _to_asset(row)

    def list_assets(
        self,
        *,
        asset_code: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Asset]:
        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                if asset_code is None:
                    cursor.execute(
                        """
                        SELECT id, asset_code, name
                        FROM assets
                        ORDER BY created_at, id
                        LIMIT %s
                        OFFSET %s
                        """,
                        (limit, offset),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, asset_code, name
                        FROM assets
                        WHERE asset_code = %s
                        ORDER BY created_at, id
                        LIMIT %s
                        OFFSET %s
                        """,
                        (
                            asset_code,
                            limit,
                            offset,
                        ),
                    )

                rows = cast(
                    list[AssetRow],
                    cursor.fetchall(),
                )

        return [asset for row in rows if (asset := _to_asset(row)) is not None]

    def replace(self, asset: Asset) -> None:
        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE assets
                    SET
                        asset_code = %s,
                        name = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (
                        asset.asset_code,
                        asset.name,
                        asset.id,
                    ),
                )

    def delete(self, asset_id: UUID) -> None:
        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM assets
                    WHERE id = %s
                    """,
                    (asset_id,),
                )
