import os
import requests
from pprint import pprint
from typing import Any, Dict, List, Union, Optional, Tuple
import json
from django.conf import settings


class SupersetSession:
    def __init__(self) -> None:
        self.superset_url = f"{settings.SUPERSET_URL}/api/v1"
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
        pprint(data)
        self.token = data["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})


class SupersetDatabase:
    def __init__(self, session: SupersetSession) -> None:
        self.session = session

    def get_database_id(self, database_name: str) -> Optional[int]:
        """Obtains the database ID from Superset."""
        url = self.session.superset_url + "database/"
        try:
            response = self.session.session.get(url)
            response.raise_for_status()
            data = response.json()
            databases = data['result']
            for database in databases:
                if database["database_name"] == database_name:
                    return database["id"]
            print(f"No se encontró la base de datos con el nombre '{database_name}'.")
        except requests.exceptions.RequestException as e:
            print("Error al obtener la lista de bases de datos:", str(e))
        return None

    def add_database(self, database_details: Dict) -> None:
        """Adds a database connection to Superset."""
        url = self.session.superset_url + "database/"
        try:
            response = self.session.session.post(url, json=database_details)
            response.raise_for_status()
            print("Conexión agregada exitosamente.")
        except requests.exceptions.RequestException as e:
            print("Error al agregar la conexión:", str(e))


class SupersetClient:
    def __init__(self) -> None:
        self.session = SupersetSession()
        self.session.login(settings.SUPERSET_ADMIN_USER, settings.SUPERSET_ADMIN_PASS)
        self.database = SupersetDatabase(self.session)


if __name__ == "__main__":
    # Replace these environment variables with your Superset configurations
    CONSOLIDADA_DATABASE = os.getenv("CONSOLIDADA_DB")
    DATABASE_TYPE = "postgresql"
    CONSOLIDADA_IP = os.getenv("CONSOLIDADA_IP")
    CONSOLIDADA_PORT = os.getenv("CONSOLIDADA_PORT")
    CONSOLIDADA_USER = os.getenv("CONSOLIDADA_USER")
    CONSOLIDADA_PASSWORD = os.getenv("CONSOLIDADA_PASS")

    database_details = {
        "database_name": CONSOLIDADA_DATABASE,
        "sqlalchemy_uri": f"{DATABASE_TYPE}://{CONSOLIDADA_USER}:{CONSOLIDADA_PASSWORD}@{CONSOLIDADA_IP}:{CONSOLIDADA_PORT}/{CONSOLIDADA_DATABASE}",
    }

    client = SupersetClient()
    client.database.add_database(database_details)
