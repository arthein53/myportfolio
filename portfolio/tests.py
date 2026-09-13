from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import Client, TestCase


class AudioRangeTests(TestCase):
    filename = "Breaking_Horizon_Original_CompositionFull_Orchestration.mp3"

    def test_audio_endpoint_honors_byte_range_requests(self):
        response = self.client.get(
            f"/audio/{self.filename}",
            HTTP_RANGE="bytes=10-19",
        )

        source = Path(finders.find(f"audio/{self.filename}"))
        expected = source.read_bytes()[10:20]

        self.assertEqual(response.status_code, 206)
        self.assertEqual(response["Accept-Ranges"], "bytes")
        self.assertEqual(response["Content-Length"], "10")
        self.assertEqual(
            response["Content-Range"],
            f"bytes 10-19/{source.stat().st_size}",
        )
        self.assertEqual(b"".join(response.streaming_content), expected)


class AdminCsrfProxyTests(TestCase):
    def test_admin_login_accepts_https_origin_forwarded_by_pws(self):
        get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password-123",
        )
        client = Client(enforce_csrf_checks=True)
        host = "rafael-arlen-myportfolio.pws.cs.ui.ac.id"
        login_page = client.get("/admin/login/", HTTP_HOST=host)

        response = client.post(
            "/admin/login/",
            {
                "username": "admin",
                "password": "test-password-123",
                "csrfmiddlewaretoken": login_page.cookies["csrftoken"].value,
            },
            HTTP_HOST=host,
            HTTP_ORIGIN="https://rafael-arlen-myportfolio.pws.cs.ui.ac.id",
            HTTP_X_FORWARDED_PROTO="https",
        )

        self.assertEqual(response.status_code, 302)
