from django.contrib import admin
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from main.forms import ProjectForm
from main.models import DiscographyEntry, Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="member", password="member-password")
        self.admin_user = User.objects.create_superuser(
            username="owner",
            password="owner-password",
            email="owner@example.com",
        )
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
            thumbnail="https://example.com/experience-thumbnail.jpg",
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

    def test_experience_uses_organization_position_and_period_fields(self):
        experience = Experience(
            title="Legacy title",
            organization="Organization",
            position="Position",
            period="Aug 2026 - Present",
            description="Structured experience content.",
        )
        experience.full_clean()


    def test_linkedin_employment_types_are_valid_categories(self):
        for category in ("seasonal", "contract", "freelance", "volunteer"):
            experience = Experience(
                title="LinkedIn role",
                description="Role imported from the LinkedIn profile.",
                category=category,
            )
            experience.full_clean()

    def test_seed_portfolio_command_is_idempotent(self):
        Experience.objects.all().delete()

        call_command("seed_portfolio", verbosity=0)
        call_command("seed_portfolio", verbosity=0)

        self.assertEqual(Experience.objects.count(), 21)
        self.assertEqual(Project.objects.filter(title="ParaLab AI/ML Architecture").count(), 1)
        self.assertFalse(Experience.objects.filter(organization="").exists())
        self.assertTrue(
            Experience.objects.filter(
                organization="Mercor",
                position="English Music & Lyrics Expert",
                period="Aug 2026 - Present",
            ).exists()
        )

    @override_settings(
        STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
    )
    def test_seed_portfolio_assigns_local_experience_thumbnails(self):
        Experience.objects.all().delete()

        call_command("seed_portfolio", verbosity=0)
        mercor = Experience.objects.get(
            organization="Mercor",
            position="English Music & Lyrics Expert",
        )

        self.assertEqual(mercor.thumbnail, "img/experience/mercor/mercor-thumbnail.png")
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "/static/img/experience/mercor/mercor-thumbnail.png")

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
        self.assertContains(response, self.experience.thumbnail)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Ongoing")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        for fragment in ("skills", "projects", "discography"):
            self.assertContains(response, f'href="{reverse("main:show_main")}#{fragment}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "No experience added yet.")

    def test_completed_experience(self):
        Experience.objects.exclude(pk=self.experience.pk).delete()
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Finished")
        self.assertNotContains(response, "Ongoing")

    def test_paralab_project_has_verified_public_links(self):
        call_command("seed_portfolio", verbosity=0)
        paralab = Project.objects.get(title="ParaLab AI/ML Architecture")

        self.assertEqual(paralab.period, "Sep 2026")
        self.assertEqual(paralab.organization, "22-Hour UI Hackathon")
        self.assertEqual(
            paralab.links,
            [
                {"label": "Open prototype", "url": "https://paralab-theta.vercel.app"},
                {
                    "label": "View GitHub",
                    "url": "https://github.com/Ini-statement-aku-yang-paling-baddie/paralab-architecture",
                },
            ],
        )
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, paralab.title)
        self.assertContains(response, "https://paralab-theta.vercel.app")
        self.assertContains(response, "https://github.com/Ini-statement-aku-yang-paling-baddie/paralab-architecture")

    def test_projects_page_deserializes_json_and_filters_by_title(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, self.project.title)
        filtered = self.client.get(reverse("main:show_projects"), {"title": "no match"})
        self.assertContains(filtered, "No projects match that title.")

    @override_settings(PROJECT_WRITE_SECRET="test-write-secret")
    def test_project_json_and_delete_endpoint(self):
        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, self.project.title)
        self.client.force_login(self.admin_user)
        deleted = self.client.post(reverse("main:delete_project", args=[self.project.pk]), {"password": "test-write-secret"})
        self.assertRedirects(deleted, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    @override_settings(PROJECT_WRITE_SECRET="test-write-secret")
    def test_create_project_requires_the_configured_secret(self):
        payload = {
            "title": "Protected Project", "description": "Created through the protected form.",
            "period": "2026", "organization": "Personal", "link_label": "Open",
            "link_url": "https://example.com/protected", "tags": '["Django"]', "order": 9,
        }
        self.client.force_login(self.admin_user)
        denied = self.client.post(reverse("main:create_project"), payload)
        self.assertEqual(denied.status_code, 200)
        self.assertFalse(Project.objects.filter(title="Protected Project").exists())
        allowed = self.client.post(reverse("main:create_project"), {**payload, "write_secret": "test-write-secret"})
        self.assertRedirects(allowed, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Protected Project").exists())

    @override_settings(PROJECT_WRITE_SECRET="test-write-secret")
    def test_create_project_accepts_the_secret_request_header(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse("main:create_project"), {"title": "Header Project", "description": "Protected through a header.", "period": "2026", "organization": "Personal", "link_label": "Open", "link_url": "https://example.com/header", "tags": '[]', "order": 10}, HTTP_X_PROJECT_SECRET="test-write-secret")
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Header Project").exists())

    def test_project_form_converts_comma_separated_tags_to_a_list(self):
        form = ProjectForm(data={"title": "Tag Test", "description": "Description", "period": "2026", "organization": "Personal", "link_label": "Open", "link_url": "https://example.com/tag-test", "tags": "Django, Python, Machine Learning", "order": 0, "write_secret": "unused"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["tags"], ["Django", "Python", "Machine Learning"])

    @override_settings(PROJECT_WRITE_SECRET="test-write-secret")
    def test_create_experience_with_model_form_requires_the_write_secret(self):
        payload = {
            "title": "Portfolio Maintainer",
            "organization": "Personal",
            "position": "Developer",
            "period": "Sep 2026 - Present",
            "description": "Maintains this Django portfolio.",
            "category": "part-time",
            "thumbnail": "https://example.com/portfolio.jpg",
        }

        self.client.force_login(self.admin_user)
        denied = self.client.post(reverse("main:create_experience"), payload)
        self.assertEqual(denied.status_code, 200)
        self.assertFalse(Experience.objects.filter(title="Portfolio Maintainer").exists())

        allowed = self.client.post(
            reverse("main:create_experience"),
            {**payload, "write_secret": "test-write-secret"},
        )
        self.assertRedirects(allowed, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(title="Portfolio Maintainer").exists())

    @override_settings(PROJECT_WRITE_SECRET="test-write-secret")
    def test_update_experience_with_model_form_updates_all_editable_fields(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.pk]),
            {
                "title": "Updated Experience",
                "organization": "Universitas Indonesia",
                "position": "Teaching Assistant",
                "period": "Sep 2026 - Jan 2027",
                "description": "Updated through the ModelForm.",
                "category": "contract",
                "thumbnail": "https://example.com/updated.jpg",
                "write_secret": "test-write-secret",
            },
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.organization, "Universitas Indonesia")
        self.assertEqual(self.experience.position, "Teaching Assistant")
        self.assertEqual(self.experience.category, "contract")

    @override_settings(PROJECT_WRITE_SECRET="test-write-secret")
    def test_experience_json_delete_and_deserialized_page(self):
        json_response = self.client.get(reverse("main:get_experiences_json"))

        self.assertEqual(json_response.status_code, 200)
        self.assertEqual(json_response["Content-Type"], "application/json")
        self.assertContains(json_response, self.experience.title)

        page_response = self.client.get(reverse("main:show_experience"))
        self.assertContains(page_response, self.experience.title)
        self.assertNotContains(page_response, reverse("main:update_experience", args=[self.experience.pk]))

        self.client.force_login(self.admin_user)
        update_page = self.client.get(reverse("main:update_experience", args=[self.experience.pk]))
        self.assertEqual(update_page.status_code, 200)
        self.assertTemplateUsed(update_page, "experience_form.html")

        deleted = self.client.post(reverse("main:delete_experience", args=[self.experience.pk]), {"password": "test-write-secret"})
        self.assertRedirects(deleted, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_edit_page_lists_projects_experiences_and_discography_with_controls(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("main:show_edit"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.release.title)
        self.assertContains(response, reverse("main:update_project", args=[self.project.pk]))
        self.assertContains(response, reverse("main:update_experience", args=[self.experience.pk]))
        self.assertContains(response, reverse("main:update_discography", args=[self.release.pk]))
        self.assertContains(response, reverse("main:delete_project", args=[self.project.pk]))
        self.assertContains(response, reverse("main:delete_experience", args=[self.experience.pk]))
        self.assertContains(response, reverse("main:delete_discography", args=[self.release.pk]))

    @override_settings(PROJECT_WRITE_SECRET="test-write-secret")
    def test_edit_forms_update_project_and_discography_data(self):
        self.client.force_login(self.admin_user)
        project_response = self.client.post(
            reverse("main:update_project", args=[self.project.pk]),
            {
                "title": "Updated Portfolio",
                "description": "Updated through the edit page.",
                "period": "2027",
                "organization": "Personal",
                "link_label": "Open",
                "link_url": "https://example.com/updated-project",
                "tags": "Django, Testing",
                "order": 2,
                "write_secret": "test-write-secret",
            },
        )
        self.assertRedirects(project_response, reverse("main:show_edit"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Updated Portfolio")
        self.assertEqual(self.project.tags, ["Django", "Testing"])

        release_response = self.client.post(
            reverse("main:update_discography", args=[self.release.pk]),
            {
                "title": "Updated Release",
                "description": "Updated through the edit page.",
                "release_type": "Original song",
                "context": "Personal Project",
                "audio_filename": "Breaking_Horizon_Original_CompositionFull_Orchestration.mp3",
                "roles": "Composer, Producer",
                "order": 2,
                "write_secret": "test-write-secret",
            },
        )
        self.assertRedirects(release_response, reverse("main:show_edit"))
        self.release.refresh_from_db()
        self.assertEqual(self.release.title, "Updated Release")
        self.assertEqual(self.release.roles, ["Composer", "Producer"])

        deleted = self.client.post(reverse("main:delete_discography", args=[self.release.pk]), {"password": "test-write-secret"})
        self.assertRedirects(deleted, reverse("main:show_edit"))
        self.assertFalse(DiscographyEntry.objects.filter(pk=self.release.pk).exists())

    def test_register_login_and_logout_manage_authentication_and_last_login_cookie(self):
        registration = self.client.post(
            reverse("main:register"),
            {"username": "new-member", "password1": "safe-password-123", "password2": "safe-password-123"},
        )
        self.assertRedirects(registration, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="new-member").exists())

        login_response = self.client.post(
            reverse("main:login"),
            {"username": "new-member", "password": "safe-password-123"},
        )
        self.assertRedirects(login_response, reverse("main:show_main"))
        self.assertIn("last_login", login_response.cookies)

        home = self.client.get(reverse("main:show_main"))
        self.assertContains(home, "Sesi Terakhir Login")
        self.assertContains(home, "new-member")

        logout_response = self.client.get(reverse("main:logout"))
        self.assertRedirects(logout_response, reverse("main:show_main"))
        self.assertEqual(logout_response.cookies["last_login"].value, "")

    @override_settings(PROJECT_WRITE_SECRET="test-write-secret")
    def test_only_superusers_can_change_projects(self):
        payload = {
            "title": "Protected Project",
            "description": "Only the owner may create this.",
            "period": "2026",
            "organization": "Personal",
            "link_label": "Open",
            "link_url": "https://example.com/protected",
            "tags": "Django",
            "order": 2,
            "write_secret": "test-write-secret",
        }

        anonymous = self.client.post(reverse("main:create_project"), payload)
        self.assertRedirects(anonymous, f"{reverse('main:login')}?next=%2Fprojects%2Fadd%2F")

        self.client.force_login(self.user)
        member = self.client.post(reverse("main:create_project"), payload)
        self.assertEqual(member.status_code, 403)

        self.client.force_login(self.admin_user)
        owner = self.client.post(reverse("main:create_project"), payload)
        self.assertRedirects(owner, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Protected Project").exists())

    def test_authenticated_users_can_toggle_project_stars(self):
        anonymous = self.client.post(reverse("main:toggle_star", args=[self.project.pk]))
        self.assertRedirects(anonymous, f"{reverse('main:login')}?next=%2Fprojects%2F{self.project.pk}%2Fstar%2F")

        self.client.force_login(self.user)
        starred = self.client.post(reverse("main:toggle_star", args=[self.project.pk]))
        self.assertRedirects(starred, reverse("main:show_projects"))
        self.assertTrue(self.project.starred_by.filter(pk=self.user.pk).exists())

        unstarred = self.client.post(reverse("main:toggle_star", args=[self.project.pk]))
        self.assertRedirects(unstarred, reverse("main:show_projects"))
        self.assertFalse(self.project.starred_by.filter(pk=self.user.pk).exists())

    def test_project_controls_match_user_permissions(self):
        anonymous_page = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(anonymous_page, reverse("main:create_project"))
        self.assertContains(anonymous_page, reverse("main:toggle_star", args=[self.project.pk]))

        self.client.force_login(self.admin_user)
        owner_page = self.client.get(reverse("main:show_projects"))
        self.assertContains(owner_page, reverse("main:create_project"))
