from datetime import datetime
from .connector import DBConnector
from .models import (
    User,
    Project,
    Commit,
    CommitParent,
    Issue,
    IssueComment,
    PullRequest,
    PullRequestComment,
    Watcher,
    ProjectMember,
    CommitComment,
    PullRequestHistory,
    ProjectCommit,
    IssueEvent,
    RepoLabel,
    IssueLabel,
    RepoMilestone,
    Extraction,
    PullRequestCommit,
)
from services.extract_service.repoinsights.commit import InsightsCommit
from services.extract_service.repoinsights.user import InsightsUser
from services.extract_service.repoinsights.repository import InsightsRepository
from services.extract_service.repoinsights.pull_request import InsightsPullRequest
from services.extract_service.repoinsights.isssue import InsightsIssue
from services.extract_service.repoinsights.issue_event import InsightsIssueEvent
from services.extract_service.repoinsights.label import InsightsLabel
from services.extract_service.repoinsights.milestone import InsightsMilestone
from services.extract_service.repoinsights.comment import (
    InsightsCommitComment,
    InsightsPullRequestComment,
    InsightsIssueComment,
)
from services.extract_service.load_module.db_connector.check_entity import entity_data
from pprint import pprint
from typing import List, Union, Dict, Any
from sqlalchemy.orm import sessionmaker
from typing import Union, List, Optional
from loguru import logger


class HandleError(Exception):
    pass


