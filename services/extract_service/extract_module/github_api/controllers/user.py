from pprint import pprint
from typing import Optional, Dict, Any, List, Union
from loguru import logger
from datetime import datetime
from services.extract_service.utils.utils import (
    get_unique_users,
    add_users_to_dict_keys,
)
from services.extract_service.extract_module.github_api.github_api import GitHubAPI


class User:
    def __init__(self, api: GitHubAPI):
        self.api = api

    def obtener_usuario(self, usuario: str) -> Union[Dict[str, Any], None]:
        if self.api.cache.has(usuario):
            logger.debug("Getting usuario cacheado {commit_sha}", commit_sha=usuario)
            return self.api.cache.get(usuario)

        url = f"https://api.github.com/users/{usuario}"
        try:
            user_data = self.api.rate_limit_handling(self.api.get, url=url)
            if user_data is None:
                return None
            user_data = user_data.json()

            self.api.cache.set(usuario, user_data)
            return user_data
        except Exception:
            logger.exception(f"Error al obtener usuario {usuario}", traceback=True)
            return None

    def _get_users_for_keys(
        self, elements, user_keys: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        users_to_fetch = set()
        for user_key in user_keys:
            users_to_fetch.update(get_unique_users(elements, user_key))
        users = {}
        for user in users_to_fetch:
            new_user = self.obtener_usuario(user)
            if new_user:
                users[user] = new_user
        return users
