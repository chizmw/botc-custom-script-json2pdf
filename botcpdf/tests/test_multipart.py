"""Tests for botcpdf.multipart module."""

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


class TestMultipart:
    """Tests for botcpdf.multipart module."""

    def test_multipart_init(self):
        """Test MultipartDecoder initialization."""

        # MULTIPART_DATA is a bytes object; check that we do actually have bytes
        assert isinstance(MULTIPART_DATA, bytes)

        multipart = MultipartDecoder(MULTIPART_DATA)
        assert multipart.boundary is not None
        assert multipart.boundary == "----WebKitFormBoundaryaJzDFsBAWm255fSZ"

        # the boundary should be a string, not bytes
        assert isinstance(multipart.boundary, str)

        assert (
            multipart.content_type
            == "multipart/form-data; boundary=----WebKitFormBoundaryaJzDFsBAWm255fSZ"
        )

        # we should have a field paperSize with a value Letter
        assert multipart.get_field("paperSize") == "Letter"

        # the paperSize field should be a string, not bytes
        assert isinstance(multipart.get_field("paperSize"), str)

        # we should have a file file with a name Half of the 108.json
        filename = "Half of the 108.json"
        assert multipart.get_file(filename).get("name") == filename

        # the file name should be a string, not bytes
        assert isinstance(multipart.get_file(filename).get("name"), str)

        # get_file_names should return a list of strings; with our data we
        # should have one item in the list with a value of Half of the 108.json
        assert isinstance(multipart.get_file_names(), list)
        assert len(multipart.get_file_names()) == 1
        assert multipart.get_file_names()[0] == filename

    def test_lambda_behaviour(self):
        """Test that the lambda behaviour works as expected"""
        # we should refactor to actually call methods, not just copy paste what
        # we did in the lambda.py file

        # event is just a dict with a body key that has the MULTIPART_DATA
        # value
        event = {"body": MULTIPART_DATA}

        multipart = MultipartDecoder(event["body"])
        # multipart should be a MultipartDecoder object
        assert isinstance(multipart, MultipartDecoder)

        uploaded_files = multipart.get_file_names()
        # uploaded_files should be a list
        assert isinstance(uploaded_files, list)

        file_info = multipart.get_file(uploaded_files[0])
        # file_info should be a dict
        assert isinstance(file_info, dict)

        # grab some info about the file
        file_name = file_info["name"]
        file_contents = file_info["json"]

        # file_name should be a string
        assert isinstance(file_name, str)
        # file_contents should be a json object
        assert isinstance(file_contents, list)
