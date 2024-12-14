from datetime import datetime, timedelta
from typing import Union, List, Dict, Set, Any
from loguru import logger


date_format = "%Y-%m-%d"
queue_format = "%Y-%m-%dT%H:%M:%SZ"


def format_dt(dt: datetime) -> str:
    return dt.strftime(queue_format)


def api_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, queue_format)


def get_user_type(type) -> Union[str, None]:
    if type == "Organization":
        return "ORG"
    elif type == "User":
        return "USR"
    elif type == "Bot":
        return "BOT"
    else:
        return None


def get_first_last_days_month(month: datetime):
    first_day = month.replace(day=1)
    if month.month != 12:
        last_day = month.replace(
            day=month.day,
            month=month.month + 1,
        ) - timedelta(days=1)
    else:
        last_day = month.replace(
            day=1,
            month=1,
            year=month.year + 1,
        ) - timedelta(days=1)
    return first_day, last_day


def get_n_months(start_date: datetime, end_date: datetime):
    months = (
        (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    )
    return months


def format_date(date: datetime) -> str:
    return date.strftime(date_format)


def is_valid_date(date_str):
    try:
        format_date(datetime.strptime(date_str, date_format))
        return True
    except ValueError:
        return False


def get_date_from_str(date_str: str) -> datetime:
    return datetime.strptime(date_str, date_format)


def compare_dates(d1: str, d2: str):
    date1 = get_date_from_str(d1)
    date2 = get_date_from_str(d2)
    return (date1 > date2) - (date1 < date2)


def _get_nested_dict_value(dictionary: dict, keys: List[str]):
    for key in keys[:-1]:
        if dictionary is not None:
            dictionary = dictionary.get(key)
        else:
            return None
    return dictionary


def _update_user_obj(user_obj: dict, users: Dict, last_key: str):
    if user_obj[last_key] is not None:
        try:
            user_obj[last_key] = users[user_obj[last_key]["login"]]
        except KeyError:
            logger.error(f"User {user_obj[last_key]} not found")
            user_obj[last_key] = None


def add_users_to_dict_keys(list_dicts: List, users: Dict, user_keys: List[str]):
    for dictionary in list_dicts:
        for key in user_keys:
            keys = key.split(".")
            user_obj = _get_nested_dict_value(dictionary, keys)

            if user_obj is not None:
                _update_user_obj(user_obj, users, keys[-1])


def get_unique_users(elements, user_key: str) -> Set[str]:
    users_to_fetch = set()
    for element in elements:
        keys = user_key.split(".")
        user_obj = element
        for key in keys:
            if user_obj is not None:
                user_obj = user_obj.get(key)
            else:
                break
        if user_obj is not None:
            try:
                users_to_fetch.add(user_obj["login"])
            except KeyError:
                logger.error(f"User {user_obj} not found")
    return users_to_fetch


def get_int_from_dict(comment: Dict[str, Any], key: str) -> int:
    pr_url: str = comment[key]
    return int(pr_url.split("/")[-1])
