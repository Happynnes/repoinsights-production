from services.extract_service.load_module.db_connector.models import (
    User,
    Project,
    Commit,
    CommitComment,
    CommitParent,
    Follower,
    Fork,
    Issue,
    IssueComment,
    IssueEvent,
    IssueLabel,
    OrganizationMember,
    ProjectCommit,
    ProjectMember,
    PullRequest,
    PullRequestComment,
    PullRequestCommit,
    PullRequestHistory,
    RepoLabel,
    RepoMilestone,
    Watcher,
    Extraction,
)
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
    DBConnector,
)
from pprint import pprint
from loguru import logger

from typing import List, TypeVar, Type

T = TypeVar("T")


class DeleteFromTemp:
    def __init__(self, uuid) -> None:
        connector = DBConnector()
        self.uuid = uuid
        self.db = DatabaseHandler(connector, self.uuid)

    def _delete_items(self, item_class: Type[T]) -> None:
        self.db.session_temp.query(item_class).filter_by(ext_ref_id=self.uuid).delete()
        self.db.session_temp.commit()

    def delete_users(self) -> None:
        self._delete_items(User)

    def delete_projects(self) -> None:
        self._delete_items(Project)

    def delete_extractions(self) -> None:
        self._delete_items(Extraction)

    def delete_project_members(self) -> None:
        self._delete_items(ProjectMember)

    def delete_commits(self) -> None:
        self._delete_items(Commit)

    def delete_issues(self) -> None:
        self._delete_items(Issue)

    def delete_prs(self) -> None:
        self._delete_items(PullRequest)

    def delete_commit_comments(self) -> None:
        self._delete_items(CommitComment)

    def delete_commit_parents(self) -> None:
        self._delete_items(CommitParent)

    def delete_issue_comments(self) -> None:
        self._delete_items(IssueComment)

    def delete_issue_events(self) -> None:
        self._delete_items(IssueEvent)

    def delete_issue_labels(self) -> None:
        self._delete_items(IssueLabel)

    def delete_pr_comments(self) -> None:
        self._delete_items(PullRequestComment)

    def delete_pr_history(self) -> None:
        self._delete_items(PullRequestHistory)

    def delete_labels(self) -> None:
        self._delete_items(RepoLabel)

    def delete_milestones(self) -> None:
        self._delete_items(RepoMilestone)

    def delete_watchers(self) -> None:
        self._delete_items(Watcher)

    def delete_followers(self) -> None:
        self._delete_items(Follower)

    def delete_pr_commits(self) -> None:
        self._delete_items(PullRequestCommit)

    def delete_project_commits(self) -> None:
        self._delete_items(ProjectCommit)

    def delete_all(self) -> None:
        self.delete_pr_commits()
        self.delete_followers()
        self.delete_watchers()
        self.delete_milestones()
        self.delete_labels()
        self.delete_pr_history()
        self.delete_pr_comments()
        self.delete_issue_labels()
        self.delete_issue_events()
        self.delete_issue_comments()
        self.delete_commit_parents()
        self.delete_commit_comments()
        self.delete_prs()
        self.delete_issues()
        self.delete_project_commits()
        self.delete_commits()
        self.delete_project_members()
        self.delete_extractions()
        self.delete_projects()
        self.delete_users()
