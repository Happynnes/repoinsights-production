import psycopg2
from psycopg2 import sql
from pprint import pprint


def create_user_with_policy(
    dbname,
    dbuser,
    dbpassword,
    dbhost,
    dbport,
    username,
    password,
    ids=None,
):
    conn = psycopg2.connect(
        dbname=dbname,
        user=dbuser,
        password=dbpassword,
        host=dbhost,
        port=dbport,
    )
    policy_name = f"{username}_policy"
    cur = conn.cursor()
    cur.execute(sql.SQL("CREATE USER {}").format(sql.Identifier(username)))
    cur.execute(
        sql.SQL("ALTER USER {} WITH PASSWORD %s").format(sql.Identifier(username)),
        [password],
    )
    if ids is not None and isinstance(ids, list):
        id_conditions = " OR ".join(f"id = {id}" for id in ids)
    else:
        id_conditions = "forked_from IS NULL AND deleted = False AND private = False"
    cur.execute(
        sql.SQL(
            """
            CREATE POLICY {} 
            ON ghtorrent_restore_2015.projects 
            TO {}
            USING ({});
        """
        ).format(
            sql.Identifier(policy_name),
            sql.Identifier(username),
            sql.SQL(id_conditions),
        )
    )
    cur.execute(
        """
        ALTER TABLE ghtorrent_restore_2015.projects ENABLE ROW LEVEL SECURITY;
        """
    )
    cur.execute(
        sql.SQL("GRANT USAGE ON SCHEMA ghtorrent_restore_2015 TO {};").format(
            sql.Identifier(username)
        )
    )
    cur.execute(
        sql.SQL(
            "GRANT SELECT ON ALL TABLES IN SCHEMA ghtorrent_restore_2015 TO {};"
        ).format(sql.Identifier(username))
    )
    cur.execute(
        sql.SQL(
            """
            ALTER DEFAULT PRIVILEGES IN SCHEMA ghtorrent_restore_2015 
            GRANT SELECT ON TABLES TO {};
        """
        ).format(sql.Identifier(username))
    )
    conn.commit()
    cur.close()
    conn.close()


def modify_user_policy(dbname, dbuser, dbpassword, username, ids=None):
    # Paso 1: Conéctate a la base de datos
    conn = psycopg2.connect(
        dbname=dbname,
        user=dbuser,
        password=dbpassword,
        host="localhost",
    )
    policy_name = f"{username}_policy"
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            DROP POLICY IF EXISTS {} 
            ON ghtorrent_restore_2015.projects;
        """
        ).format(sql.Identifier(policy_name))
    )

    # Paso 3: Crea la nueva política para el usuario
    if ids is not None and isinstance(ids, list):
        id_conditions = " OR ".join(f"id = {id}" for id in ids)
    else:
        id_conditions = "forked_from IS NULL AND deleted = False AND private = False"

    cur.execute(
        sql.SQL(
            """
            CREATE POLICY {}_policy 
            ON ghtorrent_restore_2015.projects 
            TO {}
            USING ({});
        """
        ).format(
            sql.Identifier(username),
            sql.Identifier(username),
            sql.SQL(id_conditions),
        )
    )

    # Comete los cambios y cierra la conexión
    conn.commit()
    cur.close()
    conn.close()
