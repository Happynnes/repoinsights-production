from pprint import pprint
import requests
from loguru import logger
from typing import Any, Optional, Dict, Union
import json
import redis
import time
import os
from datetime import datetime, timedelta

from services.extract_service.utils.utils import api_date, format_dt
from services.extract_service.config import GHToken
from services.extract_service.excepctions.exceptions import (
    RateLimitExceededError,
    NoMoreTokensError,
    ProjectNotFoundError,
    GitHubError,
    RateLimitExceededErrorPrivate,
    InternalGitHubError,
)

REMAINING = 200


class GitHubAPI:
    def __init__(self, private_token: str | None = None):
        self.cache = Cache()
        self.tokens_handler = GHToken()
        tokens = self.tokens_handler.get_public_tokens()
        self.token = tokens[0]
        self.private_token = private_token
        self.headers = self.get_headers(self.token, private_token)

    def get_headers(self, token: str, private_token: str | None = None):
        if private_token:
            headers = {"Authorization": f"token {private_token}"}
            return headers

        headers = {"Authorization": f"token {token}"}
        return headers

    def rate_limit_handling(self, func, *args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except RateLimitExceededError:
                try:
                    self._handle_no_more_calls()
                except NoMoreTokensError:
                    logger.critical("No more tokens")
                    self._handle_wait_time()
                    continue

                except RateLimitExceededErrorPrivate:
                    logger.critical("No more calls, API rate limit exceeded")
                    self._handle_wait_time()
                    continue

                self.rate_limit_handling(func, *args, **kwargs)

    def update_token(self, new_token: str):
        self.token = new_token
        self.headers["Authorization"] = f"token {self.token}"

    def _handle_no_more_calls(self):
        if self.private_token:
            logger.warning("Handling no more calls")
            raise RateLimitExceededErrorPrivate("Private repo no more calls")
        tokens = self.tokens_handler.get_public_tokens(only_token=False)
        for token, calls, _ in tokens:
            if calls > REMAINING:
                logger.warning(f"Token changed {token[-10:]}")
                self.update_token(token)
                return
        logger.warning("No more tokens available")
        raise NoMoreTokensError("No more tokens available")

    def _handle_wait_time(self):
        token, calls, reset_time = self.tokens_handler.get_token_lowest_wait_time()
        now = datetime.now()
        wait_time = reset_time - now.timestamp()
        pprint(
            {
                "token": token[-10:],
                "calls": calls,
                "reset_time": reset_time,
                "now": now.timestamp(),
                "wait_time": wait_time,
            }
        )
        if wait_time > 0 and calls <= REMAINING:
            logger.warning(
                f"Waiting {wait_time} seconds  {now + timedelta(seconds=wait_time)}"
            )
            time.sleep(wait_time)
        self.update_token(token)

    def get(
        self,
        url,
        params=None,
        name: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        retries: Optional[int] = 0,
    ):
        try:
            if headers is not None:
                self.headers.update(headers)

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            logger.debug(
                f"{name} \t {response.headers['X-RateLimit-Remaining']}/{response.headers['X-RateLimit-Limit']}"
            )

            remaining_limit = int(response.headers["X-RateLimit-Remaining"])
            if remaining_limit < REMAINING:
                raise RateLimitExceededError("GitHub API rate limit is low.")
            return response
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if (
                status_code == 403
                and "X-RateLimit-Remaining" in e.response.headers
                and int(e.response.headers["X-RateLimit-Remaining"]) <= REMAINING
            ):
                raise RateLimitExceededError("GitHub API rate limit exceeded.")
            elif status_code == 401:
                logger.exception("Token expired", traceback=True)
                raise GitHubError("Token expired")
            elif status_code == 422:
                logger.exception("Error to process petition", traceback=True)
                raise GitHubError("Error to process petition")
            elif status_code == 451:
                logger.exception("Proyecto eliminado", traceback=True)
                raise ProjectNotFoundError("Proyecto eliminado")
            elif status_code == 404:
                logger.exception("Proyecto no encontrado", traceback=True)
                raise ProjectNotFoundError("Proyecto no encontrado")
            elif status_code == 500:
                logger.exception(
                    "Error {number} de GitHub", traceback=True, number=status_code
                )
                raise InternalGitHubError("GitHub Internal Error")
            elif status_code == 502:
                retries = 0 if retries is None else retries
                logger.exception(
                    "Error {number} de GitHub", traceback=True, number=status_code
                )
                time.sleep(60)
                retries += 1
                if retries > 3:
                    raise InternalGitHubError("GitHub Internal Error")
                self.get(
                    url, params=params, name=name, headers=headers, retries=retries
                )
            else:
                raise e

    def _prepare_params(self, name: str, params: Optional[Dict] = None) -> Dict:
        if params is None:
            params = {}

        params.setdefault("per_page", 100)

        if params.get("since") is not None:
            self._log_warning(name, params["since"])
            params["since"] = self._format_datetime(params["since"])

        if params.get("until") is not None:
            params["until"] = self._format_datetime(params["until"])

        return params

    def _log_warning(self, name: str, since: Any) -> None:
        logger.warning(
            "{name} \t Since: {type} - {since}",
            type=type(since),
            since=since,
            name=name,
        )

    def _format_datetime(self, dt: Any) -> Any:
        if type(dt) == "datetime":
            return format_dt(dt)
        return dt

    def _realizar_solicitud_paginada(
        self,
        name: str,
        url: Union[str, None],
        params: Optional[Dict] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        params = self._prepare_params(params=params, name=name)
        if headers is None:
            headers = self.headers

        elementos = []
        pag = 1

        while url:
            try:
                response = self.get(url, params=params, headers=headers, name=name)
                if response is None:
                    break

                elementos.extend(response.json())
                logger.info(f"{name} Pagina {pag}: {len(response.json())} elementos")
                pag += 1

                url = self._get_next_url(response)

            except InternalGitHubError as e:
                logger.exception("Error 500 {e}", traceback=True, e=e)
                pag += 1
                params["page"] = pag
                url = url.split("&page=")[0] + f"&page={pag}"

        return elementos

    def _get_next_url(self, response):
        if "next" in response.links:
            return response.links["next"]["url"]
        else:
            return None

    def _filtrar_por_fecha(self, elementos, since=None, until=None):
        if since is None and until is None:
            return elementos
        resultados = []
        for elemento in elementos:
            created_at = api_date(elemento["created_at"])
            if since and created_at < since:
                continue
            if until and created_at > until:
                continue
            resultados.append(elemento)

        return resultados


class Cache:
    def __init__(self):
        self.redis_host = os.environ["REDIS_HOST"]
        self.redis_port: int = int(os.environ["REDIS_PORT"])
        self.redis_db = int(os.environ["REDIS_DB"])
        self.redis_cache = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, db=self.redis_db
        )

    def get(self, key):
        value = self.redis_cache.get(key)
        return json.loads(value.decode("utf-8")) if value else None

    def set(self, key, value):
        expiry = 6 * 60 * 60
        serialized_value = json.dumps(value)
        self.redis_cache.set(key, serialized_value, ex=expiry)

    def has(self, key):
        return self.redis_cache.exists(key)
