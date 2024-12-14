import glob
from loguru import logger
from psycopg2.extensions import connection, cursor
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from ..helper import yaml_to_dict
from ..commons import METRICS_DIR, METRICS_GROUPS, REPO_METRICS
from .metric_validator import MetricValidator


class MetricExtractor:
    @staticmethod
    def get_metrics() -> List[Dict[str, Any]]:
        metrics = []
        for metrics_group in METRICS_GROUPS:
            group = {"group": metrics_group, "metrics": []}
            metrics_group_dirs = glob.glob(METRICS_DIR + metrics_group + "/*.yml")
            group_metrics = [
                yaml_to_dict(metric_dir) for metric_dir in metrics_group_dirs
            ]
            MetricValidator.validate_metric_names(group_metrics)
            group["metrics"] = group_metrics
            metrics.append(group)
        return metrics

    @staticmethod
    def generate_params(metric: Dict, project_id: int):
        if metric.get("variables"):
            params = []
            variables = metric["variables"]
            for var in variables:
                if var == "project_id":
                    params.append(project_id)
            return params
        return [project_id]

    @staticmethod
    def convert_if_decimal(item: Tuple[Any]):
        data = list(item)
        for i in range(len(data)):
            if isinstance(data[i], Decimal):
                data[i] = float(data[i])
        return data

    @staticmethod
    def calc_metrics_group(metrics: List[Dict], project_id: int, curs: cursor):
        def get_result(data):
            if data is None:
                raise ValueError("Metric not found")
            elif len(data) == 0:
                return None
            else:
                result = [MetricExtractor.convert_if_decimal(item) for item in data]
            return result

        results = {}
        for metric in metrics:
            params = MetricExtractor.generate_params(metric, project_id)
            curs.execute(metric["metric"], params)
            data = curs.fetchall()
            result = get_result(data)
            if result is None:
                print(f"Metric {metric['name']} is empty")
                continue
            results[metric["name"]] = result

        return results
