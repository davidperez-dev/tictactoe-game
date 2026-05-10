import os

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class StatusView(APIView):
    """GET /api/v1/status/  →  { status, version }  (public)"""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "version": os.environ.get("APP_VERSION", "unknown"),
            }
        )
