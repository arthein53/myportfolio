from django.urls import path

from main.views import (
    create_project,
    delete_project,
    get_projects_json,
    show_experience,
    show_main,
    show_projects,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<int:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects", get_projects_json, name="get_projects_json"),
    path("api/projects/", get_projects_json),
]
