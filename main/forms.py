from django.forms import ModelForm, NumberInput, TextInput, Textarea, URLInput

from main.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "period",
            "organization",
            "link_label",
            "link_url",
            "tags",
            "order",
        ]
        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "period": "Periode",
            "organization": "Organisasi",
            "link_label": "Label Tautan",
            "link_url": "URL Proyek",
            "tags": "Tag",
            "order": "Urutan",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Portfolio Website", "maxlength": 255}),
            "description": Textarea(attrs={"placeholder": "Ceritakan proyekmu", "rows": 3}),
            "period": TextInput(attrs={"placeholder": "2026"}),
            "organization": TextInput(attrs={"placeholder": "Personal"}),
            "link_label": TextInput(attrs={"placeholder": "Open project"}),
            "link_url": URLInput(attrs={"placeholder": "https://github.com/username/project"}),
            "tags": Textarea(attrs={"placeholder": '["Django", "Python"]', "rows": 2}),
            "order": NumberInput(attrs={"min": 0}),
        }
