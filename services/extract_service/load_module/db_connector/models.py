from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
    TIMESTAMP,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

pk_projects = "projects.id"
pk_users = "users.id"
pk_commits = "commits.id"
pk_issues = "issues.id"
pk_pull_requests = "pull_requests.id"


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey(pk_projects), nullable=False)
    date = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    project = relationship("Project", back_populates="extractions")


class CommitComment(Base):
    __tablename__ = "commit_comments"

    id = Column(Integer, primary_key=True)
    commit_id = Column(Integer, ForeignKey(pk_commits), nullable=False)
    user_id = Column(Integer, ForeignKey(pk_users), nullable=False)
    body = Column(String(256))
    line = Column(Integer)
    position = Column(Integer)
    comment_id = Column(Integer, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)

    commit = relationship("Commit", back_populates="commit_comments")
    user = relationship("User", back_populates="commit_comments")


class CommitParent(Base):
    __tablename__ = "commit_parents"

    commit_id = Column(Integer, ForeignKey(pk_commits), primary_key=True)
    parent_id = Column(Integer, ForeignKey(pk_commits), primary_key=True)
    ext_ref_id = Column(String(32), nullable=False)

    __table_args__ = (Index("idx_16399_parent_id", parent_id),)


class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True)
    sha = Column(String(40))
    author_id = Column(Integer, ForeignKey(pk_users))
    committer_id = Column(Integer, ForeignKey(pk_users))
    project_id = Column(Integer, ForeignKey(pk_projects))
    created_at = Column(TIMESTAMP, nullable=False)
    message = Column(String(256))
    ext_ref_id = Column(String(32), nullable=False)

    commit_comments = relationship("CommitComment", back_populates="commit")
    project = relationship("Project", back_populates="commits")
    project_commits = relationship("ProjectCommit", back_populates="commit")


class Follower(Base):
    __tablename__ = "followers"

    user_id = Column(Integer, ForeignKey(pk_users), primary_key=True)
    follower_id = Column(Integer, ForeignKey(pk_users), primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="followers")
    follower = relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )


class Fork(Base):
    __tablename__ = "forks"

    forked_project_id = Column(Integer, ForeignKey(pk_projects), primary_key=True)
    forked_from_id = Column(Integer, ForeignKey(pk_projects), primary_key=True)
    fork_id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    forked_project = relationship(
        "Project", foreign_keys=[forked_project_id], back_populates="forks"
    )
    forked_from_project = relationship("Project", foreign_keys=[forked_from_id])


class IssueComment(Base):
    __tablename__ = "issue_comments"

    issue_id = Column(Integer, ForeignKey(pk_issues), primary_key=True)
    user_id = Column(Integer, ForeignKey(pk_users), primary_key=True)
    comment_id = Column(Text, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    user = relationship("User", back_populates="issue_comments")


class IssueEvent(Base):
    __tablename__ = "issue_events"

    event_id = Column(Text, primary_key=True)
    issue_id = Column(Integer, ForeignKey(pk_issues), nullable=False)
    actor_id = Column(Integer, ForeignKey(pk_users), nullable=False)
    action = Column(String(255), nullable=False)
    action_specific = Column(String(50))
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    issue = relationship("Issue", back_populates="issue_events")
    user = relationship("User", back_populates="issue_events")


class IssueLabel(Base):
    __tablename__ = "issue_labels"

    label_id = Column(Integer, default=0, primary_key=True)
    issue_id = Column(Integer, ForeignKey(pk_issues), default=0, primary_key=True)
    ext_ref_id = Column(String(32), nullable=False)


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey(pk_projects))
    reporter_id = Column(Integer, ForeignKey(pk_users))
    assignee_id = Column(Integer, ForeignKey(pk_users))
    issue_id = Column(Text, nullable=False)
    pull_request = Column(Boolean, nullable=False)
    pull_request_id = Column(Integer)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    project = relationship("Project", back_populates="issues")
    reporter = relationship(
        "User", foreign_keys=[reporter_id], back_populates="reported_issues"
    )
    assignee = relationship(
        "User", foreign_keys=[assignee_id], back_populates="assigned_issues"
    )
    issue_events = relationship("IssueEvent", back_populates="issue")


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    org_id = Column(Integer, ForeignKey(pk_users), primary_key=True)
    user_id = Column(Integer, ForeignKey(pk_users), primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)


class ProjectCommit(Base):
    __tablename__ = "project_commits"

    project_id = Column(Integer, ForeignKey(pk_projects), primary_key=True)
    commit_id = Column(Integer, ForeignKey(pk_commits), primary_key=True)
    ext_ref_id = Column(String(32), nullable=False)

    project = relationship("Project", back_populates="project_commits")
    commit = relationship("Commit", back_populates="project_commits")


