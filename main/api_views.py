from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from main.models import Experience, Project
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly
from main.serializers import ExperienceSerializer, ProjectSerializer
from main.views import has_valid_write_secret


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("starred_by").order_by("order", "title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)

        serializer = ProjectSerializer(projects, many=True, context={"request": request})
        return Response(serializer.data)

    payload = request.data.copy()
    write_secret = payload.get("write_secret", "")
    payload.pop("write_secret", None)
    if not has_valid_write_secret(request, write_secret):
        return Response(
            {"write_secret": ["Invalid write code."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ProjectSerializer(data=payload, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(Project.objects.prefetch_related("starred_by"), pk=project_id)

    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        write_secret = request.data.get("write_secret", "")
        if not has_valid_write_secret(request, write_secret):
            return Response(
                {"write_secret": ["Invalid write code."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project.objects.prefetch_related("starred_by"), pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)

    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    if request.method in ("GET", "HEAD"):
        experiences = Experience.objects.prefetch_related("starred_by").order_by(
            "-started_at",
            "title",
        )
        title = request.query_params.get("title", "").strip()
        if title:
            experiences = experiences.filter(title__icontains=title)

        serializer = ExperienceSerializer(
            experiences,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    payload = request.data.copy()
    write_secret = payload.get("write_secret", "")
    payload.pop("write_secret", None)
    if not has_valid_write_secret(request, write_secret):
        return Response(
            {"write_secret": ["Invalid write code."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ExperienceSerializer(data=payload, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    experience = get_object_or_404(
        Experience.objects.prefetch_related("starred_by"),
        pk=experience_id,
    )

    if request.method in ("GET", "HEAD"):
        serializer = ExperienceSerializer(experience, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        write_secret = request.data.get("write_secret", "")
        if not has_valid_write_secret(request, write_secret):
            return Response(
                {"write_secret": ["Invalid write code."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ExperienceSerializer(
        experience,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    experience = get_object_or_404(
        Experience.objects.prefetch_related("starred_by"),
        pk=experience_id,
    )
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)

    serializer = ExperienceSerializer(experience, context={"request": request})
    return Response(serializer.data)
