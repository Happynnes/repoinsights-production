import os
import requests
from pprint import pprint
from typing import Any, Dict, List, Union, Optional, Tuple
import json
from django.conf import settings


class MetabaseSession:
    def __init__(self) -> None:
        self.metabase_url = f"{settings.METABASE_URL}/api/"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None

    def login(self, username: str, password: str) -> None:
        """Logs in and saves the session token."""
        response = self.session.post(
            self.metabase_url + "session",
            json={"username": username, "password": password},
        )
        data = response.json()
        pprint(data)
        self.token = data["id"]
        self.session.headers.update({"X-Metabase-Session": self.token})


class MetabasePermissions:
    def __init__(self, session: MetabaseSession) -> None:
        self.session = session

    def get_groups_memberships(self) -> Dict:
        """Gets group memberships."""
        response = self.session.session.get(
            self.session.metabase_url + "permissions/group"
        )
        data = response.json()
        return data

    def permissions_graph(self) -> Dict:
        """Gets permissions graph."""
        response = self.session.session.get(
            self.session.metabase_url + "permissions/graph"
        )
        data = response.json()
        return data


class MetabaseGroup:
    def __init__(self, session: MetabaseSession) -> None:
        self.session = session

    def create_group(self, username: str) -> Dict:
        response = self.session.session.post(
            self.session.metabase_url + "permissions/group",
            json={"name": f"{username}_group"},
        )
        data = response.json()
        return data


class MetabaseUser:
    def __init__(self, session: MetabaseSession) -> None:
        self.session = session

    def create_user(
        self, email: str, fname: str, lname: Optional[str] = None
    ) -> Tuple[int, int]:
        """Creates a metabase user."""
        if lname == "":
            lname = None

        group = MetabaseGroup(self.session).create_group(fname)
        pprint({"message": "Group created!", "data": group})
        group_id = group["id"]
        response = self.session.session.post(
            self.session.metabase_url + "user",
            json={
                "first_name": fname,
                "last_name": lname,
                "email": email,
            },
        )
        user = response.json()
        pprint({"message": "User created!", "data": user})
        user_id = user["id"]

        return user_id, group_id


class MetabaseAccess:
    def __init__(self, session: MetabaseSession) -> None:
        self.session = session

    def restringir_acceso_base_datos(
        self, permissions_graph: Dict, database_id: int, user_group: int
    ) -> Dict:
        # Restringir acceso a la base de datos
        return permissions_graph


class MetabaseDatabase:
    def __init__(self, session: MetabaseSession) -> None:
        self.session = session

    def obtener_id_database(self, nombre_base_datos: str) -> Optional[int]:
        url = self.session.metabase_url + "database"
        try:
            response = self.session.session.get(url)
            response.raise_for_status()
            data = response.json()
            databases = data["data"]
            for database in databases:
                if database["name"] == nombre_base_datos:
                    return int(database["id"])
            print(f"No se encontró la base de datos con el nombre '{nombre_base_datos}'.")
        except requests.exceptions.RequestException as e:
            print("Error al obtener la lista de bases de datos:", str(e))
        return None


class MetabaseConnection:
    def __init__(self, session: MetabaseSession) -> None:
        self.session = session

    def agregar_conexion_metabase(
        self, nombre: str, tipo_motor: str, host: str, puerto: str, dbname: str,
        usuario: str, password: str
    ) -> None:
        url = self.session.metabase_url + "database"
        detalles_conexion = {
            "name": nombre,
            "engine": tipo_motor,
            "details": {
                "host": host,
                "port": puerto,
                "dbname": dbname,
                "user": usuario,
                "password": password
                # Otros detalles de conexión según el tipo de base de datos
            },
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.session.post(
                url, headers=headers, data=json.dumps(detalles_conexion)
            )
            response.raise_for_status()
            print("Conexión agregada exitosamente.")
        except requests.exceptions.RequestException as e:
            print("Error al agregar la conexión:", str(e))


class MetabaseClient:
    def __init__(self) -> None:
        self.session = MetabaseSession()
        self.session.login(settings.MB_ADMIN_USER, settings.MB_ADMIN_PASS)
        self.permissions = MetabasePermissions(self.session)
        self.group = MetabaseGroup(self.session)
        self.user = MetabaseUser(self.session)
        self.access = MetabaseAccess(self.session)
        self.database = MetabaseDatabase(self.session)
        self.connection = MetabaseConnection(self.session)


if __name__ == "__main__":
    CONSOLIDADA_DATABASE = os.getenv("CONSOLIDADA_DB")
    CONSOLIDADA_IP = os.getenv("CONSOLIDADA_IP")
    CONSOLIDADA_PORT = os.getenv("CONSOLIDADA_PORT")
    CONSOLIDADA_USER = os.getenv("CONSOLIDADA_USER")
    CONSOLIDADA_PASSWORD = os.getenv("CONSOLIDADA_PASS")
    client = MetabaseClient()
