from django.contrib.auth.models import User
from metabase.models import MetabaseUserData
from users.models import CustomUser
from pprint import pprint

from metabase.views.connector.metabase_conn import MetabaseClient


def create_metabase_user(profile: CustomUser, user: User):
    metabase_client = MetabaseClient()
    group_name = f"{profile.username}_group"
    metabase_group = metabase_client.group.create_group(username=group_name)
    pprint(metabase_group)

    metabase_user = metabase_client.user.create_user(
        email=user.email, fname=profile.username, lname=user.last_name
    )
    pprint(metabase_user)

    metabase_relation = metabase_client.group.add_user_to_group(
        group_id=metabase_group["id"],
        user_id=metabase_user["id"],  # type: ignore
    )
    pprint(metabase_relation)

    metabase_user_data = MetabaseUserData(
        user=user,
        metabase_id=metabase_user["id"], # type: ignore
        metabase_group_id=metabase_group["id"],
    )
    metabase_user_data.save()