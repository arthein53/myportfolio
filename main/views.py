import secrets
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DiscographyForm, ExperienceForm, ProjectForm
from .models import DiscographyEntry, Experience, Project


PROFILE_CONTEXT = {"name": "Arlen", "npm": "2506613514", "study_program": "S1 Ilmu Komputer", "bio": "I work across data, AI/ML, and music-making, interested in how technical systems and creative practice can make each other more meaningful."}


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    return render(
        request,
        "index.html",
        {
            **PROFILE_CONTEXT,
            "projects": Project.objects.all(),
            "discography_entries": DiscographyEntry.objects.all(),
            "last_login": last_login,
        },
    )


@login_required(login_url="/login/")
def show_edit(request):
    require_portfolio_owner(request)
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


def require_portfolio_owner(request):
    if not request.user.is_superuser:
        raise PermissionDenied


@login_required(login_url="/login/")
def create_experience(request):
    require_portfolio_owner(request)
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


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    require_portfolio_owner(request)
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


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    require_portfolio_owner(request)
    experience = get_object_or_404(Experience, pk=experience_id)
    destination = "main:show_edit" if request.POST.get("next") == "edit" else "main:show_experience"
    if request.method == "POST":
        if has_valid_write_secret(request, request.POST.get("password", "")):
            experience.delete()
            messages.success(request, "Experience deleted successfully.")
        else:
            messages.error(request, "Invalid password. Nothing was deleted.")
    return redirect(destination)


@login_required(login_url="/login/")
def create_project(request):
    require_portfolio_owner(request)
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


@login_required(login_url="/login/")
def update_project(request, project_id):
    require_portfolio_owner(request)
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


@login_required(login_url="/login/")
def update_discography(request, entry_id):
    require_portfolio_owner(request)
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


@login_required(login_url="/login/")
def delete_discography(request, entry_id):
    require_portfolio_owner(request)
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
    return HttpResponse(
        serializers.serialize("json", projects, use_natural_foreign_keys=True),
        content_type="application/json",
    )


def show_projects(request):
    json_response = get_projects_json(request)
    projects = [item.object for item in serializers.deserialize("json", json_response.content.decode("utf-8"))]
    return render(request, "project.html", {"name": "Arlen", "project_list": projects, "title_query": request.GET.get("title", "").strip()})


@login_required(login_url="/login/")
def delete_project(request, project_id):
    require_portfolio_owner(request)
    project = get_object_or_404(Project, pk=project_id)
    destination = "main:show_edit" if request.POST.get("next") == "edit" else "main:show_projects"
    if request.method == "POST":
        if has_valid_write_secret(request, request.POST.get("password", "")):
            project.delete()
            messages.success(request, "Project deleted successfully.")
        else:
            messages.error(request, "Invalid password. Nothing was deleted.")
    return redirect(destination)

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": PROFILE_CONTEXT["name"],
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": PROFILE_CONTEXT["name"],
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")
