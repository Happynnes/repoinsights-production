import pika
from curate_repos.Metrics import CurateMetrics
from pprint import pprint
from datetime import datetime
import timeit


project = "apache/airflow"
simple_project = "pygithub/pygithub"
curate_metrics = CurateMetrics(simple_project)
if curate_metrics is None:
    print("No se pudo obtener el repositorio")
    exit(1)
start_date = datetime.strptime("2017-11", "%Y-%m")
end_date = datetime.strptime("2023-02", "%Y-%m")

# ------------CONTRIBUTORS ----------------
core_contributors = curate_metrics.core_contributors_metric()
# pprint(core_contributors)


# ------------COMMITS ----------------
start = timeit.default_timer()
commit_frecuency = curate_metrics.commit_frecuency_metric(start_date, end_date)
stop = timeit.default_timer()
print(commit_frecuency)
print("Time: ", stop - start)

# # ------------CI ----------------
# ci_file = curate_metrics.continuous_integration_metric()
# print(ci_file)

# # ------------LICENCE ----------------
# licenses = curate_metrics.license_metric()
# print(licenses)

# # ------------ISSUES ----------------
start = timeit.default_timer()
issue_frecuency = curate_metrics.issue_frecuency_metric(start_date, end_date)
stop = timeit.default_timer()
pprint(issue_frecuency)
print("Time: ", stop - start)
