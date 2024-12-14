import yaml
import os
import glob
from loguru import logger
from decimal import Decimal


def yaml_to_dict(path):
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def files_in_dir(path, extension):
    files = []
    yml_files = glob.glob(os.path.join(path, f"*.{extension}"))
    for file in yml_files:
        files.append(file)
    return files


def create_metrics(conn):
    path = os.path.dirname(os.path.abspath(__file__)) + "/metrics/"
    metrics_yml = files_in_dir(path, "yml")
    for metric_yml in metrics_yml:
        metric = yaml_to_dict(metric_yml)
        if metric is None:
            continue
        name = metric["name"]
        description = metric.get("description") or ""
        with conn.cursor() as curs:
            try:
                curs.execute(
                    "INSERT INTO metrics (name, description) VALUES (%s, %s)",
                    (name, description),
                )
                conn.commit()

            except Exception as e:
                logger.error("Metric already exists", e)


def check_types(value):
    if type(value) == Decimal:
        return float(value)
    return value


def get_subdirectories(path):
    return [
        name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))
    ]
