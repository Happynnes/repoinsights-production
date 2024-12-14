from typing import Dict, List, Any, Tuple
import json
from pprint import pprint
from loguru import logger
from psycopg2.extensions import connection
from .create_metric import Metric
from .create_metric_group import MetricGroup
from ..commons import METRICS_TABLE_NAME_MAP, REPO_METRICS


class MetricsLoader:
    def __init__(self, conn: connection, project_id, extraction_id: int):
        self.conn = conn
        self.project_id = project_id
        self.extraction_id = extraction_id
        self.metric_groups: List[MetricGroup] = []

    def add_metric_group(self, group: Dict[str, Any]):
        self.metric_groups.append(MetricGroup(group, self.conn))

    def load_metrics(self, results: Dict):
        for group in self.metric_groups:
            self._load_metrics_for_group(group, results)

    def _load_metrics_for_group(self, group: MetricGroup, results: Dict):
        metrics_ids = group.get_metrics_ids()
        for metric in metrics_ids:
            self._load_metric_results(metric, results)

    def _load_metric_results(self, metric: Dict[str, Any], results: Dict):
        metric_results = results.get(metric["name"])
        if metric_results is None:
            return
        for metric_result in metric_results:
            self._log_and_load_metric_result(metric_result, metric)
        self.load_resume_metrics(metric)

    def _log_and_load_metric_result(
        self, metric_result: List[Any], metric: Dict[str, Any]
    ):
        self._load_metric_result_to_database(metric["id"], metric_result)

    def _load_metric_result_to_database(self, metric_id: int, result):
        for group in self.metric_groups:
            for m in group.metrics:
                if m.id == metric_id:
                    m.load(group.name, metric_id, result, self.extraction_id)

    def load_resume_metrics(self, metric: Dict[str, Any]):
        for group in self.metric_groups:
            if group.name == REPO_METRICS:
                continue

            for m in group.metrics:
                if m.name == metric["name"]:
                    m._create_agg_metric()
                    m._calc_agg_metric(
                        group_name=group.name,
                        metric_id=metric["id"],
                        curs=self.conn.cursor(),
                        extraction_id=self.extraction_id,
                    )
