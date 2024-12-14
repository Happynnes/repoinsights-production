from .user import InsightsUser
from typing import Dict, Any


class InsightsRepository:
    def __init__(self, repo: Dict[str, Any]) -> None:
        self.url = repo["url"]
        self.owner = InsightsUser(repo["owner"]) if repo["owner"] else None
        self.name = repo["name"]
        self.description = repo["description"][:255] if repo["description"] else None
        self.language = repo["language"]
        self.created_at = repo["created_at"]
        self.forked_from = False if repo["fork"] is False else True
        self.forked_from_id = None
        self.private = self.check_private(repo["visibility"])
        self.owner_id = None

    def set_forked_from_id(self, forked_from_id: int) -> None:
        self.forked_from_id = forked_from_id

    def set_owner_id(self, owner_id: int) -> None:
        self.owner_id = owner_id

    def set_repo_id(self, id: int) -> None:
        self.id = id

    def check_private(self, visibility: str) -> bool:
        if visibility == "public":
            return False
        elif visibility == "private":
            return True
        else:
            return False

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "name": self.name,
            "owner_id": self.owner_id,
            "description": self.description,
            "language": self.language,
            "created_at": self.created_at,
            "forked_from": self.forked_from_id,
            "private": self.private,
        }
