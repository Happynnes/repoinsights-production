from loguru import logger
from typing import List
from services.extract_service.repoinsights.commit import InsightsCommit
from services.extract_service.load_module.controllers.load_users import (
    LoadUserController,
)
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
)


class LoadCommitController:
    def __init__(
        self, temp_db: DatabaseHandler, repo_id, user_controller: LoadUserController
    ) -> None:
        self.temp_db = temp_db
        self.repo_id = repo_id
        self.user_controller = user_controller

    def load_fork_commit(self, commit: InsightsCommit) -> int:
        logger.warning("Loading fork commit {sha}", sha=commit.sha)
        commit_id = self.temp_db.find_commit_id(sha=commit.sha)
        if commit_id is None:
            logger.warning("Fork commit {sha} does not exist", sha=commit.sha)
            commit_id = self.load_commit(commit)
        else:
            logger.warning(
                "Fork commit {sha} already exists {id}",
                sha=commit.sha,
                id=commit_id,
            )

        return commit_id

    def load_commit(self, commit: InsightsCommit) -> int:
        logger.debug("Loading commit {sha}", sha=commit.sha)
        commit_id = self.find_commit_sha(commit.sha)
        if commit_id is None:
            commit_id = self.temp_db.create_commit(commit)
            if commit.project_id is not None:
                self.temp_db.create_project_commit(commit.project_id, commit_id)
        return commit_id

    def create_commit(self, commit: InsightsCommit) -> int:
        logger.debug("Creating commit {sha}", sha=commit.sha)
        commit.set_project_id(self.repo_id)
        commit.set_author_id(
            self.user_controller.load_user(commit.author) if commit.author else None
        )
        commit.set_committer_id(
            self.user_controller.load_user(commit.committer)
            if commit.committer
            else None
        )
        commit_id = self.temp_db.create_commit(commit)
        if commit.project_id is not None:
            self.temp_db.create_project_commit(commit.project_id, commit_id)
        return commit_id

    def load_commits_data(self, commits: List[InsightsCommit]):
        commit: InsightsCommit
        for commit in commits:
            commit.set_project_id(self.repo_id)
            commit.set_author_id(
                self.user_controller.load_user(commit.author) if commit.author else None
            )
            commit.set_committer_id(
                self.user_controller.load_user(commit.committer)
                if commit.committer
                else None
            )
            commit_id = self.load_commit(commit)
            self.temp_db.create_commit_comments(commit_id, commit.comments)
            # self.temp_db.create_commit_parents(commit_id, commit.parents)

    def update_commit_data(self, pr_commit: InsightsCommit, repo_id: int | None):
        pr_commit.set_project_id(repo_id)
        if pr_commit.author is None:
            pr_commit.set_author_id(None)
        else:
            pr_commit.set_author_id(self.user_controller.load_user(pr_commit.author))

        if pr_commit.committer is None:
            pr_commit.set_committer_id(None)
        else:
            pr_commit.set_committer_id(
                self.user_controller.load_user(pr_commit.committer)
            )

    def find_commit_sha(self, sha: str) -> int | None:
        return self.temp_db.find_commit_id(
            sha=sha,
        )
