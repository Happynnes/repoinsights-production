from typing import List, Any
from loguru import logger
from ..helper import get_subdirectories
from ..commons import METRICS_DIR


class MetricValidator:
    @staticmethod
    def validate_metric_names(metrics: List[Any]) -> None:
        names = [metric["name"] for metric in metrics]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate metric names detected!")

    @staticmethod
    def validate_metrics_groups(extraction_id: int, check_if_exists) -> List[str]:
        group_names = get_subdirectories(METRICS_DIR)
        groups_for_extract = []
        for group_name in group_names:
            exist = check_if_exists(extraction_id, group_name)
            if not exist:
                groups_for_extract.append(group_name)
        if len(groups_for_extract) == 0:
            logger.warning(
                f"Metrics for all groups already exist for extraction_id {extraction_id}"
            )
        return groups_for_extract
