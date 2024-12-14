from typing import Any, Dict
from services.extract_service.repoinsights.user import InsightsUser
from services.extract_service.repoinsights.label import InsightsLabel


class InsightsIssueEvent:
    def __init__(self, event: Dict[str, Any]) -> None:
        self.event_id = event["id"]
        self.action = event["event"]
        self.action_specific = event["commit_id"]
        self.created_at = event["created_at"]
        self.actor = InsightsUser(event["actor"]) if event["actor"] else None

    def set_issue_id(self, issue_id: int):
        self.issue_id = issue_id

    def set_actor_id(self, actor_id: int):
        self.actor_id = actor_id

    def to_dict(self):
        return {
            "event_id": str(self.event_id),
            "issue_id": self.issue_id,
            "actor_id": self.actor_id,
            "action": self.action,
            "action_specific": self.action_specific,
            "created_at": self.created_at,
        }
