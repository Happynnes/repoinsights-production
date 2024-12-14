from typing import List
from loguru import logger
from services.extract_service.repoinsights.pull_request import (
    InsightsPullRequest,
    InsightsPullRequestComment,
    InsightsCommit,
)
from services.extract_service.repoinsights.repository import InsightsRepository
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
)
from services.extract_service.load_module.controllers.load_users import (
    LoadUserController,
)
from services.extract_service.load_module.controllers.load_commits import (
    LoadCommitController,
)

from services.extract_service.load_module.controllers.load_projects import (
    LoadProjectController,
)


class LoadPullRequestController:
    def __init__(
        self,
        temp_db: DatabaseHandler,
        user_controller: LoadUserController,
        commit_controller: LoadCommitController,
        project_controller: LoadProjectController,
        repo_id: int,
    ) -> None:
        self.temp_db = temp_db
        self.user_controller = user_controller
        self.commit_controller = commit_controller
        self.project_controller = project_controller
        self.repo_id = repo_id

    def load_pull_request(self, pr: InsightsPullRequest):
        logger.debug("Loading pull request {number}", number=pr.number)
        return self.temp_db.create_pull_request(pr)

    def load_pull_request_comments(
        self, _, pr_id, comments: List[InsightsPullRequestComment]
    ):
        for comment in comments:
            comment.set_pull_request_id(pr_id)
            if comment.author is not None:
                comment.set_user_id(self.user_controller.load_user(comment.author))
                commit_id = self.commit_controller.find_commit_sha(comment.commit_sha)
                if commit_id is None:
                    logger.error(
                        "Commit {sha} is a forked commit, skipping",
                        sha=comment.commit_sha,
                    )
                    continue
                comment.set_commit_id(commit_id)
                self.temp_db.create_pull_request_comment(comment)
            else:
                logger.error("Comment {id} has no author, skipping", id=comment)

    def load_pull_request_commits(self, _, pr_id: int, commits: List[InsightsCommit]):
        for commit in commits:
            commit_id = self.commit_controller.find_commit_sha(commit.sha)
            if commit_id is None:
                logger.warning("Commit {sha} not found in database", sha=commit.sha)
                commit_id = self.commit_controller.create_commit(commit)
            self.temp_db.create_pull_request_commit(pr_id=pr_id, commit_id=commit_id)

    def load_pull_request_history(self, pr: InsightsPullRequest, pr_id):
        if pr.created_at is not None:
            data = {
                "pull_request_id": pr_id,
                "created_at": pr.created_at,
                "action": "opened",
                "actor_id": self.user_controller.load_user(pr.author),
            }
            self.temp_db.create_pull_request_history(data)
        if pr.closed_at is not None:
            data = {
                "pull_request_id": pr_id,
                "created_at": pr.closed_at,
                "action": "closed",
                "actor_id": self.user_controller.load_user(pr.author),
            }
            self.temp_db.create_pull_request_history(data)
        if pr.merged_at is not None:
            data = {
                "pull_request_id": pr_id,
                "created_at": pr.merged_at,
                "action": "merged",
                "actor_id": self.user_controller.load_user(pr.author),
            }
            self.temp_db.create_pull_request_history(data)

    def load_pull_requests_data(self, pull_requests: List[InsightsPullRequest]):
        for pr in pull_requests:
            pr.set_user_id(self.user_controller.load_user(pr.author))
            self.project_controller.update_repo_data(pr.head_repo)
            self.project_controller.update_repo_data(pr.base_repo)
            head_repo_id = None
            if pr.head_repo is not None:
                head_repo_id = self.project_controller.load_repository(pr.head_repo)
                pr.set_head_repo_id(head_repo_id)
            pr.set_base_repo_id(self.repo_id)

            self.commit_controller.update_commit_data(pr.head_commit, head_repo_id)
            self.commit_controller.update_commit_data(pr.base_commit, self.repo_id)

            head_commit_id = self.commit_controller.load_fork_commit(pr.head_commit)
            base_commit_id = self.commit_controller.load_commit(pr.base_commit)
            pr.set_head_commit_id(head_commit_id)
            pr.set_base_commit_id(base_commit_id)

            pr_id = self.load_pull_request(pr)
            self.load_pull_request_comments(pr, pr_id, pr.comments)
            self.load_pull_request_history(pr, pr_id)
            self.load_pull_request_commits(pr, pr_id, pr.commits)
