from ..isssue import InsightsIssue
from ..milestone import InsightsMilestone
from ..issue_event import InsightsIssueEvent
from ..comment import InsightsIssueComment
from github.Issue import Issue
from datetime import datetime
from pprint import pprint
from typing import Union, List, Any, Dict
from services.extract_service.extract_module.extract_client import GitHubExtractor
import json
from ...utils.utils import get_int_from_dict


class InsightsIssueHandler:
    def __init__(self, repo: GitHubExtractor):
        self.repo = repo

    def _get_filtered_issues(self, issues):
        print("Getting GHIssues")
        issue_objects = [
            InsightsIssue(issue) for issue in issues if not issue.pull_request
        ]
        self.set_labels(issue_objects, issues)
        return issue_objects

    def get_issues(
        self,
        state="all",
        start_date: Union[datetime, None] = None,
        end_date: Union[datetime, None] = None,
    ):
        kwargs: Dict[str, Any] = {"state": state}
        if start_date:
            kwargs["since"] = start_date
        if end_date:
            kwargs["until"] = end_date
        issues = self.repo.obtener_issues(**kwargs)
        return [
            InsightsIssue(issue) for issue in issues if not issue.get("pull_request")
        ]

    def set_labels(self, issue_objects: list, issues):
        issue_obj: InsightsIssue
        issue: Issue
        for issue_obj, issue in zip(issue_objects, issues):
            issue_obj.set_labels(issue.labels)

    def get_milestones(self, state="all"):
        milestones = self.repo.obtener_milestone(state=state)
        milestone_objects = [InsightsMilestone(milestone) for milestone in milestones]
        return milestone_objects

    def get_issue_comments(self, issues: List[InsightsIssue]):
        comments = self.repo.obtener_issues_comments()
        issue: InsightsIssue
        for issue in issues:
            issue_comments = [
                InsightsIssueComment(comment)
                for comment in comments
                if get_int_from_dict(comment, "issue_url") == issue.issue_id
            ]
            issue.set_comments(issue_comments)

    def get_issue_events(self, issues: List[InsightsIssue]):
        for issue in issues:
            events = self.repo.obtener_issue_events(issue.issue_id)
            issue_events = [InsightsIssueEvent(event) for event in events if event]
            issue.set_events(issue_events)
