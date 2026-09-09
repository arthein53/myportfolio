from django.shortcuts import render
from main.models import Experience

def show_main(request):
    context = {
        "name": "Arlen",
        "npm": "2506613514",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "I work across data, AI/ML, and music-making, interested in how technical systems and creative practice can make each other more meaningful."
        ),
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Arlen",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)