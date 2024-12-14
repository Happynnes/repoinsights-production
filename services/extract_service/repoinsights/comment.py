from typing import Any, Dict, Union
from services.extract_service.repoinsights.user import InsightsUser


class InsightsComment:
    def __init__(
        self,
        id,
        body,
        created_at,
        updated_at,
        user: Union[Dict[str, Any], None] = None,
    ):
        self.body = body if len(body) <= 256 else body[:256]
        self.created_at = created_at
        self.updated_at = updated_at
        self.author = InsightsUser(user) if user else None
        self.id = id
        self.created_at = created_at

    def set_user_id(self, user_id: Union[int, None]):
        self.user_id = user_id


class InsightsPullRequestComment(InsightsComment):
    def __init__(self, comment: Dict[str, Any]):
        super().__init__(
            body=comment["body"],
            user=comment["user"] if comment["user"] else None,
            created_at=comment["created_at"],
            updated_at=comment["updated_at"],
            id=comment["id"],
        )
        self.position = comment["position"]
        self.commit_sha = comment["commit_id"]

    def set_pull_request_id(self, pullreq_id: int):
        self.pullreq_id = pullreq_id

    def set_user_id(self, user_id: Union[int, None]):
        self.user_id = user_id

    def set_commit_id(self, commit_id: Union[int, None]):
        self.commit_id = commit_id

    def to_dict(self):
        return {
            "pull_request_id": self.pullreq_id,
            "user_id": self.user_id,
            "comment_id": str(self.id),
            "position": self.position,
            "body": self.body,
            "commit_id": self.commit_id,
            "created_at": self.created_at,
        }


class InsightsIssueComment(InsightsComment):
    def __init__(self, comment: Dict[str, Any]):
        super().__init__(
            body=comment["body"],
            user=comment["user"] if comment["user"] else None,
            created_at=comment["created_at"],
            updated_at=comment["updated_at"],
            id=comment["id"],
        )

    def set_issue_id(self, issue_id: int):
        self.issue_id = issue_id

    def to_dict(self):
        return {
            "issue_id": self.issue_id,
            "user_id": self.user_id,
            "comment_id": str(self.id),
            "created_at": self.created_at,
        }


class InsightsCommitComment(InsightsComment):
    def __init__(self, comment: Dict[str, Any]):
        super().__init__(
            body=comment["body"],
            user=comment["user"] if comment["user"] else None,
            created_at=comment["created_at"],
            updated_at=comment["updated_at"],
            id=comment["id"],
        )
        self.line = comment["line"]
        self.position = comment["position"]
        self.comment_id = comment["id"]

    def set_commit_id(self, commit_id: int):
        self.commit_id = commit_id

    def to_dict(self):
        return {
            "commit_id": self.commit_id,
            "user_id": self.user_id,
            "body": self.body,
            "line": self.line,
            "position": self.position,
            "comment_id": self.id,
            "created_at": self.created_at,
        }
