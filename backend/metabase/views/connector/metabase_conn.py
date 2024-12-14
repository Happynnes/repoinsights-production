import os
import requests
from pprint import pprint
from typing import Any, Dict, List, Union, Optional, Tuple
import json
from django.conf import settings
import time
import jwt

from repoinsights.views.helper.project_manager import ProjectManager


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
        """Creates a group."""
        pprint("Creating group")
        response = self.session.session.post(
            self.session.metabase_url + "permissions/group",
            json={"name": f"{username}_group"},
        )
        data = response.json()
        return data

    def add_user_to_group(self, group_id: int, user_id: int) -> Dict:
        """Adds a user to a group."""
        response = self.session.session.post(
            self.session.metabase_url + "permissions/membership",
            json={
                "group_id": group_id,
                "user_id": user_id,
            },
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
    
    def resend_invitation(self, user_id: int) -> Dict:
        """Resends the invitation to the user."""
        response = self.session.session.post(
            self.session.metabase_url + f"user/{user_id}/send_invite"
        )
        data = response.json()
        return data


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
            print(
                f"No se encontró la base de datos con el nombre '{nombre_base_datos}'."
            )
        except requests.exceptions.RequestException as e:
            print("Error al obtener la lista de bases de datos:", str(e))
        return None


class MetabaseConnection:
    def __init__(self, session: MetabaseSession) -> None:
        self.session = session

    def agregar_conexion_metabase(
        self,
        nombre: str,
        tipo_motor: str,
        host: str,
        puerto: str,
        dbname: str,
        usuario: str,
        password: str,
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


class MetabaseShare:
    def __init__(self, session: MetabaseSession) -> None:
        self.session = session

    def get_token(self, payload):
        return jwt.encode(payload, settings.METABASE_SECRET_KEY, algorithm="HS256")

    def create_iframe_url(self, user_id: int, dashboard_id: str | int, params) -> Tuple:
        if params is None:
            project_ids = ProjectManager.get_user_selected_project_ids(user_id)
            project_ids = [str(project_id) for project_id in project_ids]
            params = {"id": project_ids}
        payload = {
            "resource": {"dashboard": int(dashboard_id)},
            "params": params,
            "exp": round(time.time()) + (60 * 10),
        }

        iframeUrl = (
            settings.METABASE_URL
            + "/embed/dashboard/"
            + self.get_token(payload)
            + "#bordered=true&titled=false"
        )
        return iframeUrl, params


class MetabaseDashboard:
    def __init__(self, session: MetabaseSession, share: MetabaseShare) -> None:
        self.session = session
        self.share = share

    def filter_by_description(self, dashboards, filter: str) -> List:
        ids_list = []
        for dashboard in dashboards:
            if (
                dashboard.get("description")
                and filter in dashboard["description"]
                and dashboard["enable_embedding"] == True
            ):
                ids_list.append(dashboard)
        return ids_list
    
    def create_dashboard_response(self, dashboards_ids: List[Dict], user_id: int, project_id: str | int):
        iframes = []
        for dashboard in dashboards_ids:
            url, params = self.share.create_iframe_url(
                user_id, dashboard["id"], project_id
            )
            iframes.append(
                self.dashboard_response(
                    url=url, dashboard=dashboard, params=params
                )
            )
        return iframes
    
    def dashboard_response(self, url: str, params: List, dashboard: Dict) -> Dict:
        return {"data": dashboard, "iframe": url, "params": params}

    def get_all_dashboards(self, filter: Optional[str] = None):
        response = self.session.session.get(self.session.metabase_url + "dashboard")
        data = response.json()
        return data

    def get_dashboard_ids(self, filter: Optional[str]=None) -> List[Dict[str, Union[int, str]]]:
        dashboards = self.get_all_dashboards()
        if filter:
            return self.filter_by_description(dashboards, filter)
        return [
            {
                "id": dashboard["id"], 
                "name": dashboard["name"]
             }
            for dashboard in dashboards
            if dashboard["enable_embedding"] == True
        ]

    def get_dashboard_by_id(
        self, dashboard_id: int, filter: Optional[str] = None
    ) -> Dict:
        response = self.session.session.get(
            self.session.metabase_url + f"dashboard/{dashboard_id}"
        )
        data = response.json()
        if filter:
            return self.filter_by_description(data, filter)  # type: ignore
        return data



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
        self.share = MetabaseShare(self.session)
        self.dashboard = MetabaseDashboard(self.session, self.share)


if __name__ == "__main__":
    CONSOLIDADA_DATABASE = os.getenv("CONSOLIDADA_DB")
    CONSOLIDADA_IP = os.getenv("CONSOLIDADA_IP")
    CONSOLIDADA_PORT = os.getenv("CONSOLIDADA_PORT")
    CONSOLIDADA_USER = os.getenv("CONSOLIDADA_USER")
    CONSOLIDADA_PASSWORD = os.getenv("CONSOLIDADA_PASS")
    client = MetabaseClient()
