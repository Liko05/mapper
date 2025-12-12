"""
Unit tests for JavaCard AID parser (jcaid_parser.py)
"""
import unittest
from jcaid_parser import (
    is_section_marker,
    parse_basic_info,
    parse_key_info,
    parse_package_aid_table,
    parse_full_package_aid_table,
    convert_to_map_aid,
    BASIC_INFO
)

DEFAULT_DELIMITER = ";"


class TestJcaidParserHelpers(unittest.TestCase):
    """Tests for JavaCard AID parser helper functions."""

    def test_is_section_marker_card_info(self):
        """Test detection of Card info section marker."""
        self.assertEqual(is_section_marker("***** Card info;"), "Card info")
        self.assertEqual(is_section_marker("***** Card info"), "Card info")

    def test_is_section_marker_card_data(self):
        """Test detection of Card data section marker."""
        self.assertEqual(is_section_marker("***** CARD DATA"), "Card data")

    def test_is_section_marker_key_info(self):
        """Test detection of Key info section marker."""
        self.assertEqual(is_section_marker("***** KEY INFO"), "Key info")

    def test_is_section_marker_package_aid(self):
        """Test detection of Package AID section marker."""
        self.assertEqual(
            is_section_marker("PACKAGE AID; MAJOR VERSION; MINOR VERSION;"),
            "Package AID"
        )

    def test_is_section_marker_full_package_aid(self):
        """Test detection of Full package AID section marker."""
        self.assertEqual(
            is_section_marker("FULL PACKAGE AID; IS SUPPORTED?; PACKAGE NAME WITH VERSION;"),
            "Full package AID support"
        )

    def test_is_section_marker_invalid(self):
        """Test rejection of non-section markers."""
        self.assertIsNone(is_section_marker("Card ATR; 3B 00 00"))
        self.assertIsNone(is_section_marker("a0000000620001; 1; 0; java.lang"))
        self.assertIsNone(is_section_marker(""))

    def test_parse_basic_info(self):
        """Test parsing of basic information lines."""
        lines = [
            "jcAIDScan version; 0.1.1",
            "Card ATR; 3BFC180000813180459067464A00680804000000000E",
            "Card name; Feitian A22",
            "",
            "http://some-url.com"
        ]
        result = parse_basic_info(lines, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "jcAIDScan version")
        self.assertEqual(result[0]["value"], "0.1.1")
        self.assertEqual(result[1]["name"], "Card ATR")
        self.assertEqual(result[2]["name"], "Card name")

    def test_parse_basic_info_single_value(self):
        """Test parsing of single value lines (like NO CPLC)."""
        lines = [
            "Card name; Test Card",
            "NO CPLC",
            "NO CARD DATA"
        ]
        result = parse_basic_info(lines, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[1]["name"], "NO CPLC")
        self.assertEqual(result[1]["value"], "")

    def test_parse_key_info(self):
        """Test parsing of key info section."""
        lines = [
            "VER;255 ID;1 TYPE;DES3 LEN;16",
            "VER;255 ID;2 TYPE;DES3 LEN;16",
            "Key version suggests factory keys"
        ]
        result = parse_key_info(lines, DEFAULT_DELIMITER)

        self.assertEqual(len(result["keys"]), 2)
        self.assertEqual(result["keys"][0]["VER"], "255")
        self.assertEqual(result["keys"][0]["ID"], "1")
        self.assertEqual(result["keys"][0]["TYPE"], "DES3")
        self.assertEqual(result["keys"][0]["LEN"], "16")
        self.assertIn("Key version suggests factory keys", result["notes"])

    def test_parse_key_info_empty(self):
        """Test parsing of empty key info section."""
        lines = []
        result = parse_key_info(lines, DEFAULT_DELIMITER)

        self.assertEqual(len(result["keys"]), 0)
        self.assertNotIn("notes", result)

    def test_parse_package_aid_table(self):
        """Test parsing of package AID table."""
        lines = [
            "PACKAGE AID; MAJOR VERSION; MINOR VERSION; PACKAGE NAME; INTRODUCING JC API VERSION;",
            "a0000000620001; 1; 0; java.lang; 2.1",
            "a0000000620002; 1; 0; java.io; 2.2.0",
            "a0000000620101; 1; 3; javacard.framework; 2.2.2"
        ]
        result = parse_package_aid_table(lines, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["package_aid"], "a0000000620001")
        self.assertEqual(result[0]["major_version"], "1")
        self.assertEqual(result[0]["minor_version"], "0")
        self.assertEqual(result[0]["package_name"], "java.lang")
        self.assertEqual(result[0]["jc_api_version"], "2.1")

    def test_parse_package_aid_table_empty(self):
        """Test parsing of empty package AID table."""
        lines = ["PACKAGE AID; MAJOR VERSION; MINOR VERSION; PACKAGE NAME; INTRODUCING JC API VERSION;"]
        result = parse_package_aid_table(lines, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 0)

    def test_parse_full_package_aid_table(self):
        """Test parsing of full package AID support table."""
        lines = [
            "FULL PACKAGE AID; IS SUPPORTED?; PACKAGE NAME WITH VERSION;",
            "000107A0000000620001; \tyes; \tjava.lang v1.0 a0000000620001;",
            "010107A0000000620001; \tno; \tjava.lang v1.1 a0000000620001;",
            "000107A0000000620002; \tyes; \tjava.io v1.0 a0000000620002;"
        ]
        result = parse_full_package_aid_table(lines, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["full_package_aid"], "000107A0000000620001")
        self.assertTrue(result[0]["supported"])
        self.assertEqual(result[0]["package_name_version"], "java.lang v1.0 a0000000620001")

        self.assertFalse(result[1]["supported"])

    def test_parse_full_package_aid_table_case_insensitive(self):
        """Test that yes/no parsing is case insensitive."""
        lines = [
            "FULL PACKAGE AID; IS SUPPORTED?; PACKAGE NAME WITH VERSION;",
            "000107A0000000620001; YES; java.lang v1.0;",
            "010107A0000000620001; No; java.lang v1.1;",
            "020107A0000000620001; YES; java.lang v1.2;"
        ]
        result = parse_full_package_aid_table(lines, DEFAULT_DELIMITER)

        self.assertTrue(result[0]["supported"])
        self.assertFalse(result[1]["supported"])
        self.assertTrue(result[2]["supported"])


