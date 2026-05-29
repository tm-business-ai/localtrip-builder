from django.test import SimpleTestCase
from django.urls import reverse
from django.conf import settings


class HomePageTests(SimpleTestCase):
    def test_home_page_returns_success(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LocalTrip Builder")


class SecurityConfigurationTests(SimpleTestCase):
    def test_gitignore_contains_sensitive_file_patterns(self):
        gitignore = (settings.BASE_DIR / ".gitignore").read_text(encoding="utf-8")
        required_patterns = [
            ".env",
            ".env.*",
            "!.env.example",
            "db.sqlite3",
            "*.sqlite3",
            "logs/",
            "*.log",
            "media/",
            "uploads/",
            ".venv/",
            "venv/",
        ]

        for pattern in required_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, gitignore)

    def test_security_headers_are_enabled(self):
        self.assertTrue(settings.SECURE_CONTENT_TYPE_NOSNIFF)
        self.assertEqual(settings.X_FRAME_OPTIONS, "DENY")
