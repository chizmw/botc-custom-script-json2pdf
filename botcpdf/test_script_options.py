"""Tests for botcpdf.multipart module."""
import unittest

from botcpdf.script_options import ScriptOptions


class TestScriptOptions(unittest.TestCase):
    """Tests for botcpdf.script_options module."""

    def test_default_options(self):
        """Test correct values returned by _default_options"""
        # pylint: disable=protected-access
        defaults = ScriptOptions._default_options(None)
        # defaults should be a dict
        self.assertIsInstance(defaults, dict)
        # we should have 7 keys
        self.assertEqual(len(defaults.keys()), 7)
        # we should have the expected keys
        self.assertIn("paper_size", defaults.keys())
        self.assertIn("pdf_format", defaults.keys())
        self.assertIn("double_sided", defaults.keys())
        self.assertIn("player_night_order", defaults.keys())
        self.assertIn("simple_night_order", defaults.keys())
        self.assertIn("player_count", defaults.keys())
        self.assertIn("filename", defaults.keys())
        # we should have the expected values
        self.assertEqual(defaults["paper_size"], "A4")
        self.assertEqual(defaults["pdf_format"], "sample")
        self.assertEqual(defaults["double_sided"], True)
        self.assertEqual(defaults["player_night_order"], True)
        self.assertEqual(defaults["simple_night_order"], False)
        self.assertEqual(defaults["player_count"], 3)
        self.assertEqual(defaults["filename"], None)

    def test_multipart_init_no_options(self):
        """Test ScriptOoptions initialization."""

        options = ScriptOptions(None)

        # check we have the expected options set when we change nothing
        self.assertEqual(
            options.paper_size,
            "A4",
        )
        self.assertEqual(
            options.pdf_format,
            "sample",
        )
        self.assertEqual(
            options.double_sided,
            True,
        )
        self.assertEqual(
            options.player_night_order,
            True,
        )
        self.assertEqual(
            options.simple_night_order,
            False,
        )
        # although we have 3 in the dict in the code, the use of sample pdf_format
        # means we should have 1 here, becuase we set it in the code
        self.assertEqual(
            options.player_count,
            1,
        )

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
        self.assertEqual(
            options.paper_size,
            "Letter",
        )
        self.assertEqual(
            options.pdf_format,
            "sample",
        )
        self.assertEqual(
            options.double_sided,
            True,
        )
        self.assertEqual(
            options.player_night_order,
            True,
        )
        self.assertEqual(
            options.simple_night_order,
            False,
        )
        self.assertEqual(
            options.player_count,
            7,
        )
