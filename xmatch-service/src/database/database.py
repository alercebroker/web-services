from psycopg_pool import ConnectionPool


def create_connection(user, pwd, host, port, db):
    conn_url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    pool = ConnectionPool(conninfo=conn_url, open=True)
    return pool
