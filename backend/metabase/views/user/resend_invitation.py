from rest_framework.views import APIView
from django.http import JsonResponse


from ...models import MetabaseUserData
from ..connector.metabase_conn import MetabaseClient

class MetabaseInvite(APIView):
    def post(self, request):
        current_user_id = request.user.id

        metabase_user_id = MetabaseUserData.objects.get(user_id=current_user_id).metabase_user_id
        metabase_client = MetabaseClient()
        try:
            response = metabase_client.user.resend_invitation(metabase_user_id)
            print(response)
            return JsonResponse({"message": "Invitation sent successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=400)


