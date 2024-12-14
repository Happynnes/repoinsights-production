from github import Github
from github.Repository import Repository
from loguru import logger


class License:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def calc(self):
        try:
            raw_license = self.repo.get_license()
            return {
                "exist": True,
                "data": {
                    "name": raw_license.license.name,
                    "permissions": raw_license.license.conditions,
                },
            }

        except Exception as e:
            logger.exception(e, traceback=True)
            return {"exist": False, "data": {}}
