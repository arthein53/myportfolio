from django.contrib import admin
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import DiscographyEntry, Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.project = Project.objects.create(
            title="Dynamic Portfolio Project",
            description="A project managed from Django Admin.",
            period="2026",
            organization="Personal",
            link_label="Open project",
            link_url="https://example.com/project",
            tags=["Django"],
            order=1,
        )
        self.release = DiscographyEntry.objects.create(
            title="Dynamic Release",
            description="A release managed from Django Admin.",
            release_type="Original song",
            context="Personal Project",
            audio_filename="Breaking_Horizon_Original_CompositionFull_Orchestration.mp3",
            roles=["Composer"],
            links=[{"label": "Listen", "url": "https://example.com/release"}],
            order=1,
        )

    def test_content_models_are_registered_in_admin(self):
        for model in (Project, DiscographyEntry):
            self.assertIn(model, admin.site._registry)

    def test_experience_is_registered_in_admin(self):
        self.assertIn(Experience, admin.site._registry)

    def test_main_url_is_accessible(self):
        with self.assertNumQueries(2):
            response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, self.project.title)
        self.assertContains(response, "Django")
        self.assertContains(response, self.release.title)
        self.assertContains(response, "Composer")
        self.assertContains(response, self.release.audio_filename)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")