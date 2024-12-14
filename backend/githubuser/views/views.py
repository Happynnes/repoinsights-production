from pprint import pprint
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db.models import F

from urllib.parse import urlparse, parse_qs
import requests
import json
from datetime import datetime

from social.models import PrivateRepository
from social.models import UserTokens as UserTokensModel
from rabbitmq.utils import format_dt
from rabbitmq.connector import QueueController


class GitHubProjects(APIView):
    def get(self, request):
        project_per_page = 5
        current_page = int(request.GET.get("page", 1))
        url = f"https://api.github.com/user/repos?page={current_page}&per_page={project_per_page}&sort=updated&visibility=all"
        headers = {"Authorization": f"token {request.user.github_access_token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                projects = []
                for project in data:
                    projects.append(
                        {
                            "name": project["name"],
                            "owner": project["owner"]["login"],
                            "description": project["description"],
                            "language": project["language"],
                            "url": project["html_url"],
                            "id": project["id"],
                            "added": self.check_if_project_is_added(
                                project["name"], project["id"], request.user
                            ),
                            "loading": False,
                        }
                    )
                next_page_link = self.get_next_page_link(response.headers)
                next_page_number = (
                    self.get_page_number(next_page_link) if next_page_link else None
                )
                projects_response = {
                    "projects": projects,
                    "pagination": {
                        "next": next_page_number,
                        "prev": current_page - 1 if current_page > 1 else None,
                        "current": current_page,
                    },
                }
                return JsonResponse(projects_response, safe=True)
            else:
                print("Error al obtener los proyectos:", response.json())
                return JsonResponse(
                    {
                        "error": "Error al obtener los proyectos de GitHub",
                        "message": response.json(),
                    },
                    status=response.status_code,
                )
        except Exception as e:
            print("Error al obtener los proyectos:", str(e))
            return JsonResponse({"error": "Something went wrong"}, status=500)

    def check_if_project_is_added(self, repo_name, project_id, user):
        try:
            repo = PrivateRepository.objects.get(
                repo_id=project_id, user=user, repo_name=repo_name
            )
            return True
        except PrivateRepository.DoesNotExist:
            return False

    def get_next_page_link(self, headers):
        link_header = headers.get("Link", "")
        links = link_header.split(", ")
        for link in links:
            if 'rel="next"' in link:
                url = link[link.index("<") + 1 : link.index(">")]
                return url
        return None

    def get_page_number(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return int(query_params["page"][0]) if "page" in query_params else None


class GitHubAddProject(APIView):
    def post(self, request):
        current_user = request.user
        queue_controller = QueueController()
        user = request.user
        try:
            data = json.loads(request.body)
            # check if exists
            if PrivateRepository.objects.filter(
                repo_id=data.get("id"), user=user
            ).exists():
                return JsonResponse(
                    {"error": "Project already exists"}, safe=True, status=400
                )

            repo = PrivateRepository(
                user=user,
                owner_id=user.github_id,
                owner=data.get("owner"),
                repo_id=data.get("id"),
                repo_name=data.get("name"),
                repo_url=data.get("url"),
            )
            repo.save()

            # get current_user github access token
            user_tokens = current_user.github_access_token
            if not user_tokens:
                return JsonResponse(
                    {"error": "User has no github access token"}, safe=True, status=400
                )

            project_message = {
                "enqueue_time": format_dt(datetime.now()),
                "attempt": 1,
                "owner": data["owner"],
                "project": data["name"],
                "private": user_tokens,
                "user_id": user.id,
                "last_extraction": None,
            }
            queue_controller.connect()
            queue_controller.enqueue(project_message)

            return JsonResponse(
                {"message": "Project added successfully"}, safe=True, status=200
            )
        except Exception as e:
            print("Error al agregar el proyecto:", str(e))
            return JsonResponse(
                {"error": "Error al agregar el proyecto"}, safe=True, status=500
            )


class UserTokens(APIView):
    def hide_last_chars(self, token: str) -> str:
        n = 25
        first_chrs = token[:-n]
        asterics = "*" * n
        token_hidded = first_chrs + asterics
        return token_hidded[:20]

    def get(self, request):
        user = request.user
        try:
            tokens = (
                UserTokensModel.objects.filter(user=user)
                .annotate(token=F("access_token"), created_date=F("created_at"))
                .values("token", "created_date")
            )
            tokens = list(tokens)

            oauth_token = self.hide_last_chars(user.github_access_token)
            access_tokens = []
            access_tokens.append(
                {"value": oauth_token, "created_at": user.date_joined, "type": "OAuth"}
            )
            for token in tokens:
                access_tokens.append(
                    {
                        "value": self.hide_last_chars(token["token"]),
                        "created_at": token["created_date"],
                        "type": "Personal",
                    }
                )
            response = {"data": access_tokens}
            return JsonResponse(response, safe=True)
        except Exception as e:
            print("Error al obtener los tokens del usuario:", str(e))
            return JsonResponse(
                {"error": "Error al obtener los tokens del usuario"},
                safe=True,
                status=500,
            )


class UserAddTokens(APIView):
    def post(self, request):
        user = request.user
        try:
            data = json.loads(request.body)
            token = data.get("token")
            if UserTokensModel.objects.filter(user=user, access_token=token).exists():
                return JsonResponse(
                    {"error": "Token already exists"}, safe=True, status=400
                )
            user_token = UserTokensModel(user=user, access_token=token)
            user_token.save()
            return JsonResponse(
                {"message": "Token added successfully"}, safe=True, status=200
            )
        except Exception as e:
            print("Error al obtener los datos del usuario:", str(e))
            return JsonResponse(
                {"error": "Error al obtener los datos del usuario"},
                safe=True,
                status=500,
            )


class GitHubCheckPrivate(APIView):
    def get(self, request):
        user = request.user
        oauth_token = user.github_access_token
        if not oauth_token:
            return JsonResponse(
                {"error": "User has no github access token"}, safe=True, status=400
            )
        url = f"https://api.github.com/user/repos?visibility=private"
        response = requests.get(url, headers={"Authorization": f"token {oauth_token}"})
        if response.status_code == 200:
            total = len(response.json())
            if total > 0:
                return JsonResponse({"private": True}, safe=True, status=200)
            else:
                return JsonResponse({"private": False}, safe=True, status=200)
        return JsonResponse(
            {"private": False, "error": "Error al obtener los proyectos de GitHub"},
            status=response.status_code,
        )
