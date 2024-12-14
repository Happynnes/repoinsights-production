from services.traspaso_service.db_connector.models import (
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
from services.traspaso_service.db_connector.database_handler import DatabaseHandler
from pprint import pprint
from loguru import logger

from typing import List, TypeVar, Type

T = TypeVar("T")


class TempClient:
    def __init__(self, db: DatabaseHandler, uuid) -> None:
        self.db = db
        self.uuid = uuid

    def _get_items(self, item_class: Type[T]) -> List[T]:
        items = (
            self.db.session_temp.query(item_class).filter_by(ext_ref_id=self.uuid).all()
        )
        return items

    def get_users(self) -> List[User]:
        return self._get_items(User)

    def get_projects(self) -> List[Project]:
        return self._get_items(Project)

    def get_extractions(self) -> List[Extraction]:
        return self._get_items(Extraction)

    def get_project_members(self) -> List[ProjectMember]:
        return self._get_items(ProjectMember)

    def get_commits(self) -> List[Commit]:
        return self._get_items(Commit)

    def get_issues(self) -> List[Issue]:
        return self._get_items(Issue)

    def get_prs(self) -> List[PullRequest]:
        return self._get_items(PullRequest)

    def get_commit_comments(self) -> List[CommitComment]:
        return self._get_items(CommitComment)

    def get_commit_parents(self) -> List[CommitParent]:
        return self._get_items(CommitParent)

    def get_issue_comments(self) -> List[IssueComment]:
        return self._get_items(IssueComment)

    def get_issue_events(self) -> List[IssueEvent]:
        return self._get_items(IssueEvent)

    def get_issue_labels(self) -> List[IssueLabel]:
        return self._get_items(IssueLabel)

    def get_pr_comments(self) -> List[PullRequestComment]:
        return self._get_items(PullRequestComment)

    def get_pr_history(self) -> List[PullRequestHistory]:
        return self._get_items(PullRequestHistory)

    def get_labels(self) -> List[RepoLabel]:
        return self._get_items(RepoLabel)

    def get_milestones(self) -> List[RepoMilestone]:
        return self._get_items(RepoMilestone)

    def get_watchers(self) -> List[Watcher]:
        return self._get_items(Watcher)

    def get_followers(self) -> List[Follower]:
        return self._get_items(Follower)

    def get_pr_commits(self) -> List[PullRequestCommit]:
        return self._get_items(PullRequestCommit)
