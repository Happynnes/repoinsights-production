from github.Commit import Commit
from github.Repository import Repository
from datetime import datetime, timedelta
from pprint import pprint
from services.extract_service.utils.utils import get_first_last_days_month, get_n_months


class CommitFrecuency:
    def __init__(self, repo: Repository, start_month: datetime, end_month: datetime):
        self.repo = repo
        self.start_date = start_month
        self.end_date = end_month
        print({"Start date", self.start_date, "End date", self.end_date})
        self.commits = repo.get_commits(
            since=self.start_date,
            until=self.end_date,
        )

    def __get_commits_per_month(self, total_months):
        print("Total months", total_months)
        commits_per_month = []
        total_commits = 0
        current_month = self.start_date
        print("Current month", current_month)
        temp = 0
        for _ in range(0, total_months):
            if current_month.month == 12:
                current_month = current_month.replace(
                    year=current_month.year + 1, month=1
                )
            else:
                current_month = current_month.replace(month=current_month.month + temp)
            first_day, last_day = get_first_last_days_month(current_month)
            commits_month = self.repo.get_commits(since=first_day, until=last_day)
            month_data = {
                "date": datetime.strftime(current_month, "%Y-%m "),
                "commits": commits_month.totalCount,
            }
            pprint(month_data)
            total_commits += commits_month.totalCount
            commits_per_month.append(month_data)
            temp = 1
        return commits_per_month, total_commits

    def calc(self):
        m = get_n_months(self.start_date, self.end_date)
        commits_per_month, total_commits = self.__get_commits_per_month(m)
        pprint({"Total commits", total_commits})
        sum_ci = 0
        for ci in commits_per_month:
            sum_ci += ci["commits"]
        return sum_ci / m
