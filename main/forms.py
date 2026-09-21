from django import forms
from django.forms import ModelForm, NumberInput, PasswordInput, TextInput, Textarea, URLInput

from main.models import DiscographyEntry, Experience, Project


class ExperienceForm(ModelForm):
    write_secret = forms.CharField(
        label="Password",
        required=False,
        widget=PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "Portfolio password"}),
        help_text="Required to save changes. This value is never stored.",
    )

    class Meta:
        model = Experience
        fields = [
            "title",
            "organization",
            "position",
            "period",
            "description",
            "category",
            "thumbnail",
        ]
        labels = {
            "title": "Experience title",
            "organization": "Organization",
            "position": "Position",
            "period": "Period",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Thumbnail URL or static path",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Teaching Assistant"}),
            "organization": TextInput(attrs={"placeholder": "Universitas Indonesia"}),
            "position": TextInput(attrs={"placeholder": "Teaching Assistant"}),
            "period": TextInput(attrs={"placeholder": "Sep 2026 - Jan 2027"}),
            "description": Textarea(attrs={"placeholder": "Describe your role and contribution", "rows": 4}),
            "thumbnail": TextInput(attrs={"placeholder": "img/experience/organization/thumbnail.jpg"}),
        }
        help_texts = {
            "thumbnail": "Use a landscape image with a 4:3 ratio, such as 1200 × 900 px. Other ratios will be cropped to fit the card.",
        }


class DiscographyForm(ModelForm):
    roles = forms.CharField(
        label="Roles",
        required=False,
        widget=Textarea(attrs={"placeholder": "Composer, Producer", "rows": 2}),
        help_text="Separate each role with a comma.",
    )
    write_secret = forms.CharField(
        label="Password",
        required=False,
        widget=PasswordInput(attrs={"autocomplete": "off", "placeholder": "Project write code"}),
        help_text="Required to save a release. This value is never stored.",
    )

    class Meta:
        model = DiscographyEntry
        fields = ["title", "description", "release_type", "context", "audio_filename", "roles", "order"]
        widgets = {
            "title": TextInput(attrs={"placeholder": "Song title"}),
            "description": Textarea(attrs={"placeholder": "Describe the release", "rows": 4}),
            "release_type": TextInput(attrs={"placeholder": "Original song"}),
            "context": TextInput(attrs={"placeholder": "Personal project"}),
            "audio_filename": TextInput(attrs={"placeholder": "track.mp3"}),
            "order": NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.roles:
            self.initial["roles"] = ", ".join(self.instance.roles)

    def clean_roles(self):
        return [role.strip() for role in self.cleaned_data["roles"].split(",") if role.strip()]


class ProjectForm(ModelForm):
    tags = forms.CharField(
        label="Tags",
        required=False,
        widget=Textarea(attrs={"placeholder": "Django, Python, Machine Learning", "rows": 2}),
        help_text="Separate each tag with a comma.",
    )
    write_secret = forms.CharField(
        label="Password",
        required=False,
        widget=PasswordInput(attrs={"autocomplete": "off", "placeholder": "Project write code"}),
        help_text="Required to add a project. This value is never stored.",
    )

    class Meta:
        model = Project
        fields = ["title", "description", "period", "organization", "link_label", "link_url", "tags", "order"]
        labels = {"title": "Nama Proyek", "description": "Deskripsi Proyek", "period": "Periode", "organization": "Organisasi", "link_label": "Label Tautan", "link_url": "URL Proyek", "order": "Urutan"}
        widgets = {
            "title": TextInput(attrs={"placeholder": "Portfolio Website", "maxlength": 255}),
            "description": Textarea(attrs={"placeholder": "Tell your story", "rows": 3}),
            "period": TextInput(attrs={"placeholder": "2026"}),
            "organization": TextInput(attrs={"placeholder": "Personal"}),
            "link_label": TextInput(attrs={"placeholder": "Open project"}),
            "link_url": URLInput(attrs={"placeholder": "https://github.com/username/project"}),
            "order": NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.tags:
            self.initial["tags"] = ", ".join(self.instance.tags)

    def clean_tags(self):
        return [tag.strip() for tag in self.cleaned_data["tags"].split(",") if tag.strip()]
