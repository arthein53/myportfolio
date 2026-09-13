from django.contrib import admin

from .models import Experience


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
