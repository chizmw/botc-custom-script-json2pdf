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

        # MULTIPART_DATA is a bytes object; check that we do actually have bytes
        self.assertIsInstance(MULTIPART_DATA, bytes)

        multipart = MultipartDecoder(MULTIPART_DATA)
        self.assertEqual(multipart.boundary, "----WebKitFormBoundaryaJzDFsBAWm255fSZ")

        # the boundary should be a string, not bytes
        self.assertIsInstance(multipart.boundary, str)

        self.assertEqual(
            multipart.content_type,
            "multipart/form-data; boundary=----WebKitFormBoundaryaJzDFsBAWm255fSZ",
        )

        # we should have a field paperSize with a value Letter
        self.assertEqual(multipart.get_field("paperSize"), "Letter")

        # the paperSize field should be a string, not bytes
        self.assertIsInstance(multipart.get_field("paperSize"), str)

        # we should have a file file with a name Half of the 108.json
        filename = "Half of the 108.json"
        self.assertEqual(multipart.get_file(filename).get("name"), filename)

        # the file name should be a string, not bytes
        self.assertIsInstance(multipart.get_file(filename).get("name"), str)

        # get_file_names should return a list of strings; with our data we
        # should have one item in the list with a value of Half of the 108.json
        print(multipart.get_file_names())
        self.assertEqual(multipart.get_file_names(), [filename])
