import uuid

from django.core.validators import RegexValidator
from django.db import models


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ("internship", "Internship"),
        ("research", "Research"),
        ("volunteer", "Volunteer"),
        ("part-time", "Part-Time"),
        ("full-time", "Full-Time"),
        ("freelance", "Freelance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default="full-time")
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    period = models.CharField(max_length=100)
    organization = models.CharField(max_length=255)
    link_label = models.CharField(max_length=100)
    link_url = models.URLField()
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("order", "title")

    def __str__(self):
        return self.title


class ProjectTag(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tags")
    label = models.CharField(max_length=80)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "label")
        constraints = [models.UniqueConstraint(fields=("project", "label"), name="unique_project_tag")]

    def __str__(self):
        return self.label


class DiscographyEntry(models.Model):
    safe_audio_filename = RegexValidator(
        regex=r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.mp3$",
        message="Use an existing .mp3 filename from static/audio; paths are not allowed.",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    release_type = models.CharField(max_length=100)
    context = models.CharField(max_length=255)
    audio_filename = models.CharField(max_length=255, validators=[safe_audio_filename])
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("order", "title")
        verbose_name_plural = "discography entries"

    def __str__(self):
        return self.title


class DiscographyRole(models.Model):
    entry = models.ForeignKey(DiscographyEntry, on_delete=models.CASCADE, related_name="roles")
    label = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "label")
        constraints = [models.UniqueConstraint(fields=("entry", "label"), name="unique_discography_role")]

    def __str__(self):
        return self.label


class DiscographyLink(models.Model):
    entry = models.ForeignKey(DiscographyEntry, on_delete=models.CASCADE, related_name="links")
    label = models.CharField(max_length=100)
    url = models.URLField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "label")

    def __str__(self):
        return f"{self.entry}: {self.label}"
