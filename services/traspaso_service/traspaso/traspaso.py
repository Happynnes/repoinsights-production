from services.traspaso_service.traspaso.get_from_temp import TempClient
from services.traspaso_service.db_connector.database_handler import DatabaseHandler
from services.traspaso_service.add_to_consolidada import ConsolidatedClient
from loguru import logger


class Client:
    def __init__(self, db: DatabaseHandler, uuid: str) -> None:
        self.db = db
        self.uuid = uuid

    def migrate(self):
        """
        Obtener los datos de temportal con el uuid del proyecto
        """
        temp = TempClient(self.db, self.uuid)
        users = temp.get_users()
        projects = temp.get_projects()
        extractions = temp.get_extractions()
        project_members = temp.get_project_members()
        labels = temp.get_labels()
        milestones = temp.get_milestones()

        commits = temp.get_commits()
        commit_comments = temp.get_commit_comments()
        commit_parents = temp.get_commit_parents()
        issues = temp.get_issues()
        issue_comments = temp.get_issue_comments()
        issue_events = temp.get_issue_events()
        issue_labels = temp.get_issue_labels()
        prs = temp.get_prs()
        pr_comments = temp.get_pr_comments()
        pr_history = temp.get_pr_history()
        pr_commits = temp.get_pr_commits()
        watchers = temp.get_watchers()
        followers = temp.get_followers()

        logger.info("Migrando data... {uuid}", uuid=self.uuid)
        logger.debug(
            {
                "users": len(users),
                "watchers": len(watchers),
                "followers": len(followers),
                "projects": len(projects),
                "labels": len(labels),
                "milestones": len(milestones),
                "commits": len(commits),
                "commit_comments": len(commit_comments),
                "commit_parents": len(commit_parents),
                "issues": len(issues),
                "issue_comments": len(issue_comments),
                "issue_events": len(issue_events),
                "issue_labels": len(issue_labels),
                "prs": len(prs),
                "pr_comments": len(pr_comments),
                "pr_history": len(pr_history),
                "pr_commits": len(pr_commits),
            }
        )

        if (
            len(users) == 0
            and len(projects) == 0
            and len(extractions) == 0
            and len(project_members) == 0
            and len(labels) == 0
            and len(milestones) == 0
            and len(commits) == 0
            and len(commit_comments) == 0
            and len(commit_parents) == 0
            and len(issues) == 0
            and len(issue_comments) == 0
            and len(issue_events) == 0
            and len(issue_labels) == 0
            and len(prs) == 0
            and len(pr_comments) == 0
            and len(pr_history) == 0
            and len(watchers) == 0
            and len(followers) == 0
        ):
            logger.error("No data to traspasar")
            return

        consolidada = ConsolidatedClient(self.uuid, self.db)
        consolidada.add_users(users)

        consolidada.add_projects(projects)
        consolidada.add_extractions(extractions)
        consolidada.add_project_members(project_members)

        consolidada.add_labels(labels)
        consolidada.add_milestones(milestones)

        consolidada.add_watchers(watchers)
        consolidada.add_followers(followers)

        consolidada.add_commits(commits)
        consolidada.add_commit_comments(commit_comments)
        consolidada.add_commit_parents(commit_parents)

        consolidada.add_pull_requests(prs)
        consolidada.add_pull_request_comments(pr_comments)
        consolidada.add_pull_request_history(pr_history)
        consolidada.add_pull_request_commits(pr_commits)

        consolidada.add_issues(issues)
        consolidada.add_issue_comments(issue_comments)
        consolidada.add_issue_events(issue_events)
        consolidada.add_issue_labels(issue_labels)

        # DELETE FROM TEMPORAL IN REVERSE ORDER USING ext_ref_id
        # temp.delete_issue_labels()
        # temp.delete_issue_events()
        # temp.delete_issue_comments()
        # temp.delete_issues()
        # temp.delete_pr_commits()
        # temp.delete_pr_history()
        # temp.delete_pr_comments()
        # temp.delete_prs()
        # temp.delete_commit_parents()
        # temp.delete_commit_comments()
        # temp.delete_commits()
        # temp.delete_milestones()
        # temp.delete_labels()
        # temp.delete_project_members()
        # temp.delete_extractions()
        # temp.delete_projects()
        # temp.delete_followers()
        # temp.delete_watchers()
        # temp.delete_users()
        # logger.info("Data migrada {uuid}", uuid=self.uuid)
