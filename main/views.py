import secrets

from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DiscographyForm, ExperienceForm, ProjectForm
from .models import DiscographyEntry, Experience, Project

PROFILE_CONTEXT = {"name": "Arlen", "npm": "2506613514", "study_program": "S1 Ilmu Komputer", "bio": "I work across data, AI/ML, and music-making, interested in how technical systems and creative practice can make each other more meaningful."}


def show_main(request):
    return render(request, "index.html", {**PROFILE_CONTEXT, "projects": Project.objects.all(), "discography_entries": DiscographyEntry.objects.all()})


def show_edit(request):
    return render(
        request,
        "edit.html",
        {
            **PROFILE_CONTEXT,
            "projects": Project.objects.all(),
            "experience_list": Experience.objects.all(),
            "discography_entries": DiscographyEntry.objects.all(),
        },
    )


def get_experiences_json(request):
    return HttpResponse(
        serializers.serialize("json", Experience.objects.all()),
        content_type="application/json",
    )


def show_experience(request):
    json_response = get_experiences_json(request)
    experiences = [
        item.object
        for item in serializers.deserialize("json", json_response.content.decode("utf-8"))
    ]
    return render(request, "experience.html", {"name": "Arlen", "experience_list": experiences})


def has_valid_write_secret(request, submitted_secret):
    configured_secret = settings.PROJECT_WRITE_SECRET
    header_secret = request.headers.get("X-Project-Secret", "")
    return bool(configured_secret) and any(
        secrets.compare_digest(candidate, configured_secret)
        for candidate in (submitted_secret or "", header_secret)
    )


def create_experience(request):
    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not has_valid_write_secret(request, form.cleaned_data["write_secret"]):
            form.add_error("write_secret", "Invalid write code.")
        else:
            form.save()
            messages.success(request, "Experience added successfully.")
            return redirect("main:show_experience")
    return render(
        request,
        "experience_form.html",
        {"name": "Arlen", "form": form, "page_title": "Add experience", "submit_label": "Save experience"},
    )


def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)
    if request.method == "POST" and form.is_valid():
        if not has_valid_write_secret(request, form.cleaned_data["write_secret"]):
            form.add_error("write_secret", "Invalid write code.")
        else:
            form.save()
            messages.success(request, "Experience updated successfully.")
            return redirect("main:show_edit" if request.POST.get("next") == "edit" else "main:show_experience")
    return render(
        request,
        "experience_form.html",
        {"name": "Arlen", "form": form, "page_title": "Update experience", "submit_label": "Update experience", "experience": experience, "next": request.GET.get("next", "")},
    )


def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    destination = "main:show_edit" if request.POST.get("next") == "edit" else "main:show_experience"
    if request.method == "POST":
        if has_valid_write_secret(request, request.POST.get("password", "")):
            experience.delete()
            messages.success(request, "Experience deleted successfully.")
        else:
            messages.error(request, "Invalid password. Nothing was deleted.")
    return redirect(destination)


def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not has_valid_write_secret(request, form.cleaned_data["write_secret"]):
            form.add_error("write_secret", "Invalid write code.")
        else:
            form.save()
            messages.success(request, "Project added successfully.")
            return redirect("main:show_projects")
    return render(
        request,
        "projects_form.html",
        {"name": "Arlen", "form": form, "page_title": "Add New Project", "submit_label": "Save project", "cancel_url": "main:show_projects"},
    )


def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        if not has_valid_write_secret(request, form.cleaned_data["write_secret"]):
            form.add_error("write_secret", "Invalid write code.")
        else:
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect("main:show_edit")
    return render(
        request,
        "projects_form.html",
        {"name": "Arlen", "form": form, "page_title": "Update Project", "submit_label": "Update project", "cancel_url": "main:show_edit"},
    )


def update_discography(request, entry_id):
    entry = get_object_or_404(DiscographyEntry, pk=entry_id)
    form = DiscographyForm(request.POST or None, instance=entry)
    if request.method == "POST" and form.is_valid():
        if not has_valid_write_secret(request, form.cleaned_data["write_secret"]):
            form.add_error("write_secret", "Invalid write code.")
        else:
            form.save()
            messages.success(request, "Release updated successfully.")
            return redirect("main:show_edit")
    return render(request, "discography_form.html", {"name": "Arlen", "form": form})


def delete_discography(request, entry_id):
    entry = get_object_or_404(DiscographyEntry, pk=entry_id)
    if request.method == "POST":
        if has_valid_write_secret(request, request.POST.get("password", "")):
            entry.delete()
            messages.success(request, "Release deleted successfully.")
        else:
            messages.error(request, "Invalid password. Nothing was deleted.")
    return redirect("main:show_edit")


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
    destination = "main:show_edit" if request.POST.get("next") == "edit" else "main:show_projects"
    if request.method == "POST":
        if has_valid_write_secret(request, request.POST.get("password", "")):
            project.delete()
            messages.success(request, "Project deleted successfully.")
        else:
            messages.error(request, "Invalid password. Nothing was deleted.")
    return redirect(destination)
