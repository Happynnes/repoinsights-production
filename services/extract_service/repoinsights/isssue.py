from datetime import datetime
from .comment import InsightsIssueComment
from .issue_event import InsightsIssueEvent
from .label import InsightsLabel
from .user import InsightsUser
from typing import List, Union, Any, Dict


class InsightsIssue:
    def __init__(self, issue: Dict[str, Any]) -> None:
        self.reporter_id = None
        self.created_at = issue["created_at"]
        self.updated_at = issue["updated_at"]
        self.closed_at = issue["closed_at"]
        self.title = issue["title"]
        self.state = issue["state"]
        self.issue_id = issue["number"]
        self.pull_request = True if issue.get("pull_requests") else False
        self.pull_request_id = None
        self.reporter = InsightsUser(issue["user"])
        self.assignee = InsightsUser(issue["assignee"]) if issue["assignee"] else None
        self.assignee_id = None
        self.labels = self.__set_issue_labels(issue["labels"])

    def set_id(self, id: int):
        self.id = id

    def set_project_id(self, repo_id: int):
        self.repo_id = repo_id

    def set_reporter_id(self, user_id: int):
        self.reporter_id = user_id

    def set_assignee_id(self, user_id: int):
        self.assignee_id = user_id

    def set_pull_requests_id(self, pr_id: int):
        self.pull_request_id = pr_id

    def set_labels(self, labels):
        self.labels = [InsightsLabel(label) for label in labels]

    def get_labels(self):
        print("Getting labels")
        return self.labels

    def set_comments(self, comments: list[InsightsIssueComment]):
        self.comments = comments

    def set_events(self, events: list[InsightsIssueEvent]):
        self.events = events

    def __set_issue_labels(self, labels: Dict[str, Any]):
        issue_labels = []
        for label in labels:
            issue_labels.append(InsightsLabel(label))
        return issue_labels

    def get_comments(self) -> list[InsightsIssueComment]:
        return self.comments

    def to_dict(self) -> dict:
        return {
            "repo_id": self.repo_id,
            "reporter_id": self.reporter_id,
            "assignee_id": self.assignee_id,
            "issue_id": str(self.issue_id),
            "pull_request": self.pull_request,
            "pull_request_id": self.pull_request_id,
            "created_at": self.created_at,
        }
