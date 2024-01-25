import requests
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response


class ActivateUserByGet(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uid, token):
        payload = {'uid': uid, 'token': token}

        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + '/users/activation/'

        response = requests.post(post_url, data=payload)

        if response.status_code == 204:
            return Response({'detail': 'User was successful activated'}, response.status_code)
        else:
            return Response(response.json())
