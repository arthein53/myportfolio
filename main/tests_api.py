from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            password="owner-password",
            email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor",
            password="visitor-password",
        )
        self.project = Project.objects.create(
            title="Unique API Portfolio",
            description="My website",
            period="2026",
            organization="Personal",
            link_label="Open project",
            link_url="https://example.com/portfolio",
            tags=["Django"],
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.pk])
        self.star_url = reverse("api:project-star", args=[self.project.pk])
        self.payload = {
            "title": "New project",
            "description": "A useful app",
            "period": "2026",
            "organization": "Personal",
            "link_label": "Open project",
            "link_url": "https://example.com/new-project",
            "tags": ["Python"],
            "order": 2,
        }

    def test_public_list_returns_the_drf_project_contract(self):
        response = self.client.get(self.list_url, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_data = next(item for item in response.data if item["id"] == self.project.pk)
        self.assertEqual(project_data["title"], self.project.title)
        self.assertEqual(project_data["tags"], ["Django"])
        self.assertEqual(project_data["star_count"], 0)
        self.assertFalse(project_data["is_starred"])
        self.assertNotIn("fields", project_data)

    def test_owner_can_create_with_the_configured_write_secret(self):
        self.client.force_authenticate(user=self.owner)

        with self.settings(PROJECT_WRITE_SECRET="test-write-secret"):
            response = self.client.post(
                self.list_url,
                {**self.payload, "write_secret": "test-write-secret"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], self.payload["title"])
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_owner_can_create_with_the_write_secret_header(self):
        self.client.force_authenticate(user=self.owner)

        with self.settings(PROJECT_WRITE_SECRET="test-write-secret"):
            response = self.client.post(
                self.list_url,
                self.payload,
                format="json",
                HTTP_X_PROJECT_SECRET="test-write-secret",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_search_detail_and_missing_project(self):
        response = self.client.get(self.list_url, {"title": "unique api"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.get(reverse("api:project-detail", args=[999999])).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_guest_and_visitor_cannot_manage_projects(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url,
                    {"title": "Changed"},
                    format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_serializer_rejects_invalid_input_and_ignores_computed_fields(self):
        self.client.force_authenticate(user=self.owner)

        with self.settings(PROJECT_WRITE_SECRET="test-write-secret"):
            invalid_response = self.client.post(
                self.list_url,
                {
                    **self.payload,
                    "title": '<img src="x" onerror="alert(1)">',
                    "link_url": "javascript:alert(1)",
                    "write_secret": "test-write-secret",
                },
                format="json",
            )
            valid_response = self.client.post(
                self.list_url,
                {
                    **self.payload,
                    "star_count": 99,
                    "is_starred": True,
                    "starred_by_names": "forged",
                    "write_secret": "test-write-secret",
                },
                format="json",
            )

        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", invalid_response.data)
        self.assertIn("link_url", invalid_response.data)
        self.assertEqual(valid_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(valid_response.data["star_count"], 0)
        self.assertFalse(valid_response.data["is_starred"])

    def test_owner_can_put_and_delete_with_the_configured_write_secret(self):
        self.client.force_authenticate(user=self.owner)

        incomplete_response = self.client.put(
            self.detail_url,
            {"title": "Incomplete"},
            format="json",
        )
        replace_response = self.client.put(self.detail_url, self.payload, format="json")
        with self.settings(PROJECT_WRITE_SECRET="test-write-secret"):
            delete_response = self.client.delete(
                self.detail_url,
                {"write_secret": "test-write-secret"},
                format="json",
            )

        self.assertEqual(incomplete_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(replace_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(delete_response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_owner_can_patch_a_project_without_overwriting_other_fields(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url,
            {"title": "Updated portfolio"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Updated portfolio")
        self.assertEqual(self.project.description, "My website")

    def test_authenticated_visitor_can_toggle_a_star(self):
        self.client.force_authenticate(user=self.visitor)

        first_response = self.client.post(self.star_url)
        second_response = self.client.post(self.star_url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertTrue(first_response.data["is_starred"])
        self.assertEqual(first_response.data["star_count"], 1)
        self.assertFalse(second_response.data["is_starred"])
        self.assertEqual(second_response.data["star_count"], 0)

    def test_star_requires_login_and_wrong_methods_are_rejected(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.get(self.star_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_session_writes_require_a_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="owner-password"))

        with self.settings(
            PROJECT_WRITE_SECRET="test-write-secret",
            STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}},
        ):
            payload = {**self.payload, "write_secret": "test-write-secret"}
            without_token = client.post(self.list_url, payload, format="json")
            page = client.get(self.list_url, HTTP_ACCEPT="text/html")
            token = client.cookies["csrftoken"].value
            with_token = client.post(
                self.list_url,
                payload,
                format="json",
                HTTP_X_CSRFTOKEN=token,
            )

        self.assertEqual(without_token.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        self.assertEqual(with_token.status_code, status.HTTP_201_CREATED)

    def test_session_delete_requires_a_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="owner-password"))

        with self.settings(
            PROJECT_WRITE_SECRET="test-write-secret",
            STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}},
        ):
            payload = {"write_secret": "test-write-secret"}
            without_token = client.delete(self.detail_url, payload, format="json")
            client.get(self.list_url, HTTP_ACCEPT="text/html")
            token = client.cookies["csrftoken"].value
            with_token = client.delete(
                self.detail_url,
                payload,
                format="json",
                HTTP_X_CSRFTOKEN=token,
            )

        self.assertEqual(without_token.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(with_token.status_code, status.HTTP_204_NO_CONTENT)

    def test_session_star_requires_a_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="visitor", password="visitor-password"))

        with self.settings(
            STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}},
        ):
            without_token = client.post(self.star_url)
            client.get(self.list_url, HTTP_ACCEPT="text/html")
            token = client.cookies["csrftoken"].value
            with_token = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)

        self.assertEqual(without_token.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(with_token.status_code, status.HTTP_200_OK)
        self.assertTrue(with_token.data["is_starred"])
