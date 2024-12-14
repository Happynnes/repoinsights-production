from typing import Any, Dict, List
from services.extract_service.excepctions.exceptions import ExtractDataResulstsError


class ResultSorter:
    @staticmethod
    def sort(results: List[Dict[str, Any]]):
        order = {
            "project": 1,
            "owner": 2,
            "commit": 3,
            "pull_request": 4,
            "issue": 5,
            "watchers": 6,
            "members": 7,
            "milestones": 8,
            "labels": 9,
        }
        try:
            sorted_results = sorted(results, key=lambda x: order[x["name"]])
            return sorted_results
        except KeyError as e:
            raise ExtractDataResulstsError(
                f"Results must contain a 'name' key. Error: {e}"
            )
