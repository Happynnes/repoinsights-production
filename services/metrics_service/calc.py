import json
from services.metrics_service.calc_controller.calculate import CalculateMetrics
from services.metrics_service.conn import ConsolidadaConnection
from services.metrics_service.load_controller.load import MetricsLoader
from psycopg2.extensions import connection

from services.metrics_service.exceptions import ExtractionNotFound, RepoNotFound


def get_extraction_id(conn: connection, uuid: str):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id FROM extractions WHERE ext_ref_id = %s
        """,
        (uuid,),
    )
    result = cursor.fetchone()
    if result is None:
        raise ExtractionNotFound("Extraction not found")
    extraction_id: int = result[0]
    return extraction_id


def get_project_id(conn: connection, project_name: str):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id FROM projects WHERE name = %s AND forked_from IS null
        """,
        (project_name,),
    )
    result = cursor.fetchone()
    if result is None:
        raise RepoNotFound("Project not found")
    project_id: int = result[0]
    return project_id


def calculate_metrics(project_name, uuid):
    consolidada_conn = ConsolidadaConnection()
    conn = consolidada_conn.get_connection()
    extraction_id = get_extraction_id(conn, uuid)
    project_id = get_project_id(conn, project_name)
    calc_metrics = CalculateMetrics(conn, project_id, extraction_id)
    load_metrics = MetricsLoader(conn, project_id, extraction_id)
    results = calc_metrics.calculate_metrics()

    for metric_group in calc_metrics.metrics:
        load_metrics.add_metric_group(metric_group)
    load_metrics.load_metrics(results)
