from rest_framework.views import APIView
from django.http import JsonResponse

from ...models import SupersetUserData
from ..connector.superset_conn import SupersetClient

class SupersetInvite(APIView):
    def post(self, request):
        current_user_id = request.user.id

        # Obtener el superset_user_id del usuario actual desde la base de datos
        superset_user_id = SupersetUserData.objects.get(user_id=current_user_id).superset_user_id
        superset_client = SupersetClient()
        try:
            # Superset no tiene un endpoint específico para reenviar invitaciones
            # Implementamos una solución alternativa, como enviar una notificación o correo manualmente
            response = superset_client.user.resend_invitation(superset_user_id)
            print(response)
            return JsonResponse({"message": "Invitation sent successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=400)
