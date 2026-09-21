from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("main", "0005_experience_identity")]

    operations = [
        migrations.AddField(
            model_name="project",
            name="links",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Example: [{"label": "Open project", "url": "https://example.com"}]',
            ),
        ),
    ]
