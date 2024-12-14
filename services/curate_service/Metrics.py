from github import Github
from .GHToken import GHToken
from pprint import pprint
from .CoreContributors import CoreContributors
from .CommitFrecuency import CommitFrecuency
from .ContinuousIntegration import ContinuousIntegration
from .License import License
from datetime import datetime
from .IssueFrecuency import IssueFrecuency


"""
1.Community, as evidence of collaboration.              DONE  core_contributors_metric()
2.Continuous integration, as evidence of quality.       DONE  continuous_integration_metric()
3.Documentation, as evidence of maintainability.        NEEDS-CODE
4.History, as evidence of sustained evolution.          DONE  commit_frecuency_metric()
5.Issues, as evidence of project management.            DONE  commit_frecuency_metric()
6.License, as evidence of accountability.               DONE  license_metric()
7.Unit testing, as evidence of quality.                 NEEDS-CODE 
"""


class FailGetRepo(Exception):
    pass


class CurateMetrics:
    def __init__(self, project) -> None:
        self.core_contributors_min = 2

        self.token = GHToken().get_token()
        self.gh = Github(self.token, per_page=100)
        self.repo = self.__get_repo__(project)

    def __get_repo__(self, project: str):
        try:
            repo = self.gh.get_repo(project)
            return repo
        except Exception as e:
            print(e)
            raise FailGetRepo("No se pudo obtener el repositorio")

    """
    Core contributors: is the cardinality of the smallest set of contributors whose total number of commits 
    to a source code repository
    accounts for 80% or more of the total contributions
    que endpoints de la api de github debo utilizar
    """

    def core_contributors_metric(self):
        core_contributors = CoreContributors(self.repo)
        return core_contributors.calc()

    """
    Commit frequency: is the average number of commits per month
    ci-> is the number of commits for the months i
    m -> is the number of months between the first and last commit to the repository
    # se tomaran en cuenta los meses incluidos. 2023-01 al 2023-04 se tomaran 4 meses
    """

    def commit_frecuency_metric(self, start_date: datetime, end_date: datetime):
        commit_frecuency_period = CommitFrecuency(self.repo, start_date, end_date)
        return commit_frecuency_period.calc()

    """
    Desde GitHub no es posible obtener el numero de issues creados en un periodo de tiempo.
    Se puede obtener issues que han sido modificados desde una fecha.
    """

    def issue_frecuency_metric(self, start_date: datetime, end_date: datetime):
        issue_frecuency_period = IssueFrecuency(self.repo, start_date, end_date)
        return issue_frecuency_period.calc()

    """
    CI: Looking for a con-figuration file (required by certain CI services) in the source code repository.
    """

    def continuous_integration_metric(self):
        ci = ContinuousIntegration(self.repo)
        exist_ci_file = ci.calc()
        return exist_ci_file

    """
    Licence: The metric for the license dimension may be defined as a piecewise function asshown below
    """

    def license_metric(self):
        licenses = License(self.repo)
        return licenses.calc()
