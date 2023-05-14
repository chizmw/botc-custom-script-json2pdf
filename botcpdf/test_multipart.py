"""Tests for botcpdf.multipart module."""
import unittest

from botcpdf.multipart import MultipartDecoder


# pylint: disable=line-too-long
MULTIPART_DATA = (
    b"------WebKitFormBoundaryaJzDFsBAWm255fSZ\r\n"
    b'Content-Disposition: form-data; name="paperSize"\r\n'
    b"\r\n"
    b"Letter\r\n"
    b"------WebKitFormBoundaryaJzDFsBAWm255fSZ\r\n"
    b'Content-Disposition: form-data; name="file"; filename="Half of the 108.json"\r\n'
    b"Content-Type: application/json\r\n"
    b"\r\n"
    b'[{"id": "washerwoman"}, {"id": "librarian"}, {"id": "investigator"}, {"id": "chef"}, {"id": "empath"}, {"id": "fortune_teller"}, {"id": "undertaker"}, {"id": "monk"}, {"id": "ravenkeeper"}, {"id": "virgin"}, {"id": "slayer"}, {"id": "soldier"}, {"id": "mayor"}, {"id": "butler"}, {"id": "drunk"}, {"id": "recluse"}, {"id": "saint"}, {"id": "poisoner"}, {"id": "spy"}, {"id": "baron"}, {"id": "scarlet_woman"}, {"id": "legion"}, {"id": "imp"}, {"id": "vortox"}]\r\n'
    b"------WebKitFormBoundaryaJzDFsBAWm255fSZ--"
)


class TestMultipart(unittest.TestCase):
    """Tests for botcpdf.multipart module."""

    def test_multipart_init(self):
        """Test MultipartDecoder initialization."""
        multipart = MultipartDecoder(MULTIPART_DATA)
        self.assertEqual(multipart.boundary, b"----WebKitFormBoundaryaJzDFsBAWm255fSZ")

        self.assertEqual(
            multipart.content_type,
            "multipart/form-data; boundary=----WebKitFormBoundaryaJzDFsBAWm255fSZ",
        )

        # we should have a field paperSize with a value Letter
        self.assertEqual(multipart.get_field("paperSize"), "Letter")

        # we should have a file file with a name Half of the 108.json
        filename = "Half of the 108.json"
        self.assertEqual(multipart.get_file(filename).get("name"), filename)
