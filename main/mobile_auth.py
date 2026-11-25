from django.contrib.auth.forms import UserCreationForm
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    parser_classes,
    permission_classes,
    renderer_classes,
)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from main.permissions import can_create_projects


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
def register(request):
    fields = ("username", "password1", "password2")
    if not isinstance(request.data, dict) or any(
        key in request.data and not isinstance(request.data[key], str) for key in fields
    ):
        return Response(
            {"detail": "Expected a JSON object with string credentials."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    form = UserCreationForm(request.data)
    if not form.is_valid():
        return Response(dict(form.errors), status=status.HTTP_400_BAD_REQUEST)

    form.save()
    return Response(
        {"message": "Account created. Please log in."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
def login(request):
    serializer = AuthTokenSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            "token": token.key,
            "username": user.get_username(),
            "can_write": can_create_projects(user),
        },
        headers={"Cache-Control": "no-store"},
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def logout(request):
    request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)