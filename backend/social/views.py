from time import sleep
import hashlib
from typing import Dict
from django.http import JsonResponse
import requests
import json
from pprint import pprint
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.contrib.auth import get_user_model
from metabase.views.connector.create_role_and_policy import create_user_with_policy
from psycopg2.errors import DuplicateObject
from metabase.views.connector.metabase_conn import MetabaseClient
from metabase.models import MetabaseUserData
from django.conf import settings

from social.models import PrivateRepository
from social.utils import generate_jwt_token, get_user_data_dict

User = get_user_model()


class GithubLogin(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client_id = settings.GITHUB_CLIENT_ID
        scopes = "%20".join(settings.GITHUB_SCOPES)
        url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope={scopes}"
        return Response({"auth_url": url}, status=status.HTTP_200_OK)


class GithubGrantPrivateRepo(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client_id = settings.GITHUB_CLIENT_ID
        private_scope = "repo"
        scopes = settings.GITHUB_SCOPES.copy()
        scopes.append(private_scope)
        str_scopes = "%20".join(scopes)
        url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope={str_scopes}"
        return Response({"auth_url": url}, status=status.HTTP_200_OK)


class GithubCallback(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            frontend_url = f"{settings.FRONTEND_URL}/auth/callback?error=access_denied"
            return redirect(frontend_url)

        access_token = self.get_access_token(code)
        if not access_token:
            return Response(
                {"error": "Access token not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_data = self.get_user_data(access_token)
        if user_data.get("error"):
            return Response(
                user_data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        primary_email = self.get_primary_email(access_token)
        if not primary_email:
            return Response(
                {"error": "Failed to fetch user email from GitHub"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = self.create_or_update_user(user_data, primary_email, access_token)
        if not user:
            return Response(
                {"error": "Failed to create or update user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        password = self.generate_password_from_github_username(user.github_username)  # type: ignore
        user.set_password(password)
        user.save()

        token = generate_jwt_token(user)
        request.session["access_token"] = access_token
        user_data = get_user_data_dict(user)
        frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={token['access']}&user={user_data}"
        return redirect(frontend_url)

    def generate_password_from_github_username(self, username: str):
        github_username = username.lower()
        password = hashlib.sha256(github_username.encode()).hexdigest()
        return password

    def get_access_token(self, code) -> str | None:
        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
        }
        headers = {"Accept": "application/json"}
        response = requests.post(
            "https://github.com/login/oauth/access_token", data=data, headers=headers
        )
        response_json: Dict = response.json()
        return response_json.get("access_token")

    def get_user_data(self, access_token) -> Dict:
        user_data_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"},
        )
        response = user_data_response.json()
        if user_data_response.status_code == 200:
            return response

        return {
            "error": "Failed to fetch user data from GitHub",
            "message": response["message"],
        }

    def get_primary_email(self, access_token):
        email_response = requests.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"token {access_token}"},
        )
        if email_response.status_code == 200:
            email_data = email_response.json()
            for email in email_data:
                if email.get("primary"):
                    return email.get("email")
        return None

    def create_or_update_user(self, user_data, primary_email, access_token):
        github_id = user_data.get("id")
        if not github_id:
            return None
        print(user_data)
        try:
            user = User.objects.get(github_id=github_id)
            user.github_username = user_data.get("login")  # type: ignore
            user.github_access_token = access_token  # type: ignore
            user.save()
            return user

        except User.DoesNotExist:
            user = User.objects.create_user(  # type: ignore
                username=user_data.get("login"),
                email=primary_email,
                github_id=github_id,
                github_username=user_data.get("login"),
                github_email=primary_email,
                github_avatar_url=user_data.get("avatar_url"),
                github_access_token=access_token,
                github_url=user_data.get("html_url"),
                github_bio=user_data.get("bio"),
                github_company=user_data.get("company"),
                github_location=user_data.get("location"),
                # Agregar otros campos según sea necesario
            )
            #self.create_metabase_user(user)
            return user

    def create_metabase_user(self, user):
        try:
            metabase_client = MetabaseClient()
            pprint("Creating metabase user...")
            user_id, group_id = metabase_client.user.create_user(
                fname=user.github_username, email=user.github_email
            )

            metabase_client.group.add_user_to_group(group_id=group_id, user_id=user_id)
            repoinsights_user, repoinsights_password = (
                user.github_username,
                user.github_username,
            )
            try:
                create_user_with_policy(
                    dbname=settings.CONSOLIDADA_DATABASE,
                    dbuser=settings.CONSOLIDADA_USER,
                    dbhost=settings.CONSOLIDADA_IP,
                    dbpassword=settings.CONSOLIDADA_PASSWORD,
                    dbport=settings.CONSOLIDADA_PORT,
                    username=repoinsights_user,
                    password=repoinsights_password,
                )
            except SyntaxError as e:
                print("Error al crear el usuario de la base de datos:", str(e))
                raise e
            except DuplicateObject as e:
                print("El usuario ya existe:", str(e))

            pprint("Creating metabase user...")
            metabase_db_name = f"{repoinsights_user}_consolidada"
            database_id = metabase_client.database.obtener_id_database(metabase_db_name)
            if database_id is None:
                database_id = metabase_client.connection.agregar_conexion_metabase(
                    dbname=settings.CONSOLIDADA_DATABASE,
                    host=settings.CONSOLIDADA_IP,
                    puerto=settings.CONSOLIDADA_PORT,
                    nombre=metabase_db_name,
                    usuario=repoinsights_user,
                    password=repoinsights_password,
                    tipo_motor="postgres",
                )
                sleep(5)
                database_id = metabase_client.database.obtener_id_database(
                    metabase_db_name
                )
            pprint(database_id)
            graph = metabase_client.permissions.permissions_graph()
            pprint(graph)
            if database_id is not None:
                updated_graph = metabase_client.access.restringir_acceso_base_datos(
                    graph, database_id, group_id
                )
                pprint(updated_graph)

            metabase_user_data = MetabaseUserData(
                user_id=user.id,
                metabase_user_id=user_id,
                metabase_group_id=group_id,
                metabase_db_id=database_id,
            )
            metabase_user_data.save()

        except Exception as e:
            pprint("Error creating metabase user")
            raise e


class RegularLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        print(username, password)
        if username is None or password is None:
            return JsonResponse(
                {"error": "Please provide both username and password"},
                status=400,
            )
        user = User.objects.filter(email=username, github_id=password).first()
        print(user)
        if user is None:
            return JsonResponse({"error": "Invalid credentials"}, status=400)
        print("Generating token")
        token = generate_jwt_token(user)
        user_data = get_user_data_dict(user)
        return JsonResponse({"token": token["access"], "user": user_data})
