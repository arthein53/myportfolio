from django.contrib import admin

from .models import DiscographyEntry, Experience, Project


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_ongoing", "started_at", "ended_at")
    list_filter = ("category", "ended_at")
    search_fields = ("title", "description")
    readonly_fields = ("id", "started_at")
    ordering = ("-started_at",)

    @admin.display(boolean=True, description="Status")
    def is_ongoing(self, obj):
        return obj.is_ongoing


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "period", "organization", "order")
    search_fields = ("title", "description", "organization")
    ordering = ("order", "title")


@admin.register(DiscographyEntry)
class DiscographyEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "release_type", "context", "audio_filename", "order")
    list_filter = ("release_type",)
    search_fields = ("title", "description", "context")
    ordering = ("order", "title")
