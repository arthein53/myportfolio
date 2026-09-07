from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import TestCase


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