class ProjectMember(Base):
    __tablename__ = "project_members"

    repo_id = Column(Integer, ForeignKey(pk_projects), primary_key=True)
    user_id = Column(Integer, ForeignKey(pk_users), primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    repo = relationship("Project", back_populates="project_members")
    user = relationship("User", back_populates="project_members")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    owner_id = Column(Integer, ForeignKey(pk_users))
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    language = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)
    forked_from = Column(Integer, nullable=True)
    deleted = Column(Boolean, default=False, nullable=False)
    private = Column(Boolean, default=False, nullable=False)

    owner = relationship("User", back_populates="projects")
    repo_labels = relationship("RepoLabel", back_populates="project")
    repo_milestones = relationship("RepoMilestone", back_populates="project")
    watchers = relationship("Watcher", back_populates="project")
    commits = relationship("Commit", back_populates="project")
    issues = relationship("Issue", back_populates="project")
    project_commits = relationship("ProjectCommit", back_populates="project")
    project_members = relationship("ProjectMember", back_populates="repo")
    pull_requests = relationship(
        "PullRequest",
        foreign_keys="PullRequest.base_repo_id",
        back_populates="base_repo",
    )
    forks = relationship(
        "Fork", foreign_keys="Fork.forked_project_id", back_populates="forked_project"
    )
    extractions = relationship("Extraction", back_populates="project")


class PullRequestComment(Base):
    __tablename__ = "pull_request_comments"

    pull_request_id = Column(Integer, ForeignKey(pk_pull_requests), primary_key=True)
    user_id = Column(Integer, ForeignKey(pk_users), primary_key=True)
    comment_id = Column(Text, primary_key=True)
    position = Column(Integer)
    body = Column(String(256))
    commit_id = Column(Integer, ForeignKey(pk_commits), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    user = relationship("User", back_populates="pull_request_comments")


class PullRequestCommit(Base):
    __tablename__ = "pull_request_commits"

    pull_request_id = Column(Integer, ForeignKey(pk_pull_requests), primary_key=True)
    commit_id = Column(Integer, ForeignKey(pk_commits), primary_key=True)
    ext_ref_id = Column(String(32), nullable=False)


class PullRequestHistory(Base):
    __tablename__ = "pull_request_history"

    id = Column(Integer, primary_key=True)
    pull_request_id = Column(Integer, ForeignKey(pk_pull_requests), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)
    action = Column(String(255), nullable=False)
    actor_id = Column(Integer, ForeignKey(pk_users))

    user = relationship("User", back_populates="pull_request_history")


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True)
    head_repo_id = Column(Integer, ForeignKey(pk_projects))
    base_repo_id = Column(Integer, ForeignKey(pk_projects), nullable=False)
    head_commit_id = Column(Integer, ForeignKey(pk_commits))
    base_commit_id = Column(Integer, ForeignKey(pk_commits), nullable=False)
    user_id = Column(Integer, ForeignKey(pk_users), nullable=False)
    pullreq_id = Column(Integer, nullable=False)
    intra_branch = Column(Boolean, nullable=False)
    merged = Column(Boolean, default=False, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    head_repo = relationship("Project", foreign_keys=[head_repo_id])
    base_repo = relationship("Project", foreign_keys=[base_repo_id])
    head_commit = relationship("Commit", foreign_keys=[head_commit_id])
    base_commit = relationship("Commit", foreign_keys=[base_commit_id])
    user = relationship("User", back_populates="pull_requests")


class RepoLabel(Base):
    __tablename__ = "repo_labels"

    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey(pk_projects))
    name = Column(String(24), nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    project = relationship("Project", back_populates="repo_labels")


class RepoMilestone(Base):
    __tablename__ = "repo_milestones"

    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey(pk_projects))
    name = Column(String(24), nullable=False)
    ext_ref_id = Column(String(32), nullable=False)

    project = relationship("Project", back_populates="repo_milestones")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False)
    name = Column(String(255))
    company = Column(String(255))
    location = Column(String(255))
    email = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(32), nullable=False)
    type = Column(String(255), default="USR", nullable=False)

    projects = relationship("Project", back_populates="owner")
    watchers = relationship("Watcher", back_populates="user")
    reported_issues = relationship(
        "Issue", foreign_keys=[Issue.reporter_id], back_populates="reporter"
    )
    assigned_issues = relationship(
        "Issue", foreign_keys=[Issue.assignee_id], back_populates="assignee"
    )
    pull_requests = relationship("PullRequest", back_populates="user")
    commit_comments = relationship("CommitComment", back_populates="user")
    issue_comments = relationship("IssueComment", back_populates="user")
    issue_events = relationship("IssueEvent", back_populates="user")
    followers = relationship(
        "Follower", foreign_keys="Follower.user_id", back_populates="user"
    )
    following = relationship(
        "Follower", foreign_keys="Follower.follower_id", back_populates="follower"
    )
    project_members = relationship("ProjectMember", back_populates="user")
    pull_request_comments = relationship("PullRequestComment", back_populates="user")
    pull_request_history = relationship("PullRequestHistory", back_populates="user")


class Watcher(Base):
    __tablename__ = "watchers"

    repo_id = Column(Integer, ForeignKey(pk_projects), primary_key=True)
    user_id = Column(Integer, ForeignKey(pk_users), primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    ext_ref_id = Column(String(24), nullable=False, default="0")

    project = relationship("Project", back_populates="watchers")
    user = relationship("User", back_populates="watchers")
