from django.contrib.auth.models import Group, User
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Project


class MobileAuthTests(APITestCase):
    def test_register_creates_a_regular_account_without_a_session(self):
        password = "9c!sD5zAmR29"
        response = self.client.post(
            "/auth/register/",
            {"username": "mobile-user", "password1": password, "password2": password},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["message"])
        user = User.objects.get(username="mobile-user")
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_superuser)
        self.assertNotIn("sessionid", response.cookies)

    def test_registration_rejects_invalid_credentials_without_creating_accounts(self):
        password = "9c!sD5zAmR29"
        User.objects.create_user("already-taken")
        for username, password1, password2, error in (
            ("already-taken", password, password, "username"),
            ("mismatched", password, password + "x", "password2"),
            ("weak", "123", "123", "password2"),
            ("wrong-type", [], [], "detail"),
        ):
            with self.subTest(username=username):
                response = self.client.post(
                    "/auth/register/",
                    {"username": username, "password1": password1, "password2": password2},
                    format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(error, response.json())
        self.assertEqual(User.objects.count(), 1)

    def test_login_returns_token_and_project_create_capability_without_session(self):
        password = " 9c!sD5zAmR29 "
        member = User.objects.create_user("member", password=password)
        editor = User.objects.create_user("editor", password=password)
        editor.groups.add(Group.objects.create(name="Editor"))
        owner = User.objects.create_superuser("owner", password=password)
        for user, can_write in ((member, False), (editor, False), (owner, True)):
            with self.subTest(username=user.username):
                response = self.client.post(
                    "/auth/login/", {"username": user.username, "password": password}, format="json",
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data, {
                    "token": data["token"], "username": user.username, "can_write": can_write,
                })
                self.assertTrue(data["token"])
                self.assertNotIn("sessionid", response.cookies)

    def test_login_rejects_wrong_password_and_inactive_account(self):
        User.objects.create_user("active", password="test-passphrase")
        User.objects.create_user("disabled", password="test-passphrase", is_active=False)
        for username, password in (("active", "wrong"), ("disabled", "test-passphrase")):
            with self.subTest(username=username):
                response = self.client.post(
                    "/auth/login/", {"username": username, "password": password}, format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertNotIn("token", response.json())

    def test_logout_revokes_token_without_using_a_session(self):
        user = User.objects.create_user("member", password="test-passphrase")
        project = Project.objects.create(title="Starred project")
        project.starred_by.add(user)
        project_url = reverse("api:project-detail", args=[project.pk])

        login = self.client.post(
            "/auth/login/", {"username": user.username, "password": "test-passphrase"}, format="json",
        )
        self.assertEqual(login.status_code, 200)
        self.assertEqual(self.client.post("/auth/logout/").status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.json()['token']}")
        self.assertTrue(self.client.get(project_url).json()["is_starred"])
        logout = self.client.post("/auth/logout/")
        self.assertEqual(logout.status_code, 204)
        self.assertEqual(self.client.post("/auth/logout/").status_code, 401)
        self.assertEqual(self.client.get(project_url).status_code, 403)
        self.client.credentials()
        self.assertFalse(self.client.get(project_url).json()["is_starred"])

    @override_settings(PROJECT_WRITE_SECRET="test-write-code")
    def test_token_project_create_still_requires_owner_and_write_secret(self):
        client = APIClient(enforce_csrf_checks=True)
        member = User.objects.create_user("member", password="test-passphrase")
        editor = User.objects.create_user("editor", password="test-passphrase")
        editor.groups.add(Group.objects.create(name="Editor"))
        owner = User.objects.create_superuser("owner", password="test-passphrase")
        url = reverse("api:project-list")
        payload = {
            "title": "Mobile project",
            "description": "A mobile-created project.",
            "period": "2026",
            "organization": "Personal",
            "link_label": "Open project",
            "link_url": "https://example.com/project",
        }

        for user in (member, editor, owner):
            with self.subTest(username=user.username):
                login = client.post(
                    "/auth/login/", {"username": user.username, "password": "test-passphrase"}, format="json",
                )
                self.assertEqual(login.status_code, 200)
                client.credentials(HTTP_AUTHORIZATION=f"Token {login.json()['token']}")
                valid_payload = {**payload, "write_secret": "test-write-code"}
                if user == owner:
                    self.assertEqual(client.post(url, payload, format="json").status_code, 400)
                    self.assertEqual(client.post(url, {**payload, "write_secret": "wrong"}, format="json").status_code, 400)
                create = client.post(url, valid_payload, format="json")
                self.assertEqual(create.status_code, 201 if user == owner else 403)

        project = Project.objects.get(title=payload["title"])
        project.starred_by.add(owner)
        item = next(item for item in client.get(url).json() if item["id"] == project.pk)
        self.assertTrue(item["is_starred"])
        detail_url = reverse("api:project-detail", args=[project.pk])
        self.assertEqual(client.patch(detail_url, {"title": "No token edits"}, format="json").status_code, 403)
        self.assertEqual(client.delete(detail_url, {"write_secret": "test-write-code"}, format="json").status_code, 403)
        self.assertEqual(client.post(reverse("api:project-star", args=[project.pk])).status_code, 403)

    @override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:3000"])
    def test_allowlisted_web_origin_can_preflight_mobile_api_only(self):
        for path, method, allowed in (
            ("/auth/login/", "POST", True),
            ("/api/v1/projects/", "POST", True),
            ("/api/v1/projects/1/", "GET", True),
            ("/api/v1/projects/1/star/", "POST", False),
            ("/login/", "POST", False),
        ):
            with self.subTest(path=path):
                response = self.client.options(
                    path,
                    HTTP_ORIGIN="http://localhost:3000",
                    HTTP_ACCESS_CONTROL_REQUEST_METHOD=method,
                    HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization, content-type",
                )
                if allowed:
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:3000")
                    self.assertIn("authorization", response.headers["Access-Control-Allow-Headers"])
                    self.assertNotIn("Access-Control-Allow-Credentials", response.headers)
                else:
                    self.assertNotIn("Access-Control-Allow-Origin", response.headers)

    def test_unlisted_web_origin_has_no_cors_access(self):
        response = self.client.options(
            "/auth/login/",
            HTTP_ORIGIN="https://unlisted.example",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)