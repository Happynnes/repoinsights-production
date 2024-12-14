from datetime import datetime, timedelta
from typing import Union, List, Dict, Set, Any
from loguru import logger


def format_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
