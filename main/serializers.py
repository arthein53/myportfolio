from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Project


class ProjectSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
    )
    links = serializers.ListField(
        child=serializers.DictField(),
        required=False,
    )
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "period",
            "organization",
            "link_label",
            "link_url",
            "links",
            "tags",
            "order",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = ["id"]

    def _validate_text(self, value, field_name):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError(f"{field_name} cannot be empty.")
        return value

    def validate_title(self, value):
        return self._validate_text(value, "Title")

    def validate_description(self, value):
        return self._validate_text(value, "Description")

    def validate_period(self, value):
        return self._validate_text(value, "Period")

    def validate_organization(self, value):
        return self._validate_text(value, "Organization")

    def validate_link_label(self, value):
        return self._validate_text(value, "Link label")

    def validate_tags(self, value):
        return [
            clean_tag
            for tag in value
            if (clean_tag := strip_tags(tag).strip())
        ]

    def validate_links(self, value):
        validated_links = []
        for link in value:
            label = strip_tags(str(link.get("label", ""))).strip()
            url = link.get("url", "")
            if not label or not isinstance(url, str):
                raise serializers.ValidationError(
                    "Each link must include a non-empty label and URL."
                )
            try:
                serializers.URLField().run_validation(url)
            except serializers.ValidationError as error:
                raise serializers.ValidationError(error.detail) from error
            validated_links.append({"label": label, "url": url})
        return validated_links

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and request.user in obj.starred_by.all()
        )

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    EDITABLE_FIELDS = (
        "title",
        "organization",
        "position",
        "period",
        "description",
        "category",
        "thumbnail",
        "ended_at",
    )
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id",
            "title",
            "organization",
            "position",
            "period",
            "description",
            "category",
            "category_display",
            "thumbnail",
            "started_at",
            "ended_at",
            "is_ongoing",
            "star_count",
            "is_starred",
        ]
        read_only_fields = [
            "id",
            "category_display",
            "started_at",
            "is_ongoing",
            "star_count",
            "is_starred",
        ]

    def _validate_text(self, value, field_name, *, required=False):
        cleaned_value = strip_tags(value).strip()
        if required and not cleaned_value:
            raise serializers.ValidationError(f"{field_name} cannot be empty.")
        return cleaned_value

    def validate_title(self, value):
        return self._validate_text(value, "Title", required=True)

    def validate_organization(self, value):
        return self._validate_text(value, "Organization")

    def validate_position(self, value):
        return self._validate_text(value, "Position")

    def validate_period(self, value):
        return self._validate_text(value, "Period")

    def validate_description(self, value):
        return self._validate_text(value, "Description", required=True)

    def validate_thumbnail(self, value):
        return self._validate_text(value, "Thumbnail")

    def validate(self, attrs):
        if self.instance is not None and not self.partial:
            missing_fields = [
                field_name
                for field_name in self.EDITABLE_FIELDS
                if field_name not in self.initial_data
            ]
            if missing_fields:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "PUT requires every editable field: "
                            + ", ".join(self.EDITABLE_FIELDS)
                            + "."
                        ]
                    }
                )
        return attrs

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.starred_by.filter(pk=request.user.pk).exists()
        )
