from github import Github
from github.Repository import Repository
import os


class ContinuousIntegration:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.temp_repos_path = "temp_repos"

    def __get_root_files(self):
        return self.repo.get_dir_contents(path=".")

    def __find_ci_files(self):
        ci_files = [
            ".github",
            "travis.yml",
            "circleci.yml",
            "appveyor.yml",
            "azure-pipelines.yml",
            "bitrise.yml",
            "buildkite.yml",
            "codeship.yml",
            "drone.yml",
            ".gitlab-ci.yml",
            "wercker.yml",
            "snap.yml",
            "shippable.yml",
            "semaphore.yml",
            "sail.yml",
            "build.yml",
        ]
        for file in self.__get_root_files():
            if file.name in ci_files:
                return {"exist": True, "data": {"name": file.name, "path": file.path}}
        return {"exist": False, "data": {}}

    def calc(self):
        self.__get_root_files()
        exist_ci_file = self.__find_ci_files()
        return exist_ci_file
