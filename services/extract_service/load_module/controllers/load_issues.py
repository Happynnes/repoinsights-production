from typing import List
from loguru import logger
from services.extract_service.repoinsights.label import InsightsLabel
from services.extract_service.repoinsights.isssue import (
    InsightsIssue,
    InsightsIssueComment,
    InsightsIssueEvent,
)
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
)
from services.extract_service.load_module.controllers.load_users import (
    LoadUserController,
)


class LoadIssueController:
    def __init__(
        self,
        temp_db: DatabaseHandler,
        repo_id: int,
        user_controller: LoadUserController,
    ) -> None:
        self.temp_db = temp_db
        self.repo_id = repo_id
        self.user_controller = user_controller

    def load_issue_labels(self, project_id, issue_id, labels: List[InsightsLabel]):
        logger.debug("Loading issue labels")
        for label in labels:
            label.set_project_id(project_id)
            label_id = self.temp_db.create_label(label)
            self.temp_db.create_issue_label_relation(issue_id, label_id)

    def load_issues_data(self, issues: List[InsightsIssue]):
        for issue in issues:
            issue.set_project_id(self.repo_id)
            issue.set_reporter_id(self.user_controller.load_user(issue.reporter))
            if issue.assignee:
                issue.set_assignee_id(self.user_controller.load_user(issue.assignee))
            self.set_pr_id(issue)
            issue_id = self.temp_db.create_issue(issue)
            self.load_issue_labels(self.repo_id, issue_id, issue.labels)
            comment: InsightsIssueComment
            for comment in issue.comments:
                comment.set_issue_id(issue_id)
                if comment.author:
                    comment.set_user_id(self.user_controller.load_user(comment.author))
                self.temp_db.create_issue_comment(comment)
            event: InsightsIssueEvent
            for event in issue.events:
                event.set_issue_id(issue_id)
                if event.actor:
                    event.set_actor_id(self.user_controller.load_user(event.actor))
                    self.temp_db.create_issue_event(event)
                else:
                    logger.error("Event without actor")

    def set_pr_id(self, issue: InsightsIssue) -> None:
        if issue.pull_request is None or issue.pull_request == False:
            return
        else:
            pr_id = self.temp_db.find_pr_id(
                pullreq_id=issue.issue_id, base_repo_id=self.repo_id
            )
            if pr_id:
                issue.set_pull_requests_id(pr_id)
