"""Tests for botcpdf.multipart module."""

from botcpdf.script_options import ScriptOptions


class TestScriptOptions:
    """Tests for botcpdf.script_options module."""

    def test_default_options(self):
        """Test correct values returned by _default_options"""
        # pylint: disable=protected-access
        defaults = ScriptOptions._default_options(None)

        # defaults should be a dict
        assert isinstance(defaults, dict)
        # we should have 7 keys
        assert len(defaults.keys()) == 7
        # we should have the expected keys, and default values; because this is
        # test code, we're not bothered about pylint and the duplicate-code
        # warning
        # pylint: disable=duplicate-code
        expected_defaults = {
            "paper_size": "A4",
            "pdf_format": "sample",
            "double_sided": True,
            "player_night_order": True,
            "simple_night_order": False,
            # we set a weird default paired with sample pdf_format
            # so we can check that we both have it in the defaults and
            # (later in other tests)
            # verify that we override it correctly when 'sample' is set
            "player_count": 3,
            "filename": None,
        }
        for key, value in expected_defaults.items():
            assert (
                # pylint: disable=consider-iterating-dictionary
                key
                in defaults.keys()
            )
            #
            assert defaults[key] == value

    def test_multipart_init_no_options(self):
        """Test ScriptOptions initialization."""

        options = ScriptOptions(None)
        options.logger.debug(options)
        # print the keys of the options object
        options.logger.debug("option keys: %s", options.__dict__.keys())

        # check we have the expected options set when we change nothing
        # because this is test code, we're not bothered about pylint and the
        # duplicate-code warning
        # pylint: disable=duplicate-code
        expected_values = {
            "paper_size": "A4",
            "pdf_format": "sample",
            "double_sided": True,
            "player_night_order": True,
            "simple_night_order": False,
            # although we have 3 in the dict in the code, the use of sample
            # pdf_format means we should have 1 here, becuase we set it in the
            # code
            "player_count": 1,
            "filename": None,
        }
        for key, value in expected_values.items():
            assert hasattr(options, key), f"options.{key} not found"
            assert getattr(options, key) == value, f"expected options.{key}=={value}"

    def test_multipart_init_with_options(self):
        """Test ScriptOptions initialization with options."""
        use_options = {
            "paper_size": "Letter",
            "pdf_format": "sample",
            "player_count": "teensyville",
        }

        options = ScriptOptions(use_options)

        # check that we get the expected options set; "sample" pdf_format with a
        # couple of overrides that should still be set
        expected_values = {
            "paper_size": "Letter",
            "pdf_format": "sample",
            "double_sided": True,
            "player_night_order": True,
            "simple_night_order": False,
            "player_count": 7,
        }
        for key, value in expected_values.items():
            print(f"checking: options.{key}=={value}")
            assert hasattr(options, key)
            assert getattr(options, key) == value
