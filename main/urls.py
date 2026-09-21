from django.urls import path

from main.views import (
    create_experience,
    create_project,
    delete_discography,
    delete_experience,
    delete_project,
    get_experiences_json,
    get_projects_json,
    show_edit,
    show_experience,
    show_main,
    show_projects,
    update_discography,
    update_experience,
    update_project,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("edit/", show_edit, name="show_edit"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/update/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("api/experiences", get_experiences_json, name="get_experiences_json"),
    path("api/experiences/", get_experiences_json),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<int:project_id>/update/", update_project, name="update_project"),
    path("projects/<int:project_id>/delete/", delete_project, name="delete_project"),
    path("discography/<int:entry_id>/update/", update_discography, name="update_discography"),
    path("discography/<int:entry_id>/delete/", delete_discography, name="delete_discography"),
    path("api/projects", get_projects_json, name="get_projects_json"),
    path("api/projects/", get_projects_json),
]
