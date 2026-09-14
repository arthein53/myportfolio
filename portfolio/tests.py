import json
import os
from pathlib import Path
import subprocess
import sys

from django.conf import settings

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


class ProductionHardeningTests(TestCase):
    def test_static_assets_use_compressed_manifest_storage(self):
        self.assertEqual(
            settings.STORAGES["staticfiles"]["BACKEND"],
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
        )
        self.assertTrue(settings.WHITENOISE_KEEP_ONLY_HASHED_FILES)

    def test_templates_do_not_bypass_static_storage(self):
        templates_dir = Path(settings.BASE_DIR) / "templates"
        for template_path in templates_dir.glob("*.html"):
            self.assertNotIn('/static/', template_path.read_text())

    def test_production_enforces_https_security_settings(self):
        env = {
            **os.environ,
            "PRODUCTION": "True",
            "SECRET_KEY": "test-secret-key-for-production-settings-only-with-more-than-fifty-characters",
            "DB_NAME": "placeholder",
            "DB_USER": "placeholder",
            "DB_PASSWORD": "placeholder",
            "DB_HOST": "127.0.0.1",
            "DB_PORT": "5432",
        }
        probe = (
            "import json; from django.conf import settings; "
            "print(json.dumps({'debug': settings.DEBUG, "
            "'session_cookie_secure': settings.SESSION_COOKIE_SECURE, "
            "'csrf_cookie_secure': settings.CSRF_COOKIE_SECURE, "
            "'ssl_redirect': settings.SECURE_SSL_REDIRECT, "
            "'hsts_seconds': settings.SECURE_HSTS_SECONDS, "
            "'hsts_include_subdomains': settings.SECURE_HSTS_INCLUDE_SUBDOMAINS, "
            "'secret_key': settings.SECRET_KEY}))"
        )
        result = subprocess.run(
            [sys.executable, "manage.py", "shell", "-c", probe],
            cwd=settings.BASE_DIR,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        production = json.loads(result.stdout.splitlines()[-1])

        self.assertFalse(production["debug"])
        self.assertTrue(production["session_cookie_secure"])
        self.assertTrue(production["csrf_cookie_secure"])
        self.assertTrue(production["ssl_redirect"])
        self.assertEqual(production["hsts_seconds"], 31_536_000)
        self.assertTrue(production["hsts_include_subdomains"])
        self.assertEqual(production["secret_key"], env["SECRET_KEY"])
