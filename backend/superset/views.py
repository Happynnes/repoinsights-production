from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
from django.db import connections
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError


def get_superset_token():
    """Función para obtener el access token."""
    url = f"{settings.SUPERSET_URL}/api/v1/security/login"
    payload = {
        "username": "admin",
        "password": "admin",
        "provider": "db",
        "refresh": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def get_dashboard_guest_token(request, dashboard_id):
    # Paso 1: Obtener el access token
    token = get_superset_token()
    if not token:
        return JsonResponse({"error": "No se pudo obtener el token de autenticación"}, status=500)

    # Paso 2: Obtener el CSRF token
    csrf_url = f"{settings.SUPERSET_URL}/api/v1/security/csrf_token/"
    headers = {
        "Authorization": f"Bearer {token}",
        "credentials":"include"
    }
    csrf_response = requests.get(csrf_url, headers=headers)
    if csrf_response.status_code == 200:
        csrf_token = csrf_response.json().get("result")
        print(f"CSRF token obtenido: {csrf_token}")
    else:
        return JsonResponse({"error": "No se pudo obtener el CSRF token"}, status=500)

    # Paso 3: Solicitar el guest token para el dashboard
    url = f"{settings.SUPERSET_URL}/api/v1/security/guest_token/"
    payload = {
        "resources": [
            {
                "id": str(dashboard_id),  # Asegúrate de que el ID sea un string
                "type": "dashboard"
            }
        ],
        "rls": [],
        "user": {
            "first_name": "admin",
            "last_name": "admin",
            "username": "admin"
        }
    }


    headers = {
        "Authorization": f"Bearer {token}",
        "X-CSRFTOKEN": csrf_token,
        "Content-Type": "application/json",
    }

    # Prueba añadir el token CSRF como cookie también
    cookies = {
        "csrf_token": csrf_token
    }

    # Realizar la solicitud POST para obtener el guest token
    response = requests.post(url, headers=headers, cookies=cookies, json=payload)
    print(f"Esto es lo que envio en el post: {url, headers, cookies, payload}")
    
    if response.status_code == 200:
        guest_token = response.json().get("token")
        return JsonResponse({"guest_token": guest_token})
    else:
        print(f"Error obteniendo el guest token: {response.text}")
        return JsonResponse({"error": "No se pudo obtener el guest token"}, status=response.status_code)

def run_query(query):
    with connections["repoinsights"].cursor() as cursor:
        cursor.execute(query)
        resultados = cursor.fetchall()
        return resultados

class ContributorsSuperset(APIView):
    def get(self, request):
        try:
            # Obtén el parámetro project_id
            project_id = request.GET.get("project_id")
            if not project_id:
                return JsonResponse({"error": "project_id is required"}, status=400)

            # Define la consulta con el project_id
            query = f"""
                WITH total_contributions AS (
                    SELECT 
                        project_id, 
                        committer_id, 
                        COUNT(*) AS contributions_per_dev
                    FROM 
                        commits
                    WHERE 
                        project_id = {project_id}
                    GROUP BY 
                        project_id, committer_id
                ),
                ranked_contributions AS (
                    SELECT 
                        tc.project_id,
                        tc.committer_id,
                        u.login AS user_login,
                        tc.contributions_per_dev,
                        ROW_NUMBER() OVER (
                            PARTITION BY tc.project_id
                            ORDER BY tc.contributions_per_dev DESC
                        ) AS rank
                    FROM 
                        total_contributions tc
                    LEFT JOIN 
                        users u ON tc.committer_id = u.id
                    WHERE 
                        u.login IS NOT NULL
                )
                SELECT 
                    project_id,
                    committer_id,
                    user_login,
                    contributions_per_dev
                FROM 
                    ranked_contributions
                WHERE 
                    rank <= 3
                ORDER BY 
                    project_id, rank;
            """

            # Ejecuta la consulta
            top_contributors = run_query(query)

            # Construye la respuesta
            response = [
                {
                    "project_id": item[0],
                    "committer_id": item[1],
                    "user_login": item[2],
                    "contributions_per_dev": item[3],
                }
                for item in top_contributors
            ]

            return JsonResponse({"data": response}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class HeatmapSuperset(APIView):
    def get(self, request):
        try:
            # Obtén el parámetro project_id
            project_id = request.GET.get("project_id")
            if not project_id:
                return JsonResponse({"error": "project_id is required"}, status=400)

            # Define la consulta con el project_id
            query = f"""
                WITH daily_commits AS (
                SELECT 
                    r.id AS project_id,
                    DATE(c.created_at) AS commit_date,
                    COUNT(*) AS commits_on_date
                FROM
                    commits c
                    INNER JOIN projects r ON c.project_id = r.id
                WHERE 
                project_id={project_id}
                GROUP BY
                    r.id, DATE(c.created_at)
            ),
            project_dates AS (
                SELECT
                    r.id AS project_id,
                    GENERATE_SERIES(
                        DATE(MIN(c.created_at)),
                        DATE(MAX(c.created_at)),
                        '1 day'::INTERVAL
                    )::DATE AS commit_date
                FROM
                    commits c
                    INNER JOIN projects r ON c.project_id = r.id
                WHERE 
                project_id={project_id}
                GROUP BY
                    r.id
            )
            SELECT
                pd.project_id,
                pd.commit_date,
                COALESCE(dc.commits_on_date, 0) AS commits_on_date
            FROM
                project_dates pd
            LEFT JOIN
                daily_commits dc ON pd.project_id = dc.project_id AND pd.commit_date = dc.commit_date
            ORDER BY
                pd.project_id, pd.commit_date;
            """

            # Ejecuta la consulta
            heatmap = run_query(query)

            # Construye la respuesta
            response = [
                {
                    "project_id": item[0],
                    "commit_date": item[1],
                    "commits_on_date": item[2]
                }
                for item in heatmap
            ]

            return JsonResponse({"data": response}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class ExtraInformationSuperset(APIView):
    def get(self, request):
        try:
            # Obtén el parámetro project_id
            project_id = request.GET.get("project_id")
            if not project_id:
                return JsonResponse({"error": "project_id is required"}, status=400)

            # Define la consulta con el project_id
            query = f"""
                SELECT 
    p.id AS project_id,
    u.location AS owner_location,
    (SELECT COUNT(*) 
     FROM commits c 
     WHERE c.project_id = p.id) AS total_commits,
    (SELECT MAX(c.created_at) 
     FROM commits c 
     WHERE c.project_id = p.id) AS last_commit_date,
    (SELECT MAX(i.created_at) 
     FROM issues i 
     WHERE i.repo_id = p.id AND i.pull_request = FALSE) AS last_issue_opened_date,
    (SELECT MAX(prh.created_at)
    FROM pull_requests pr
    JOIN pull_request_history prh ON pr.id = prh.pull_request_id 
    WHERE pr.base_repo_id = p.id AND prh.action = 'opened') AS last_pr_opened_date
FROM
    projects p
    JOIN users u ON p.owner_id = u.id
WHERE
    p.id = {project_id}
ORDER BY
    p.id;
            """

            # Ejecuta la consulta
            extraInfo = run_query(query)

            # Construye la respuesta
            response = [
                {
                    "project_id": item[0],
                    "owner_location": item[1],
                    "total_commits": item[2],
                    "last_commit_date": item[3],
                    "last_issue_opened_date": item[4],
                    "last_pr_opened_date": item[5],
                }
                for item in extraInfo
            ]

            return JsonResponse({"data": response}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class DailyCommits3D(APIView):
    def get(self, request):
        try:
            # Obtén los parámetros de la solicitud
            project_ids = request.GET.getlist("project_ids")
            if not project_ids:
                return JsonResponse({"error": "project_ids parameter is required"}, status=400)

            # Convierte los IDs a una lista separada por comas para la consulta
            project_ids_str = ",".join(map(str, project_ids))

            # Define la consulta con los IDs de los proyectos
            query = f"""
            WITH daily_commits AS (
                SELECT 
                    r.id AS project_id,
                    DATE(c.created_at) AS commit_date,
                    COUNT(*) AS commits_on_date
                FROM
                    commits c
                    INNER JOIN projects r ON c.project_id = r.id
                WHERE 
                    project_id IN ({project_ids_str})
                GROUP BY
                    r.id, DATE(c.created_at)
            ),
            project_dates AS (
                SELECT
                    r.id AS project_id,
                    r.name AS project_name,
                    GENERATE_SERIES(
                        DATE(MIN(c.created_at)),
                        DATE(MAX(c.created_at)),
                        '1 day'::INTERVAL
                    )::DATE AS commit_date
                FROM
                    commits c
                    INNER JOIN projects r ON c.project_id = r.id
                WHERE 
                    project_id IN ({project_ids_str})
                GROUP BY
                    r.id
            )
            SELECT
                pd.project_id,
                pd.project_name,
                pd.commit_date,
                COALESCE(dc.commits_on_date, 0) AS commits_on_date
            FROM
                project_dates pd
            LEFT JOIN
                daily_commits dc ON pd.project_id = dc.project_id AND pd.commit_date = dc.commit_date
            ORDER BY
                pd.project_id, pd.commit_date;
            """

            # Ejecuta la consulta
            result = run_query(query)

            # Construye la respuesta
            response = [
                {
                    "project_id": row[0],
                    "project_name": row[1],
                    "commit_date": row[2],
                    "commits_on_date": row[3],
                }
                for row in result
            ]

            return JsonResponse({"data": response}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class DailyIssues3D(APIView):
    def get(self, request):
        try:
            # Obtén los parámetros de la solicitud
            project_ids = request.GET.getlist("project_ids")
            if not project_ids:
                return JsonResponse({"error": "project_ids parameter is required"}, status=400)

            # Convierte los IDs a una lista separada por comas para la consulta
            project_ids_str = ",".join(map(str, project_ids))

            # Define la consulta con los IDs de los proyectos
            query = f"""
            WITH daily_issues AS (
            SELECT 
                r.id AS project_id,
                DATE(c.created_at) AS issue_date,
                COUNT(*) AS issues_on_date
            FROM
                issues c
                INNER JOIN projects r ON c.repo_id = r.id
            WHERE 
                r.id IN ({project_ids_str})
            GROUP BY
                r.id, DATE(c.created_at)
            ),
            project_dates AS (
            SELECT
                r.id AS project_id,
                r.name AS project_name,
                GENERATE_SERIES(
                    DATE(MIN(c.created_at)),
                    DATE(MAX(c.created_at)),
                    '1 day'::INTERVAL
                )::DATE AS issue_date
            FROM
                issues c
                INNER JOIN projects r ON c.repo_id = r.id
            WHERE 
                r.id IN ({project_ids_str})
            GROUP BY
                r.id
            )
            SELECT
            pd.project_id,
            pd.project_name,
            pd.issue_date,
            COALESCE(dc.issues_on_date, 0) AS issues_on_date
            FROM
            project_dates pd
            LEFT JOIN
            daily_issues dc ON pd.project_id = dc.project_id AND pd.issue_date = dc.issue_date
            ORDER BY
            pd.project_id, pd.issue_date;
            """

            # Ejecuta la consulta
            result = run_query(query)

            # Construye la respuesta
            response = [
                {
                    "project_id": row[0],
                    "project_name": row[1],
                    "issue_date": row[2],
                    "issues_on_date": row[3],
                }
                for row in result
            ]

            return JsonResponse({"data": response}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class DailyPRsMerged3D(APIView):
    def get(self, request):
        try:
            # Obtén los parámetros de la solicitud
            project_ids = request.GET.getlist("project_ids")
            if not project_ids:
                return JsonResponse({"error": "project_ids parameter is required"}, status=400)

            # Convierte los IDs a una lista separada por comas para la consulta
            project_ids_str = ",".join(map(str, project_ids))

            # Define la consulta con los IDs de los proyectos
            query = f"""
            WITH merged_pull_requests AS (
            SELECT 
                p.id AS project_id,
                p.name AS project_name,
                DATE(prh.created_at) AS pr_merged_date,
                COUNT(*) AS pr_merged_on_date
            FROM
                pull_request_history prh
                INNER JOIN pull_requests pr ON prh.pull_request_id = pr.id
                INNER JOIN projects p ON pr.base_repo_id = p.id
            WHERE 
                prh.action = 'merged'
                AND p.id IN ({project_ids_str})
            GROUP BY
                p.id, p.name, DATE(prh.created_at)
            ),
            project_dates AS (
            SELECT
                p.id AS project_id,
                p.name AS project_name,
                GENERATE_SERIES(
                    DATE(MIN(prh.created_at)),
                    DATE(MAX(prh.created_at)),
                    '1 day'::INTERVAL
                )::DATE AS pr_merged_date
            FROM
                pull_request_history prh
                INNER JOIN pull_requests pr ON prh.pull_request_id = pr.id
                INNER JOIN projects p ON pr.base_repo_id = p.id
            WHERE 
                prh.action = 'merged'
                AND p.id IN ({project_ids_str})
            GROUP BY
                p.id, p.name
            )
            SELECT
            pd.project_id,
            pd.project_name,
            pd.pr_merged_date,
            COALESCE(mpr.pr_merged_on_date, 0) AS pr_merged_on_date
            FROM
            project_dates pd
            LEFT JOIN
            merged_pull_requests mpr ON pd.project_id = mpr.project_id AND pd.pr_merged_date = mpr.pr_merged_date
            ORDER BY
            pd.project_id, pd.pr_merged_date;
            """

            # Ejecuta la consulta
            result = run_query(query)

            # Construye la respuesta
            response = [
                {
                    "project_id": row[0],
                    "project_name": row[1],
                    "pr_merged_date": row[2],
                    "pr_merged_on_date": row[3],
                }
                for row in result
            ]

            return JsonResponse({"data": response}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class DailyPRsClosed3D(APIView):
    def get(self, request):
        try:
            # Obtén los parámetros de la solicitud
            project_ids = request.GET.getlist("project_ids")
            if not project_ids:
                return JsonResponse({"error": "project_ids parameter is required"}, status=400)

            # Convierte los IDs a una lista separada por comas para la consulta
            project_ids_str = ",".join(map(str, project_ids))

            # Define la consulta con los IDs de los proyectos
            query = f"""
            WITH merged_pull_requests AS (
            SELECT 
                p.id AS project_id,
                p.name AS project_name,
                DATE(prh.created_at) AS pr_closed_date,
                COUNT(*) AS pr_closed_on_date
            FROM
                pull_request_history prh
                INNER JOIN pull_requests pr ON prh.pull_request_id = pr.id
                INNER JOIN projects p ON pr.base_repo_id = p.id
            WHERE 
                prh.action = 'closed'
                AND p.id IN ({project_ids_str})
            GROUP BY
                p.id, p.name, DATE(prh.created_at)
            ),
            project_dates AS (
            SELECT
                p.id AS project_id,
                p.name AS project_name,
                GENERATE_SERIES(
                    DATE(MIN(prh.created_at)),
                    DATE(MAX(prh.created_at)),
                    '1 day'::INTERVAL
                )::DATE AS pr_closed_date
            FROM
                pull_request_history prh
                INNER JOIN pull_requests pr ON prh.pull_request_id = pr.id
                INNER JOIN projects p ON pr.base_repo_id = p.id
            WHERE 
                prh.action = 'closed'
                AND p.id IN ({project_ids_str})
            GROUP BY
                p.id, p.name
            )
            SELECT
            pd.project_id,
            pd.project_name,
            pd.pr_closed_date,
            COALESCE(mpr.pr_closed_on_date, 0) AS pr_closed_on_date
            FROM
            project_dates pd
            LEFT JOIN
            merged_pull_requests mpr ON pd.project_id = mpr.project_id AND pd.pr_closed_date = mpr.pr_closed_date
            ORDER BY
            pd.project_id, pd.pr_closed_date;
            """

            # Ejecuta la consulta
            result = run_query(query)

            # Construye la respuesta
            response = [
                {
                    "project_id": row[0],
                    "project_name": row[1],
                    "pr_closed_date": row[2],
                    "pr_closed_on_date": row[3],
                }
                for row in result
            ]

            return JsonResponse({"data": response}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
