from typing import Dict, List

COMMIT = "commit"
LANGS = "langs"
USER = "user"
SORT = "sort"
PERSONAL = "personal"

measurement_types = {
    "count": None,
    "hours": "h",
    "days": "d",
    "weeks": "w",
    "boolean": None,
    "percentage": "%",
}

rating = Dict[str, Dict[str, int | float | bool]]
weight = Dict[str, int | float | bool]
score = Dict[str, int | str | float | rating | weight]
metric_scores: List[score]

N = 5
metric_scores = [
    {
        "name": "issue_closed_per_day",
        "title": "Issues cerrados por día",
        "weight": {"value": 0.2, "invert": False},
        "rating": {
            "F": {"max": 7, "min": 0},
            "C": {"max": 30, "min": 7},
            "B": {"max": 60, "min": 30},
            "A": {"max": 1000000, "min": 60},
        },
    },
    {
        "name": "hero_project",
        "title": "Hero project",
        "weight": {"value": 0.2, "invert": True},
        "show_value": False,
        "rating": {"A": {"max": 0.50, "min": 0}, "F": {"max": 1, "min": 0.50}},
    },
    {
        "name": "time_to_first_response_issues_avg",
        "title": "Tiempo primera respuesta issue",
        "weight": {"value": 0.2, "invert": True},
        "rating": {"A": {"max": 20, "min": 0}, "F": {"max": 1000000, "min": 20}},
    },
    {
        "name": "active_days_coverage",
        "title": "Días activos",
        "weight": {"value": 0.2, "invert": False},
        "rating": {
            "A": {"max": 1, "min": 0.80},
            "B": {"max": 0.80, "min": 0.60},
            "C": {"max": 0.60, "min": 0.40},
            "D": {"max": 0.40, "min": 0.20},
            "E": {"max": 0.20, "min": 0.1},
            "F": {"max": 0.1, "min": 0},
        },
    },
    {
        "name": "commits_in_pr_avg",
        "title": "Commits en PR",
        "weight": {"value": 0.2, "invert": False},
        "rating": {"A": {"max": 250, "min": 0}},
    },
]
