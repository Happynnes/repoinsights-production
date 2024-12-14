from pprint import pprint
from github import Github, Repository


class CoreContributors:
    def __init__(self, repo: Repository.Repository):
        self.repo = repo

    def get_contributors_data(self, contributors, total_commits):
        contributors_data = []
        for contributor in contributors:
            contributor_percentage = contributor.contributions / total_commits * 100
            contributors_data.append(
                {
                    "id": contributor.id,
                    "login": contributor.login,
                    "total": contributor.contributions,
                    "percentage": contributor_percentage,
                }
            )

        return contributors_data

    def __calc_core_contributors(self, contributors: list[dict]):
        core_contributors = []
        sum_percentage = 0
        index = 0
        while index < len(contributors) and sum_percentage < 80.0:
            contributor = contributors[index]
            core_contributors.append(contributor)
            sum_percentage += contributor["percentage"]
            index += 1
        return {
            "core_contributors": core_contributors,
            "cardinality": len(core_contributors),
        }

    def calc(self) -> dict:
        contributors = self.repo.get_contributors()
        total_commits = self.repo.get_commits().totalCount
        contributors_data = self.get_contributors_data(contributors, total_commits)
        core_contributors = self.__calc_core_contributors(contributors_data)
        return core_contributors
