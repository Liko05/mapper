"""
Unit tests for TPM parser (tpm_parser.py)
"""
import unittest
from tpm_parser import (
    is_tpm_operation,
    is_config_line,
    parse_basic_info,
    parse_key_value_pairs,
    parse_stats_line,
    parse_data_group,
    convert_to_map_tpm,
    BASIC_INFO
)

DEFAULT_DELIMITER = ";"


class TestTpmParserHelpers(unittest.TestCase):
    """Tests for TPM parser helper functions."""

    def test_is_tpm_operation_valid(self):
        """Test detection of valid TPM operation headers."""
        self.assertTrue(is_tpm_operation("TPM2_Create"))
        self.assertTrue(is_tpm_operation("TPM2_Sign"))
        self.assertTrue(is_tpm_operation("TPM2_RSA_Decrypt"))
        self.assertTrue(is_tpm_operation("TPM2_VerifySignature"))
        self.assertTrue(is_tpm_operation("  TPM2_Create  "))

    def test_is_tpm_operation_invalid(self):
        """Test rejection of non-TPM operation lines."""
        self.assertFalse(is_tpm_operation("Key parameters:;RSA 1024"))
        self.assertFalse(is_tpm_operation("operation stats (ms/op):;avg op:;315.61"))
        self.assertFalse(is_tpm_operation("TPM2_Create;something"))
        self.assertFalse(is_tpm_operation(""))
        self.assertFalse(is_tpm_operation("Some random text"))

    def test_is_config_line_valid(self):
        """Test detection of valid configuration lines."""
        self.assertTrue(is_config_line("Key parameters:;RSA 1024"))
        self.assertTrue(is_config_line("Algorithm:;0x0006"))
        self.assertTrue(is_config_line("Hash algorithm:;SHA-256"))
        self.assertTrue(is_config_line("Data length (bytes):;256"))

    def test_is_config_line_invalid(self):
        """Test rejection of non-configuration lines."""
        self.assertFalse(is_config_line("TPM2_Create"))
        self.assertFalse(is_config_line("operation stats (ms/op):;avg op:;315.61"))
        self.assertFalse(is_config_line(""))

    def test_parse_basic_info(self):
        """Test parsing of basic information section."""
        lines = [
            "Tested and provided by;John Doe",
            "Execution date/time; 2019/05/17 09:03:05",
            "Manufacturer; INTC",
        ]
        result = parse_basic_info(lines, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "Tested and provided by")
        self.assertEqual(result[0]["value"], "John Doe")
        self.assertEqual(result[1]["name"], "Execution date/time")
        self.assertEqual(result[1]["value"], "2019/05/17 09:03:05")

    def test_parse_key_value_pairs(self):
        """Test parsing of key-value pairs from config lines."""
        line = "Key parameters:;ECC 0x0003"
        result = parse_key_value_pairs(line, DEFAULT_DELIMITER)
        self.assertEqual(result["Key parameters"], "ECC 0x0003")

        line = "Algorithm:;0x0006;Key length:;128;Mode:;0x0040"
        result = parse_key_value_pairs(line, DEFAULT_DELIMITER)
        self.assertEqual(result["Algorithm"], "0x0006")
        self.assertEqual(result["Key length"], "128")
        self.assertEqual(result["Mode"], "0x0040")

    def test_parse_stats_line(self):
        """Test parsing of operation stats lines."""
        line = "operation stats (ms/op):;avg op:;315.61;min op:;308.45;max op:;340.50"
        result = parse_stats_line(line, DEFAULT_DELIMITER)

        self.assertEqual(result["avg op"], "315.61")
        self.assertEqual(result["min op"], "308.45")
        self.assertEqual(result["max op"], "340.50")

    def test_parse_stats_line_operation_info(self):
        """Test parsing of operation info lines."""
        line = "operation info:;total iterations:;1000;successful:;1000;failed:;0;error:;None"
        result = parse_stats_line(line, DEFAULT_DELIMITER)

        self.assertEqual(result["total iterations"], "1000")
        self.assertEqual(result["successful"], "1000")
        self.assertEqual(result["failed"], "0")
        self.assertEqual(result["error"], "None")

    def test_parse_data_group(self):
        """Test parsing of a complete data group."""
        group = [
            "Key parameters:;RSA 1024",
            "operation stats (ms/op):;avg op:;996.97;min op:;192.47;max op:;4708.57",
            "operation info:;total iterations:;1000;successful:;1000;failed:;0;error:;None"
        ]
        result = parse_data_group(group, DEFAULT_DELIMITER)

        self.assertEqual(result["Key parameters"], "RSA 1024")
        self.assertEqual(result["avg op"], "996.97")
        self.assertEqual(result["total iterations"], "1000")


class TestTpmParserConvertToMap(unittest.TestCase):
    """Tests for the main convert_to_map_tpm function."""

    def test_convert_to_map_tpm_basic(self):
        """Test basic conversion with a simple TPM data structure."""
        groups = [
            # Basic info group
            ["Manufacturer; INTC", "Firmware version; 11.0.0.1202"],
            # TPM operation header
            ["TPM2_Create"],
            # Data group
            [
                "Key parameters:;RSA 1024",
                "operation stats (ms/op):;avg op:;100.00;min op:;90.00;max op:;110.00",
                "operation info:;total iterations:;100;successful:;100;failed:;0;error:;None"
            ]
        ]

        result = convert_to_map_tpm(groups, DEFAULT_DELIMITER)

        self.assertEqual(result["_type"], "tpm")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("TPM2_Create", result)
        self.assertEqual(len(result["TPM2_Create"]), 1)
        self.assertEqual(result["TPM2_Create"][0]["Key parameters"], "RSA 1024")

    def test_convert_to_map_tpm_multiple_operations(self):
        """Test conversion with multiple TPM operations."""
        groups = [
            ["Manufacturer; INTC"],
            ["TPM2_Create"],
            ["Key parameters:;RSA 1024", "operation stats (ms/op):;avg op:;100.00;min op:;90.00;max op:;110.00"],
            ["TPM2_Sign"],
            ["Key parameters:;ECC 0x0003;Scheme:;0x0018", "operation stats (ms/op):;avg op:;145.32;min op:;131.96;max op:;156.38"]
        ]

        result = convert_to_map_tpm(groups, DEFAULT_DELIMITER)

        self.assertIn("TPM2_Create", result)
        self.assertIn("TPM2_Sign", result)
        self.assertEqual(result["TPM2_Sign"][0]["Key parameters"], "ECC 0x0003")
        self.assertEqual(result["TPM2_Sign"][0]["Scheme"], "0x0018")

    def test_convert_to_map_tpm_empty_groups(self):
        """Test handling of empty groups."""
        groups = [
            ["Manufacturer; INTC"],
            [],
            ["TPM2_Create"],
            [],
            ["Key parameters:;RSA 1024", "operation stats (ms/op):;avg op:;100.00;min op:;90.00;max op:;110.00"]
        ]

        result = convert_to_map_tpm(groups, DEFAULT_DELIMITER)

        self.assertEqual(result["_type"], "tpm")
        self.assertIn("TPM2_Create", result)


if __name__ == '__main__':
    unittest.main()

