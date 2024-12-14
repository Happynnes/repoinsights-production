entity_data = {
    "User": {
        "search_keys": ["login"],
    },
    "Project": {
        "search_keys": ["name"],
    },
    "Extraction": {
        "search_keys": ["project_id", "date"],
    },
    "ProjectMember": {
        "search_keys": ["repo_id", "user_id"],
    },
    "RepoLabel": {
        "search_keys": ["repo_id", "name"],
    },
    "RepoMilestone": {
        "search_keys": ["repo_id", "name"],
    },
    "Watcher": {"search_keys": ["repo_id", "user_id"]},
    "Follower": {
        "search_keys": ["user_id", "follower_id"],
    },
    "Commit": {
        "search_keys": [
            "sha",
        ],
    },
    "CommitComment": {
        "search_keys": ["commit_id", "user_id"],
    },
    "CommitParent": {
        "search_keys": ["commit_id", "parent_id"],
    },
    "PullRequest": {
        "search_keys": ["pullreq_id", "base_repo_id"],
    },
    "PullRequestComment": {
        "search_keys": [
            "pull_request_id",
            "user_id",
            "comment_id",
            "commit_id",
        ],
    },
    "PullRequestCommit": {
        "search_keys": ["pull_request_id", "commit_id"],
    },
    "PullRequestHistory": {
        "search_keys": ["pull_request_id", "action"],
    },
    "Issue": {"search_keys": ["repo_id", "issue_id"]},
    "IssueComment": {
        "search_keys": ["issue_id", "user_id", "comment_id"],
    },
    "IssueEvent": {"search_keys": ["issue_id", "action"]},
    "IssueLabel": {
        "search_keys": ["issue_id", "label_id"],
    },
    "ProjectCommit": {
        "search_keys": ["project_id", "commit_id"],
    },
}
