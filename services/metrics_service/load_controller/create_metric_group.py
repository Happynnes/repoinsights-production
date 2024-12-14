from typing import Dict, Any
from psycopg2.extensions import connection
from .create_metric import Metric


class MetricGroup:
    def __init__(self, group: Dict[str, Any], conn: connection):
        self.name = group["group"]
        self.metrics = [Metric(metric, conn) for metric in group["metrics"]]

    def get_metrics_ids(self):
        return [{"name": metric.name, "id": metric.id} for metric in self.metrics]
