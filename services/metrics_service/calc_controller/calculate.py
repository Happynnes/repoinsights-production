from pprint import pprint
from loguru import logger
from psycopg2.extensions import connection

from ..helper import yaml_to_dict
from .metric_validator import MetricValidator
from .metric_extractor import MetricExtractor
from .metric_db import MetricDB
import json


class CalculateMetrics:
    def __init__(self, conn: connection, project_id: int, extraction_id: int) -> None:
        self.project_id = project_id
        self.conn = conn
        self.extraction_id = extraction_id
        self.db = MetricDB(conn)
        self.metrics = MetricExtractor.get_metrics()

    def calculate_metrics(self):
        results = {}
        with self.conn.cursor() as curs:
            valid_groups = MetricValidator.validate_metrics_groups(
                self.extraction_id, self.db.check_if_exists_metric_in_group
            )
            logger.info(f"Valid groups: {valid_groups}")
            for metric in self.metrics:
                metric_group_name, metrics = metric["group"], metric["metrics"]
                exist = self.db.check_if_exists_metric_in_group(
                    self.extraction_id, metric_group_name
                )
                if not exist and metric_group_name in valid_groups:
                    try:
                        group_metrics = MetricExtractor.calc_metrics_group(
                            metrics, self.project_id, curs
                        )
                        results.update(group_metrics)
                    except Exception as e:
                        json_metric = json.dumps(metric)
                        pprint(json_metric)
                        raise e
                else:
                    logger.warning(
                        f"Metrics for group {metric_group_name} already exist for extraction_id {self.extraction_id}"
                    )
        return results
