import os

METRICS_DIR = os.path.dirname(os.path.abspath(__file__)) + "/metrics/"
REPO_METRICS = "repository"
ISSUES_METRICS = "issues"
PULL_REQUESTS_METRICS = "pull_requests"
DEVELOPERS_METRICS = "developers"

METRICS_GROUPS = [
    REPO_METRICS,
    ISSUES_METRICS,
    PULL_REQUESTS_METRICS,
    DEVELOPERS_METRICS,
]

REPO_TABLE = "project_metrics"
ISSUES_TABLE = "issue_metrics"
PULL_REQUESTS_TABLE = "pull_request_metrics"
DEVELOPERS_TABLE = "user_metrics"


METRICS_TABLE_NAME_MAP = {
    REPO_METRICS: {
        "table": REPO_TABLE,
        "params": ["metric_id", "extraction_id", "value"],
    },
    ISSUES_METRICS: {
        "table": ISSUES_TABLE,
        "params": ["metric_id", "extraction_id", "issue_id", "value"],
    },
    PULL_REQUESTS_METRICS: {
        "table": PULL_REQUESTS_TABLE,
        "params": ["metric_id", "extraction_id", "pull_request_id", "value"],
    },
    DEVELOPERS_METRICS: {
        "table": DEVELOPERS_TABLE,
        "params": ["metric_id", "extraction_id", "user_id", "value"],
    },
}