class TestJcaidParserConvertToMap(unittest.TestCase):
    """Tests for the main convert_to_map_aid function."""

    def test_convert_to_map_aid_basic(self):
        """Test basic conversion with simple AID data."""
        groups = [
            [
                "jcAIDScan version; 0.1.1",
                "Card ATR; 3BFC180000",
                "Card name; Test Card"
            ],
            ["***** Card info;"],
            ["NO CPLC"],
            ["***** KEY INFO"],
            ["VER;255 ID;1 TYPE;DES3 LEN;16"],
            ["Key version suggests factory keys"],
            ["PACKAGE AID; MAJOR VERSION; MINOR VERSION; PACKAGE NAME; INTRODUCING JC API VERSION;"],
            ["a0000000620001; 1; 0; java.lang; 2.1"],
            ["FULL PACKAGE AID; IS SUPPORTED?; PACKAGE NAME WITH VERSION;"],
            ["000107A0000000620001; yes; java.lang v1.0 a0000000620001;"]
        ]

        result = convert_to_map_aid(groups, DEFAULT_DELIMITER)

        self.assertEqual(result["_type"], "javacard-aid")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Key info", result)
        self.assertIn("Package AID", result)
        self.assertIn("Full package AID support", result)

    def test_convert_to_map_aid_basic_info(self):
        """Test that basic info is parsed correctly."""
        groups = [
            [
                "jcAIDScan version; 0.1.1",
                "Card ATR; 3BFC180000",
                "Card name; Test Card"
            ]
        ]

        result = convert_to_map_aid(groups, DEFAULT_DELIMITER)

        self.assertEqual(len(result[BASIC_INFO]), 3)
        self.assertEqual(result[BASIC_INFO][0]["name"], "jcAIDScan version")
        self.assertEqual(result[BASIC_INFO][0]["value"], "0.1.1")

    def test_convert_to_map_aid_key_info(self):
        """Test that key info is parsed correctly."""
        groups = [
            ["Card name; Test Card"],
            ["***** KEY INFO"],
            ["VER;255 ID;1 TYPE;DES3 LEN;16"],
            ["VER;255 ID;2 TYPE;AES LEN;32"],
            ["Factory keys"]
        ]

        result = convert_to_map_aid(groups, DEFAULT_DELIMITER)

        self.assertIn("Key info", result)
        self.assertEqual(len(result["Key info"]["keys"]), 2)
        self.assertEqual(result["Key info"]["keys"][1]["TYPE"], "AES")

    def test_convert_to_map_aid_package_tables(self):
        """Test that package AID tables are parsed correctly."""
        groups = [
            ["Card name; Test Card"],
            ["PACKAGE AID; MAJOR VERSION; MINOR VERSION; PACKAGE NAME; INTRODUCING JC API VERSION;"],
            ["a0000000620001; 1; 0; java.lang; 2.1"],
            ["a0000000620002; 1; 0; java.io; 2.2.0"],
            ["FULL PACKAGE AID; IS SUPPORTED?; PACKAGE NAME WITH VERSION;"],
            ["000107A0000000620001; yes; java.lang v1.0;"],
            ["010107A0000000620001; no; java.lang v1.1;"]
        ]

        result = convert_to_map_aid(groups, DEFAULT_DELIMITER)

        self.assertEqual(len(result["Package AID"]), 2)
        self.assertEqual(len(result["Full package AID support"]), 2)
        self.assertTrue(result["Full package AID support"][0]["supported"])
        self.assertFalse(result["Full package AID support"][1]["supported"])

    def test_convert_to_map_aid_empty_sections(self):
        """Test handling of empty optional sections."""
        groups = [
            ["Card name; Test Card"],
            ["***** Card info;"],
            ["***** CARD DATA"],
            ["***** KEY INFO"]
            # No key info, package AID, or full package AID data
        ]

        result = convert_to_map_aid(groups, DEFAULT_DELIMITER)

        self.assertEqual(result["_type"], "javacard-aid")
        self.assertIn(BASIC_INFO, result)


if __name__ == '__main__':
    unittest.main()

