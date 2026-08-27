import psycopg


def ping_database(database_url: str) -> bool:
    with psycopg.connect(
        database_url,
        connect_timeout=5,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()

    return row == (1,)
