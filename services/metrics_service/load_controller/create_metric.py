from typing import Any, Dict, Tuple
from psycopg2.extensions import connection, cursor
from loguru import logger
from pprint import pprint

from ..commons import METRICS_TABLE_NAME_MAP, REPO_METRICS


class Metric:
    def __init__(self, metric: Dict[str, Any], conn: connection):
        self.conn = conn
        self.name = metric["name"]
        self.description = metric.get("description")
        self.measurement_type = metric.get("measurement")
        self.id = self._get_or_create_id()

    def _get_or_create_id(self):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                INSERT INTO metrics (name, description, measurement_type) VALUES (%s, %s, %s) 
                ON CONFLICT (name) DO UPDATE
                SET description = EXCLUDED.description, measurement_type = EXCLUDED.measurement_type 
                RETURNING id
                """,
                (self.name, self.description, self.measurement_type),
            )
            result = curs.fetchone()

            if result is None:
                curs.execute("SELECT id FROM metrics WHERE name = %s", (self.name,))
                result = curs.fetchone()
                if result:
                    result = result[0]
            self.conn.commit()
        return result[0] if result else None

    def load(
        self,
        group_name: str,
        metric_id: int,
        result: Tuple[Any],
        extraction_id: int,
    ):
        table_info = METRICS_TABLE_NAME_MAP.get(group_name)
        if table_info is None:
            raise ValueError(f"Unknown group_name: {group_name}")

        table_name = table_info["table"]
        params = table_info["params"]
        results = list(result)
        results.pop(0)  # remove project_id
        results.insert(0, extraction_id)
        results.insert(0, metric_id)
        placeholders = ", ".join(["%s"] * len(results))
        params_query = ", ".join(params)

        query = f"INSERT INTO {table_name} ({params_query}) VALUES ({placeholders})"
        with self.conn.cursor() as curs:
            curs.execute(query, results)
            self.conn.commit()

    def _create_agg_metric(self):
        central_tendency_measures = ["avg", "median", "iqr"]
        for measure in central_tendency_measures:
            metric_name = f"{self.name}_{measure}"
            metric_description = f"{self.description} ({measure})"
            with self.conn.cursor() as curs:
                curs.execute(
                    """
                    INSERT INTO metrics (name, description, measurement_type) VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET description = EXCLUDED.description, measurement_type = EXCLUDED.measurement_type
                    RETURNING id
                    """,
                    (metric_name, metric_description, self.measurement_type),
                )
                self.conn.commit()

    def _calc_agg_metric(
        self, group_name: str, metric_id: int, extraction_id: int, curs: cursor
    ):
        table_info = METRICS_TABLE_NAME_MAP.get(group_name)
        if table_info is None:
            raise ValueError(f"Unknown group_name: {group_name}")

        table_name = table_info["table"]
        central_tendency_measures = {
            "avg": "AVG(CAST(value AS FLOAT))",
            "median": "PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CAST(value AS FLOAT))",
            "iqr": "PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY CAST(value AS FLOAT)) - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY CAST(value AS FLOAT))",
        }
        for measure, agg_function in central_tendency_measures.items():
            metric_name = f"{self.name}_{measure}"
            curs.execute("SELECT id FROM metrics WHERE name = %s", (metric_name,))
            agg_metric_id = curs.fetchone()
            if agg_metric_id is None:
                raise ValueError(f"Unknown metric: {metric_name}")
            agg_metric_id = agg_metric_id[0]
            curs.execute(
                f"""
                SELECT {agg_function} AS result
                FROM {table_name}
                WHERE metric_id = %s AND extraction_id = %s
                """,
                (metric_id, extraction_id),
            )
            agg_result = curs.fetchone()
            if agg_result is None:
                raise ValueError(f"Unknown metric: {metric_name}")
            agg_result = agg_result[0]
            logger.debug(
                "{metric_name} ({agg_function}): {agg_result}",
                metric_name=metric_name,
                agg_function=agg_function,
                agg_result=agg_result,
            )
            curs.execute(
                """
                INSERT INTO project_metrics (extraction_id, metric_id, value) VALUES (%s, %s, %s)
                """,
                (extraction_id, agg_metric_id, agg_result),
            )
            self.conn.commit()
