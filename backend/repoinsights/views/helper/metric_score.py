from django.db import connections
from typing import Dict

from .variables import metric_scores, measurement_types


class ProjectMetricScore:
    @staticmethod
    def calc_metric_values(metric_names, project_ids):
        project_ids_str = ",".join(map(str, project_ids))
        metric_names_str = "','".join(metric_names)
        query = f"""
            SELECT
                pm.value AS value,
                m.name AS metric_name,
                m.measurement_type,
                e.project_id
            FROM "ghtorrent_restore_2015"."project_metrics" pm
            JOIN extractions e ON pm.extraction_id = e.id
            JOIN (
                SELECT MAX(date) as max_date, project_id
                FROM extractions e
                WHERE e.project_id IN ({project_ids_str})
                GROUP BY project_id
            ) AS max_extractions ON e.date = max_extractions.max_date AND e.project_id = max_extractions.project_id
            JOIN "ghtorrent_restore_2015"."projects" p ON e.project_id = p.id
            JOIN metrics m ON pm.metric_id = m.id
            WHERE m.name IN ('{metric_names_str}')
        """
        with connections["repoinsights"].cursor() as cursor:
            cursor.execute(query)
            response = cursor.fetchall()

        result = {}
        for row in response:
            project_id = row[3]
            metric_name = row[1]
            if project_id not in result:
                result[project_id] = {}
            result[project_id][metric_name] = (float(row[0]), row[1], row[2])
        return result

    @staticmethod
    def calc_rating(metric_data, metric_value: float):
        if metric_value is None:
            return None
        if isinstance(metric_data, dict):
            for metric in metric_data.items():
                rate = metric[0]
                min_value = float(metric[1]["min"])
                max_value = float(metric[1]["max"])
                if metric_value >= min_value and metric_value <= max_value:
                    return rate
            return None

    @staticmethod
    def prepare_metric_data(
        metric_score, metric_value, metric_name, metric_measurement
    ):
        rating = ProjectMetricScore.calc_rating(metric_score["rating"], metric_value)
        show_value = metric_score.get("show_value", True)
        metric_title = (
            metric_score["title"] if metric_score.get("title") else metric_score["name"]
        )
        return {
            "id": metric_score["name"],
            "name": metric_title,
            "value": metric_value,
            "rating": rating,
            "show_value": show_value,
            "measurement": measurement_types[metric_measurement.lower()]
            if metric_measurement
            else None,
        }

    @staticmethod
    def calc_metric_score(projects: list, show_empty_values=False) -> list:
        project_ids = [project["id"] for project in projects]
        metric_names = [metric["name"] for metric in metric_scores]
        if not (project_ids and metric_names):
            return []

        metric_values = ProjectMetricScore.calc_metric_values(metric_names, project_ids)
        for project in projects:
            project["rating"] = []
            project_id = project["id"]
            empty_metrics = True
            project_metrics = metric_values.get(project_id)
            if project_metrics is None:
                project["empty"] = True
                continue

            for metric_score in metric_scores:
                score_metric_name = metric_score["name"]
                if score_metric_name in project_metrics:
                    metric_value, metric_name, metric_measurement = project_metrics[
                        score_metric_name
                    ]
                    data = ProjectMetricScore.prepare_metric_data(
                        metric_score, metric_value, metric_name, metric_measurement
                    )
                    project["rating"].append(data)
                    empty_metrics = False
                elif show_empty_values:
                    data = {
                        "id": score_metric_name,
                        "name": score_metric_name,
                        "value": None,
                        "rating": None,
                        "show_value": False,
                        "measurement": None,
                    }
                    project["rating"].append(data)
            project["empty"] = empty_metrics

        return projects

    @staticmethod
    def get_metrics():
        return [
            {
                "id": metric["name"],
                "name": metric["title"],
                "invert": metric["weight"]["invert"],  # type: ignore
            }
            for metric in metric_scores
        ]
