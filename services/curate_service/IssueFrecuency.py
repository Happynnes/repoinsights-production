from github import Github
from github.Repository import Repository
from github.PaginatedList import PaginatedList
from github.Issue import Issue
from datetime import datetime
from services.extract_service.utils.utils import get_first_last_days_month, get_n_months
from pprint import pprint
from typing import Union, List

"""
Se puede mejorar __get_issues_between_dates para no tener que buscar nuevamente en la API los issues desde nueva fecha.
Se podrían guardar todos los issues desde self.start_date hasta self.end_date luego buscar en esa lista.
"""


class IssueFrecuency:
    def __init__(
        self, repo: Repository, start_date: datetime, end_date: datetime
    ) -> None:
        self.repo = repo
        self.start_date = get_first_last_days_month(start_date)[0]
        self.end_date = get_first_last_days_month(end_date)[1]
        # Obtiene todos los issues actualizados desde la fecha de inicio
        self.issues = repo.get_issues(
            state="all", since=self.start_date, sort="created", direction="asc"
        )
        print(
            {
                "Start date": self.dt_to_str(self.start_date),
                "End date": self.dt_to_str(self.end_date),
            }
        )

    def dt_to_str(self, dt):
        return datetime.strftime(dt, "%Y-%m-%d")

    def __get_issues_between_dates(
        self,
        issues,
        start_date: datetime,
        end_date: datetime,
    ):
        month_issues = []
        issue: Issue

        for issue in issues:
            # check if is pull request
            if issue.created_at >= end_date:
                break

            if issue.created_at <= start_date:
                continue

            if issue.pull_request:
                print(
                    {
                        "date": self.dt_to_str(issue.created_at),
                        "issue": f"{issue.number} is pull request",
                    }
                )
                continue

            self.dt_to_str(issue.updated_at) if issue.closed_at else None
            self.dt_to_str(issue.closed_at) if issue.closed_at else None

            month_issues.append(issue)
        return month_issues

    def get_issues_per_month(self, issues: list, months: int):
        current_month = self.start_date
        issues_months = []
        temp = 0
        for _ in range(0, months):
            if current_month.month == 12:
                current_month = current_month.replace(
                    year=current_month.year + 1, month=1
                )
            else:
                current_month = current_month.replace(month=current_month.month + temp)

            first_day, last_day = get_first_last_days_month(current_month)
            temp_issues = self.__get_issues_between_dates(issues, first_day, last_day)
            issues_months.append(
                {
                    "date": current_month,
                    "issues": len(temp_issues),
                    "Issues": temp_issues,
                }
            )
            temp = 1
        return issues_months

    def calc(self):
        issues_between_dates = self.__get_issues_between_dates(
            self.issues, self.start_date, self.end_date
        )
        print("total issues between dates: ", len(issues_between_dates))
        n_months = get_n_months(self.start_date, self.end_date)
        issues_per_month = self.get_issues_per_month(issues_between_dates, n_months)
        sum_si = 0
        for si in issues_per_month:
            print(
                {
                    "date": self.dt_to_str(si["date"]),
                    "issues": si["issues"],
                }
            )
            sum_si += si["issues"]
        return sum_si / n_months
