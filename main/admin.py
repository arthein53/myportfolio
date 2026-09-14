from django.contrib import admin

from .models import (
    DiscographyEntry,
    DiscographyLink,
    DiscographyRole,
    Experience,
    Project,
    ProjectTag,
)


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


class ProjectTagInline(admin.TabularInline):
    model = ProjectTag
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "period", "organization", "order")
    search_fields = ("title", "description", "organization")
    ordering = ("order", "title")
    inlines = (ProjectTagInline,)


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ("label", "project", "order")
    list_filter = ("project",)
    search_fields = ("label", "project__title")
    ordering = ("project", "order", "label")


class DiscographyRoleInline(admin.TabularInline):
    model = DiscographyRole
    extra = 1


class DiscographyLinkInline(admin.TabularInline):
    model = DiscographyLink
    extra = 1


@admin.register(DiscographyEntry)
class DiscographyEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "release_type", "context", "audio_filename", "order")
    list_filter = ("release_type",)
    search_fields = ("title", "description", "context")
    ordering = ("order", "title")
    inlines = (DiscographyRoleInline, DiscographyLinkInline)


@admin.register(DiscographyRole)
class DiscographyRoleAdmin(admin.ModelAdmin):
    list_display = ("label", "entry", "order")
    list_filter = ("entry",)
    search_fields = ("label", "entry__title")
    ordering = ("entry", "order", "label")


@admin.register(DiscographyLink)
class DiscographyLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "entry", "url", "order")
    list_filter = ("entry",)
    search_fields = ("label", "entry__title", "url")
    ordering = ("entry", "order", "label")
