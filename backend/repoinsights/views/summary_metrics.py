from django.db import connections
from django.http import JsonResponse
from rest_framework.views import APIView


def run_query(query: str):
    with connections["repoinsights"].cursor() as cursor:
        cursor.execute(query)
        resultados = cursor.fetchall()
        return resultados


class RepoInsightsSummaryMetrics(APIView):
    def get(self, request):
        try:
            general = run_query(
                """
                    SELECT AVG(pm.value::numeric)*100 AS "Promedio", 'Días con contribuciones' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'active_days_coverage'
                    UNION ALL
                    SELECT AVG(pm.value::numeric) AS "Promedio", 'Commits por desarrollador' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'commits_per_dev_avg'
                    UNION ALL
                    SELECT AVG(pm.value::numeric) AS "Promedio", 'Dispersión del equipo de trabajo' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'dev_contributions_dispersion'
                    UNION ALL
                    SELECT AVG(um.user_count) AS "Promedio", 'N° desarrolladores del bus factor' AS "Descripción"
                    FROM (
                    SELECT extraction_id, COUNT(um.user_id) AS user_count
                    FROM user_metrics um
                    JOIN metrics m ON um.metric_id = m.id
                    WHERE m.name = 'truck_factor'
                    GROUP BY extraction_id
                    ) AS um
                """
            )

            issues = run_query(
                """
                    SELECT ROUND(AVG(pm.value::numeric), 0) AS "Promedio", 'Tiempo en cerrar issues' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'defect_resolution_time_avg'
                    UNION ALL
                    SELECT ROUND(AVG(pm.value::numeric), 0) AS "Promedio", 'Tiempo en primera respuesta' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'time_to_first_response_issues_avg'
                    UNION ALL
                    SELECT ROUND(AVG(pm.value::numeric), 0) AS "Promedio", 'Tiempo entre issues' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'mtbf'
                    UNION ALL
                    SELECT ROUND(AVG(pm.value::numeric), 3) AS "Promedio", 'Issues cerrados por día' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'issue_closed_per_day'
                    UNION ALL
                    SELECT ROUND(AVG(pm.value::numeric), 3) AS "Promedio", 'Issues asignados a cada dev' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'issues_per_dev_avg'
                    UNION ALL
                    SELECT ROUND(AVG(pm.value::numeric), 3) AS "Promedio", 'Comentarios por issue' AS "Descripción"
                    FROM project_metrics pm
                    JOIN metrics m ON pm.metric_id = m.id
                    WHERE m.name = 'issue_commented_avg'
                    """
            )

            pull_requests = run_query(
                """
                    SELECT ROUND(AVG(value::numeric), 0) AS "Promedio", 'Horas en merge una PR' AS "Descripción"
                    FROM project_metrics
                    JOIN metrics ON project_metrics.metric_id = metrics.id
                    WHERE metrics.name = 'decision_time_avg'
                    UNION ALL
                    SELECT ROUND(AVG(value::numeric), 0) AS "Promedio", 'Horas en cerrar una PR' AS "Descripción"
                    FROM project_metrics
                    JOIN metrics ON project_metrics.metric_id = metrics.id
                    WHERE metrics.name = 'close_time_pr_avg'
                    UNION ALL
                    SELECT ROUND(AVG(value::numeric), 0) AS "Promedio", 'PRs abiertas por desarrollador' AS "Descripción"
                    FROM project_metrics
                    JOIN metrics ON project_metrics.metric_id = metrics.id
                    WHERE metrics.name = 'prs_created_per_dev_avg'
                    UNION ALL
                    SELECT ROUND(AVG(value::numeric), 3) AS "Promedio", 'PR cerradas vs total' AS "Descripción"
                    FROM project_metrics
                    JOIN metrics ON project_metrics.metric_id = metrics.id
                    WHERE metrics.name = 'pr_closure_ratio'
                    UNION ALL
                    SELECT ROUND(AVG(value::numeric), 3) AS "Promedio", 'Commits por PR' AS "Descripción"
                    FROM project_metrics
                    JOIN metrics ON project_metrics.metric_id = metrics.id
                    WHERE metrics.name = 'avg_commits_in_pr'
                    UNION ALL
                    SELECT ROUND(AVG(value::numeric), 3) AS "Promedio", 'PRs abiertas vs cerradas' AS "Descripción"
                    FROM project_metrics
                    JOIN metrics ON project_metrics.metric_id = metrics.id
                    WHERE metrics.name = 'pr_open_to_closed_ratio'
                """
            )

            general = [{"name": item[1], "value": float(item[0])} for item in general]
            issues = [{"name": item[1], "value": float(item[0])} for item in issues]
            pull_requests = [{"name": item[1], "value": float(item[0])} for item in pull_requests]

            return JsonResponse(
                {
                    "headers": ["general", "issues", "pull_requests"],
                    "data": {
                        "general": {
                            "data": general,
                            "title": "General",
                        },
                        "issues": {
                            "data": issues,
                            "title": "Issues",
                        },
                        "pull_requests": {
                            "data": pull_requests,
                            "title": "Pull Requests",
                        },
                    }
                },
                status=200,
                safe=True,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
