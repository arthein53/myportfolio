from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProjectForm

from main.models import DiscographyEntry, Experience, Project


def show_main(request):
    context = {
        "name": "Arlen",
        "npm": "2506613514",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "I work across data, AI/ML, and music-making, interested in how technical systems and creative practice can make each other more meaningful."
        ),
        "projects": Project.objects.all(),
        "discography_entries": DiscographyEntry.objects.all(),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Arlen",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_main")

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "projects_form.html", context)
