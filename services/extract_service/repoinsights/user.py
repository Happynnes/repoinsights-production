from pprint import pprint
from typing import List, Optional, Union, Dict, Any
from ..utils.utils import get_user_type


class InsightsUser:
    def __init__(self, user: Dict[str, Any]) -> None:
        self.login = user["login"]
        self.name = user["name"]
        self.company = user["company"]
        self.location = user["location"]
        self.email = user["email"]
        self.created_at = user["created_at"]
        self.type = get_user_type(user["type"])

    def to_dict(self) -> dict:
        return {
            "login": self.login,
            "name": self.name,
            "company": self.company,
            "location": self.location,
            "email": self.email,
            "created_at": self.created_at,
            "type": self.type,
        }
