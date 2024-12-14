from services.traspaso_service.db_connector.models import (
    User,
    Project,
    Commit,
    CommitComment,
    CommitParent,
    Follower,
    Fork,
    Issue,
    IssueComment,
    IssueEvent,
    IssueLabel,
    OrganizationMember,
    ProjectCommit,
    ProjectMember,
    PullRequest,
    PullRequestComment,
    PullRequestCommit,
    PullRequestHistory,
    RepoLabel,
    RepoMilestone,
    Watcher,
    Extraction,
)


class EntityData:
    def __init__(self, cache) -> None:
        self.cache = cache

        self.entity_data = {
            User: {
                "search_keys": ["login"],
                "add_keys": [
                    "login",
                    "name",
                    "email",
                    "company",
                    "location",
                    "created_at",
                    "ext_ref_id",
                    "type",
                ],
                "cache_map": self.cache.user_id_map,
            },
            Project: {
                "search_keys": ["name", ("owner_id", self.cache.user_id_map, User)],
                "add_keys": [
                    "url",
                    ("owner_id", self.cache.user_id_map, User),
                    "name",
                    "description",
                    "language",
                    "created_at",
                    "ext_ref_id",
                    ("forked_from", self.cache.project_id_map, Project),
                    "deleted",
                    "private",
                ],
                "cache_map": self.cache.project_id_map,
            },
            Extraction: {
                "search_keys": [
                    ("project_id", self.cache.project_id_map, Project),
                    "date",
                ],
                "add_keys": [
                    ("project_id", self.cache.project_id_map, Project),
                    "date",
                    "ext_ref_id",
                ],
            },
            ProjectMember: {
                "search_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    ("user_id", self.cache.user_id_map, User),
                ],
                "add_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    ("user_id", self.cache.user_id_map, User),
                    "created_at",
                    "ext_ref_id",
                ],
            },
            RepoLabel: {
                "search_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    "name",
                ],
                "add_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    "name",
                    "ext_ref_id",
                ],
                "cache_map": self.cache.label_id_map,
            },
            RepoMilestone: {
                "search_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    "name",
                ],
                "add_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    "name",
                    "ext_ref_id",
                ],
            },
            Watcher: {
                "search_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    ("user_id", self.cache.user_id_map, User),
                ],
                "add_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    ("user_id", self.cache.user_id_map, User),
                    "created_at",
                    "ext_ref_id",
                ],
            },
            Follower: {
                "search_keys": [
                    ("user_id", self.cache.user_id_map, User),
                    ("follower_id", self.cache.user_id_map, User),
                ],
                "add_keys": [
                    ("user_id", self.cache.user_id_map, User),
                    ("follower_id", self.cache.user_id_map, User),
                    "created_at",
                    "ext_ref_id",
                ],
            },
            Commit: {
                "search_keys": [
                    # ("repo_id", self.cache.project_id_map), # TODO FIX REPOS MIGRATED
                    "sha",
                ],
                "add_keys": [
                    "sha",
                    ("author_id", self.cache.user_id_map, User),
                    ("committer_id", self.cache.user_id_map, User),
                    ("project_id", self.cache.project_id_map, Project),
                    "created_at",
                    "message",
                    "ext_ref_id",
                ],
                "cache_map": self.cache.commit_id_map,
            },
            CommitComment: {
                "search_keys": [
                    ("commit_id", self.cache.commit_id_map, Commit),
                    ("user_id", self.cache.user_id_map, User),
                ],
                "add_keys": [
                    ("commit_id", self.cache.commit_id_map, Commit),
                    ("user_id", self.cache.user_id_map, User),
                    "body",
                    "line",
                    "position",
                    "comment_id",
                    "ext_ref_id",
                    "created_at",
                ],
            },
            CommitParent: {
                "search_keys": [
                    ("commit_id", self.cache.commit_id_map, Commit),
                    ("parent_id", self.cache.commit_id_map, Commit),
                ],
                "add_keys": [
                    ("commit_id", self.cache.commit_id_map, Commit),
                    ("parent_id", self.cache.commit_id_map, Commit),
                    "ext_ref_id",
                ],
            },
            PullRequest: {
                "search_keys": [
                    "pullreq_id",
                    ("base_repo_id", self.cache.project_id_map, Project),
                ],
                "add_keys": [
                    ("head_repo_id", self.cache.project_id_map, Project),
                    ("base_repo_id", self.cache.project_id_map, Project),
                    ("head_commit_id", self.cache.commit_id_map, Commit),
                    ("base_commit_id", self.cache.commit_id_map, Commit),
                    ("user_id", self.cache.user_id_map, User),
                    "pullreq_id",
                    "intra_branch",
                    "merged",
                    "ext_ref_id",
                ],
                "cache_map": self.cache.pull_request_id_map,
            },
            PullRequestComment: {
                "search_keys": [
                    ("pull_request_id", self.cache.pull_request_id_map, PullRequest),
                    ("user_id", self.cache.user_id_map, User),
                    "comment_id",
                    ("commit_id", self.cache.commit_id_map, Commit),
                ],
                "add_keys": [
                    ("pull_request_id", self.cache.pull_request_id_map, PullRequest),
                    ("user_id", self.cache.user_id_map, User),
                    "comment_id",
                    "position",
                    "body",
                    ("commit_id", self.cache.commit_id_map, Commit),
                    "created_at",
                    "ext_ref_id",
                ],
            },
            PullRequestCommit: {
                "search_keys": [
                    ("pull_request_id", self.cache.pull_request_id_map, PullRequest),
                    ("commit_id", self.cache.commit_id_map, Commit),
                ],
                "add_keys": [
                    ("pull_request_id", self.cache.pull_request_id_map, PullRequest),
                    ("commit_id", self.cache.commit_id_map, Commit),
                    "ext_ref_id",
                ],
            },
            PullRequestHistory: {
                "search_keys": [
                    ("pull_request_id", self.cache.pull_request_id_map, PullRequest),
                    "action",
                ],
                "add_keys": [
                    ("pull_request_id", self.cache.pull_request_id_map, PullRequest),
                    "created_at",
                    ("actor_id", self.cache.user_id_map, User),
                    "ext_ref_id",
                    "action",
                ],
            },
            Issue: {
                "search_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    "issue_id",
                ],
                "add_keys": [
                    ("repo_id", self.cache.project_id_map, Project),
                    ("reporter_id", self.cache.user_id_map, User),
                    ("assignee_id", self.cache.user_id_map, User),
                    "issue_id",
                    "pull_request",
                    ("pull_request_id", self.cache.pull_request_id_map, PullRequest),
                    "created_at",
                    "ext_ref_id",
                ],
                "cache_map": self.cache.issue_id_map,
            },
            IssueComment: {
                "search_keys": [
                    ("issue_id", self.cache.issue_id_map, Issue),
                    ("user_id", self.cache.user_id_map, User),
                    "comment_id",
                ],
                "add_keys": [
                    ("issue_id", self.cache.issue_id_map, Issue),
                    ("user_id", self.cache.user_id_map, User),
                    "comment_id",
                    "created_at",
                    "ext_ref_id",
                ],
            },
            IssueEvent: {
                "search_keys": [
                    ("issue_id", self.cache.issue_id_map, Issue),
                    "action",
                ],
                "add_keys": [
                    "event_id",
                    ("issue_id", self.cache.issue_id_map, Issue),
                    ("actor_id", self.cache.user_id_map, User),
                    "action",
                    "action_specific",
                    "created_at",
                    "ext_ref_id",
                ],
                "id": "event_id",
            },
            IssueLabel: {
                "search_keys": [
                    ("issue_id", self.cache.issue_id_map, Issue),
                    ("label_id", self.cache.label_id_map, RepoLabel),
                ],
                "add_keys": [
                    ("issue_id", self.cache.issue_id_map, Issue),
                    ("label_id", self.cache.label_id_map, RepoLabel),
                    "ext_ref_id",
                ],
                "id": "label_id",
            },
        }

    def get_entity_data(self):
        return self.entity_data