class DatabaseHandler:
    def __init__(self, connector: DBConnector, uuid: str):
        self.connector = connector
        self.session_maker = sessionmaker(bind=connector.engine)
        self.session_temp = self.session_maker()
        self.uuid = uuid

    def get_or_create(
        self,
        model,
        create: Optional[bool] = True,
        **kwargs,
    ):
        search_params = entity_data[model.__name__]["search_keys"]
        search = {key: kwargs[key] for key in search_params}
        instance = self.session_temp.query(model).filter_by(**search).first()
        if instance:
            logger.debug("Instance already exists")
            return instance
        elif create:
            try:
                logger.debug("Creating new instance")
                kwargs["ext_ref_id"] = self.uuid
                instance = model(**kwargs)
                self.session_temp.add(instance)
                self.session_temp.commit()
                return instance
            except Exception as e:
                logger.error("Error creating")
                raise HandleError(e)
        else:
            logger.debug("Instance does not exist and not created")
            return None

    def create_watchers(self, watchers: List[InsightsUser], project_id: int):
        watchers_db = []
        watcher: InsightsUser
        for watcher in watchers:
            user = self.get_or_create(User, **watcher.to_dict())
            user_id = int(user.id)  # type: ignore

            existing_watcher = (
                self.session_temp.query(Watcher)
                .filter_by(repo_id=project_id, user_id=user_id)
                .first()
            )
            if not existing_watcher:
                new_watcher = Watcher(
                    repo_id=project_id, user_id=user_id, created_at=watcher.created_at
                )

                watchers_db.append(new_watcher)

        self.session_temp.add_all(watchers_db)
        self.session_temp.commit()

    def create_members(self, member_data: Dict[str, Any]):
        existing_member = self.get_or_create(ProjectMember, **member_data)
        return int(existing_member.id)  # type: ignore

    def create_label(self, label_data: InsightsLabel):
        existing_label = self.get_or_create(RepoLabel, **label_data.to_dict())
        return int(existing_label.id)  # type: ignore

    def create_issue_label_relation(self, issue_id: int, label_id: int):
        self.get_or_create(IssueLabel, issue_id=issue_id, label_id=label_id)

    def create_project(self, repository: InsightsRepository):
        existing_project = self.get_or_create(Project, **repository.to_dict())
        return int(existing_project.id)  # type: ignore

    def create_user(self, user: InsightsUser) -> int:
        existing_user = self.get_or_create(User, **user.to_dict())
        return int(existing_user.id)  # type: ignore

    def create_commit(self, commit: InsightsCommit):
        existing_commit = self.get_or_create(Commit, **commit.to_dict())
        return int(existing_commit.id)  # type: ignore

    def create_project_commit(self, project_id: int, commit_id: int):
        self.get_or_create(ProjectCommit, project_id=project_id, commit_id=commit_id)

    def create_commit_parent_relation(self, commit_id: int, parent_id: int):
        existing_relation = (
            self.session_temp.query(CommitParent)
            .filter_by(commit_id=commit_id, parent_id=parent_id)
            .first()
        )
        if not existing_relation:
            new_relation = CommitParent(commit_id=commit_id, parent_id=parent_id)
            self.session_temp.add(new_relation)
            return new_relation
        else:
            logger.warning(
                f"Relation commit-parent already exists: {commit_id} - {parent_id}"
            )
            return None

    def create_commit_parents(self, commit_id: int, parents: list):
        parent_sha: str
        commits_parents = []
        for parent_sha in parents:
            parent_commit = self.get_or_create(Commit, sha=parent_sha)
            parent_id = int(parent_commit.id)  # type: ignore

            commit_parent_relation = self.create_commit_parent_relation(
                commit_id, parent_id
            )
            if commit_parent_relation:
                commits_parents.append(commit_parent_relation)
            else:
                logger.info(f"Parent commit not found: {parent_sha}")

        self.session_temp.add_all(commits_parents)
        self.session_temp.commit()

    def create_commit_comments(self, commit_id: int, comments: list):
        comment: InsightsCommitComment
        for comment in comments:
            if comment.author:
                user = self.get_or_create(User, **comment.author.to_dict())
                user_id = int(user.id)  # type: ignore
            else:
                user_id = None
            # add user_id to comment
            comment.set_user_id(user_id)
            comment.set_commit_id(commit_id)
            self.get_or_create(CommitComment, **comment.to_dict())

    def create_pull_request(self, pr: InsightsPullRequest):
        existing_pr = self.get_or_create(PullRequest, **pr.to_dict())
        return int(existing_pr.id)  # type: ignore

    def create_pull_request_comment(self, comment: InsightsPullRequestComment):
        self.get_or_create(PullRequestComment, **comment.to_dict())

    def create_pull_request_commit(self, pr_id: int, commit_id: int):
        self.get_or_create(
            PullRequestCommit, pull_request_id=pr_id, commit_id=commit_id
        )

    def create_pull_request_history(self, pr: Dict[str, Any]):
        existing_pr = self.get_or_create(PullRequestHistory, **pr)
        return int(existing_pr.id)  # type: ignore

    def create_issue(self, issue: InsightsIssue):
        existing_issue = self.get_or_create(Issue, **issue.to_dict())
        return int(existing_issue.id)  # type: ignore

    def create_issue_comment(self, comment: InsightsIssueComment):
        self.get_or_create(IssueComment, **comment.to_dict())

    def create_issue_event(self, event: InsightsIssueEvent):
        self.get_or_create(IssueEvent, **event.to_dict())

    def find_pr_id(self, **kwargs) -> int:
        pr = self.get_or_create(PullRequest, create=False, **kwargs)
        return int(pr.id)  # type: ignore

    def find_commit_id(self, **kwargs) -> int | None:
        commit = self.get_or_create(Commit, **kwargs, create=False)
        return int(commit.id) if commit else None  # type: ignore

    def create_milestone(self, milestone: InsightsMilestone):
        existing_milestone = self.get_or_create(RepoMilestone, **milestone.to_dict())
        return int(existing_milestone.id)  # type: ignore

    def create_extraction_project(self, project_id: int):
        extraction = self.get_or_create(
            model=Extraction, project_id=project_id, date=datetime.now()
        )
        return int(extraction.id)  # type: ignore

    def close(self):
        self.session_temp.close()
