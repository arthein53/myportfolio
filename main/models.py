import uuid

from django.core.validators import RegexValidator
from django.db import models


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ("internship", "Internship"),
        ("research", "Research"),
        ("seasonal", "Seasonal"),
        ("contract", "Contract"),
        ("volunteer", "Volunteer"),
        ("part-time", "Part-Time"),
        ("full-time", "Full-Time"),
        ("freelance", "Freelance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)
    period = models.CharField(max_length=100, blank=True)
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
    tags = models.JSONField(default=list, blank=True, help_text='Example: ["Django", "Python"]')
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("order", "title")

    def __str__(self):
        return self.title


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
    roles = models.JSONField(default=list, blank=True, help_text='Example: ["Writer", "Composer"]')
    links = models.JSONField(
        default=list,
        blank=True,
        help_text='Example: [{"label": "Listen", "url": "https://example.com"}]',
    )
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("order", "title")
        verbose_name_plural = "discography entries"

    def __str__(self):
        return self.title
