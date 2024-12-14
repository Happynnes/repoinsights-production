import os
import requests
from pprint import pprint
from typing import Any, Dict, List, Union, Optional, Tuple
import json
from django.conf import settings
import jwt

from repoinsights.views.helper.project_manager import ProjectManager


class SupersetSession:
    def __init__(self) -> None:
        self.superset_url = f"{settings.SUPERSET_URL}/api/v1/"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None

    def login(self, username: str, password: str) -> None:
        """Logs in and saves the session token."""
        response = self.session.post(
            self.superset_url + "security/login",
            json={"username": username, "password": password},
        )
        data = response.json()
        self.token = data["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})


class SupersetDatabase:
    def __init__(self, session: SupersetSession) -> None:
        self.session = session

    def get_database_id(self, database_name: str) -> Optional[int]:
        """Obtains the database ID by name."""
        response = self.session.session.get(self.session.superset_url + "database")
        data = response.json()
        databases = data["result"]
        for database in databases:
            if database["database_name"] == database_name:
                return int(database["id"])
        print(f"No se encontró la base de datos con el nombre '{database_name}'.")
        return None

    def add_database_connection(self, name: str, sqlalchemy_uri: str) -> None:
        """Adds a new database connection to Superset."""
        url = self.session.superset_url + "database/"
        details = {
            "database_name": name,
            "sqlalchemy_uri": sqlalchemy_uri,
            "extra": {"engine": "postgresql"},
        }
        try:
            response = self.session.session.post(url, json=details)
            response.raise_for_status()
            print("Conexión agregada exitosamente.")
        except requests.exceptions.RequestException as e:
            print("Error al agregar la conexión:", str(e))


class SupersetDashboard:
    def __init__(self, session: SupersetSession) -> None:
        self.session = session

    def get_all_dashboards(self) -> List[Dict]:
        """Obtains all dashboards."""
        response = self.session.session.get(self.session.superset_url + "dashboard/")
        return response.json()["result"]

    def get_dashboard_by_id(self, dashboard_id: int) -> Dict:
        """Obtains a dashboard by its ID."""
        response = self.session.session.get(
            self.session.superset_url + f"dashboard/{dashboard_id}"
        )
        return response.json()["result"]


class SupersetClient:
    def __init__(self) -> None:
        self.session = SupersetSession()
        self.session.login(settings.SUPERSET_ADMIN_USER, settings.SUPERSET_ADMIN_PASS)
        self.database = SupersetDatabase(self.session)
        self.dashboard = SupersetDashboard(self.session)

class SupersetUser:
    def __init__(self, session: SupersetSession) -> None:
        self.session = session

    def resend_invitation(self, user_id: int) -> Dict:
        """Envía una invitación al usuario. Este método simula el reenvío."""
        # Como no hay un endpoint directo en Superset, se puede implementar
        # un mecanismo alternativo para enviar una invitación.
        user_email = self.get_user_email(user_id)  # Asume que tienes este método implementado
        # Lógica para reenviar correo/invitación al usuario (puedes integrar algún servicio de correo)
        return {"message": f"Invitation sent to {user_email}"}
    
    def get_user_email(self, user_id: int) -> str:
        """Obtiene el correo electrónico del usuario a partir del user_id."""
        url = self.session.superset_url + f"security/user/{user_id}"
        response = self.session.session.get(url)
        data = response.json()
        return data.get("email")



if __name__ == "__main__":
    CONSOLIDADA_DATABASE = os.getenv("CONSOLIDADA_DB")
    CONSOLIDADA_USER = os.getenv("CONSOLIDADA_USER")
    CONSOLIDADA_PASSWORD = os.getenv("CONSOLIDADA_PASS")
    
    client = SupersetClient()
    # Agrega la conexión a Superset aquí, usando la base de datos consolidada
    sqlalchemy_uri = f"postgresql://{CONSOLIDADA_USER}:{CONSOLIDADA_PASSWORD}@{os.getenv('CONSOLIDADA_IP')}:{os.getenv('CONSOLIDADA_PORT')}/{CONSOLIDADA_DATABASE}"
    client.database.add_database_connection(CONSOLIDADA_DATABASE, sqlalchemy_uri)
