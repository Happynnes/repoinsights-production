from typing import Optional, Dict, Any, List, Union
from loguru import logger
from services.extract_service.extract_module.github_api.github_api import GitHubAPI
from services.extract_service.extract_module.github_api.controllers.user import User
from services.extract_service.utils.utils import add_users_to_dict_keys
from services.extract_service.repoinsights.repository import InsightsRepository
from services.extract_service.excepctions.exceptions import (
    ProjectNotFoundError,
    GitHubUserException,
)


class Repository:
    def __init__(
        self, api: GitHubAPI, repositorio: str, owner: str, user: User
    ) -> None:
        self.usuario = owner
        self.repositorio = repositorio
        self.api = api
        self.user_controller = user

    def validate_repo_name(self, full_name: str):
        consolidada_name = f"{self.usuario}/{self.repositorio}"
        logger.warning(f"Validando nombre de repo {full_name} == {consolidada_name}")
        try:
            if full_name != consolidada_name:
                raise GitHubUserException(
                    f"El nombre del repo no coincide con el nombre consolidado: {full_name} != {consolidada_name}"
                )
        except GitHubUserException as e:
            logger.exception("Nombre no existe", traceback=True)
            raise e

    def obtener_repositorio(self) -> Dict[str, Any]:
        url = f"https://api.github.com/repos/{self.usuario}/{self.repositorio}"
        repo_data = self.api.rate_limit_handling(
            self.api.get,
            url=url,
            name="repo",
        )
        if repo_data is None:
            raise ProjectNotFoundError("Error al obtener repo")
        repo = repo_data.json()
        logger.warning(f"Obteniendo repo {self.usuario}/{self.repositorio}")
        full_name: str = repo["full_name"]
        self.validate_repo_name(full_name)
        owner_data = self.user_controller.obtener_usuario(self.usuario)
        repo["owner"] = owner_data

        return repo

    def obtener_contribuidores(self):
        url = f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/contributors"
        params = {"per_page": 100}
        contribuidores = self.api.rate_limit_handling(
            self.api._realizar_solicitud_paginada,
            name="contributors",
            url=url,
            params=params,
        )
        return contribuidores

    def obtener_stargazers(self):
        url = (
            f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/stargazers"
        )
        headers = {"Accept": "application/vnd.github.v3.star+json"}
        stargazers = self.api._realizar_solicitud_paginada(
            name="stargazers", url=url, headers=headers
        )
        for stargazer in stargazers:
            user_name = stargazer["user"]["login"]
            user_data = self.user_controller.obtener_usuario(user_name)
            stargazer["user"] = user_data

        return stargazers

    def obtener_labels(self) -> List[Dict[str, Any]]:
        url = f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/labels"
        labels = self.api.rate_limit_handling(
            self.api._realizar_solicitud_paginada,
            url=url,
            name="labels",
        )
        return labels

    def obtener_milestone(self, state=None) -> List[Dict[str, Any]]:
        url = (
            f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/milestones"
        )
        params = {"state": state}
        milestone = self.api.rate_limit_handling(
            self.api._realizar_solicitud_paginada,
            url=url,
            params=params,
            name="milestone",
        )
        users = self.user_controller._get_users_for_keys(
            milestone,
            ["creator"],
        )
        add_users_to_dict_keys(
            milestone,
            users,
            ["creator"],
        )
        return milestone
