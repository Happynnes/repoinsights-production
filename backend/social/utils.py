from rest_framework_simplejwt.tokens import RefreshToken
import json

def generate_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    token = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return token


def get_user_data_dict(user):
    user_data = {
        "login": user.github_username,
        "name": user.github_username,
        "email": user.github_email,
        "avatar": user.github_avatar_url,
        "user_url": user.github_url,
        "github_id": user.github_id,
        "bio": user.github_bio,
        "company_name": user.github_company,
        "location": user.github_location,
        "user_url": user.github_url,
        "github_id": user.github_id,
    }
    return json.dumps(user_data)