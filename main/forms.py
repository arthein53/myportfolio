from django import forms
from django.forms import ModelForm, NumberInput, PasswordInput, TextInput, Textarea, URLInput

from main.models import Project


class ProjectForm(ModelForm):
    tags = forms.CharField(
        label="Tags",
        required=False,
        widget=Textarea(attrs={"placeholder": "Django, Python, Machine Learning", "rows": 2}),
        help_text="Separate each tag with a comma.",
    )
    write_secret = forms.CharField(
        label="Write code",
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
