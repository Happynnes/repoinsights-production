from services.extract_service.extract_module.github_api.extractor import GitHubExtractor
from datetime import datetime
from loguru import logger
from typing import Union, List
from services.extract_service.utils.paralell import run_in_parallel

from services.extract_service.repoinsights.handlers.commit_handler import (
    InsightsCommitHandler,
)
from services.extract_service.repoinsights.handlers.project_user_handler import (
    InsightsProjectUserHandler,
)
from services.extract_service.repoinsights.handlers.label_handler import (
    InsightsLabelHandler,
)
from services.extract_service.repoinsights.handlers.issue_handler import (
    InsightsIssueHandler,
)
from services.extract_service.repoinsights.handlers.pull_request_handler import (
    InsightsPullRequestHandler,
)
from services.extract_service.repoinsights.handlers.repository_handler import (
    InsightsRepositoryHandler,
)


class RepoNotFound(Exception):
    pass


class ExtractDataController:
    def __init__(
        self,
        owner: str,
        repo: str,
        since: datetime | None,
        until: datetime | None,
        private_token: str | None,
        data_types: List[str],
    ) -> None:
        self.data_types = data_types
        self.since = since
        self.until = until
        self.private = private_token

        self.repo = GitHubExtractor(owner, repo, private_token=private_token)
        self.commit_handler = InsightsCommitHandler(self.repo)
        self.project_handler = InsightsProjectUserHandler(self.repo)
        self.pull_request_handler = InsightsPullRequestHandler(self.repo)
        self.label_handler = InsightsLabelHandler(self.repo)
        self.issue_handler = InsightsIssueHandler(self.repo)
        self.repo_handler = InsightsRepositoryHandler(self.repo)

    def extract(self):
        args_list = [(data_type,) for data_type in self.data_types]
        main_project = self.extract_data("project")
        results = run_in_parallel(self.extract_data, args_list)
        results.append(main_project)
        return results

    def extract_data(
        self,
        data_type: str,
    ):
        if data_type == "commits":
            commits = self.commit_handler.get_commits(self.since, self.until)
            logger.info(f"Total GHCommits: {len(commits)}")
            self.commit_handler.get_commit_comments(commits)
            return {"name": "commit", "data": commits}

        elif data_type == "project":
            project = self.repo_handler.get_main_repo()
            if project.owner is None:
                raise RepoNotFound("Repo not found")

            logger.info("Project owner: {owner}", owner=project.owner.login)
            return {"name": "project", "data": project}

        elif data_type == "pull_requests":
            prs = self.pull_request_handler.get_all_pull_requests(
                self.since, self.until
            )
            logger.info(f"Total GHPullRequests: {len(prs)}")
            self.pull_request_handler.get_pull_request_comments(prs)
            self.pull_request_handler.get_pull_request_commits(prs)
            return {"name": "pull_request", "data": prs}

        elif data_type == "issues":
            issues = self.issue_handler.get_issues(
                start_date=self.since, end_date=self.until
            )
            logger.info(f"Total GHIssues: {len(issues)}")
            self.issue_handler.get_issue_comments(issues)
            self.issue_handler.get_issue_events(issues)

            return {"name": "issue", "data": issues}

        elif data_type == "labels":
            labels = self.label_handler.get_labels()
            logger.info(f"Total GHLabels: {len(labels)}")
            return {"name": "labels", "data": labels}

        elif data_type == "members":
            members = self.project_handler.get_members(
                since=self.since, until=self.until
            )
            logger.info(f"Total members GHUser: {len(members)}")
            return {"name": "member", "data": members}

        elif data_type == "stargazers":
            stargazers = self.project_handler.get_stargazers(
                since=self.since, until=self.until
            )
            logger.info(f"Total stargazers GHUser: {len(stargazers)}")
            return {"name": "watchers", "data": stargazers}

        elif data_type == "milestones":
            milestones = self.issue_handler.get_milestones()
            logger.info(f"Total GHMilestone: {len(milestones)}")
            return {"name": "milestones", "data": milestones}

        else:
            print(f"Invalid data type: {data_type}")
