from psycopg2 import connect as PGConnect
from sshtunnel import SSHTunnelForwarder
from json import dumps as JSONDumps
from s3_sync.utils.config import *


def pg_query(query: str):
    """
    Initialize the Postgres provider
    """
    tunnel = None

    if (pg_tunnel_enabled == 'true'):
        tunnel = SSHTunnelForwarder(
            (pg_tunnel_ssh_host, pg_tunnel_ssh_port),
            ssh_username=pg_tunnel_ssh_user,
            ssh_password=pg_tunnel_ssh_password,
            ssh_pkey=pg_tunnel_ssh_key,
            remote_bind_address=(pg_db_host, pg_db_port),
            local_bind_address=(pg_tunnel_local_host, pg_tunnel_local_port)
        )
        tunnel.start()

    conn = PGConnect(
        database=pg_db_database,
        user=pg_db_user,
        password=pg_db_password,
        host=pg_db_host if (pg_tunnel_enabled == 'false'
                            ) else pg_tunnel_local_host,
        port=pg_db_port if (pg_tunnel_enabled == 'false'
                            ) else pg_tunnel_local_port
    )

    cur = conn.cursor()

    cur.execute(query)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    if (tunnel != None):
        tunnel.close()

    return rows


def get_media_attachments():
    query = "SELECT id, file_file_name, thumbnail_file_name, processing, processing FROM media_attachments ORDER BY id;"
    return pg_query(query)


if __name__ == '__main__':
    # "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    # "SELECT COUNT(*) FROM media_attachments;"
    # "SELECT id, file_file_name, thumbnail_file_name, processing, processing FROM media_attachments ORDER BY id desc LIMIT 10;"
    # query = "SELECT id, file_file_name, thumbnail_file_name, processing, processing FROM media_attachments ORDER BY id desc LIMIT 10;"
    query = "SELECT * FROM preview_cards ORDER BY id LIMIT 10;"

    rows = pg_query(query)

    for row in rows:
        # print(type(row[0]))
        print(str(row))
        # print(JSONDumps(row))
