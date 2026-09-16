import secrets

from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import DiscographyEntry, Experience, Project

PROFILE_CONTEXT = {"name": "Arlen", "npm": "2506613514", "study_program": "S1 Ilmu Komputer", "bio": "I work across data, AI/ML, and music-making, interested in how technical systems and creative practice can make each other more meaningful."}


def show_main(request):
    return render(request, "index.html", {**PROFILE_CONTEXT, "projects": Project.objects.all(), "discography_entries": DiscographyEntry.objects.all()})


def show_experience(request):
    return render(request, "experience.html", {"name": "Arlen", "experience_list": Experience.objects.all()})


def has_valid_write_secret(request, submitted_secret):
    configured_secret = settings.PROJECT_WRITE_SECRET
    header_secret = request.headers.get("X-Project-Secret", "")
    return bool(configured_secret) and any(
        secrets.compare_digest(candidate, configured_secret)
        for candidate in (submitted_secret or "", header_secret)
    )


def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not has_valid_write_secret(request, form.cleaned_data["write_secret"]):
            form.add_error("write_secret", "Invalid write code.")
        else:
            form.save()
            messages.success(request, "Project added successfully.")
            return redirect("main:show_projects")
    return render(request, "projects_form.html", {"name": "Arlen", "form": form})


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    return HttpResponse(serializers.serialize("json", projects), content_type="application/json")


def show_projects(request):
    json_response = get_projects_json(request)
    projects = [item.object for item in serializers.deserialize("json", json_response.content.decode("utf-8"))]
    return render(request, "project.html", {"name": "Arlen", "project_list": projects, "title_query": request.GET.get("title", "").strip()})


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
    return redirect("main:show_projects")
