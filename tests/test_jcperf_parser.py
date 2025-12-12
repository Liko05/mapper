"""
Unit tests for JavaCard Performance parser (jcperf_parser.py)
"""
import unittest
from jcperf_parser import (
    is_section_header,
    is_section_end,
    is_method_name_line,
    extract_section_name,
    parse_basic_info,
    parse_measurement_config,
    parse_measurements,
    parse_stats,
    parse_operation_info,
    parse_method_block,
    convert_to_map_jcperf,
    BASIC_INFO
)

DEFAULT_DELIMITER = ";"


class TestJcperfParserHelpers(unittest.TestCase):
    """Tests for JavaCard performance parser helper functions."""

    def test_is_section_header_fixed_format(self):
        """Test detection of fixed format section headers."""
        self.assertTrue(is_section_header("MESSAGE DIGEST"))
        self.assertTrue(is_section_header("RANDOM GENERATOR"))
        self.assertTrue(is_section_header("CIPHER"))
        self.assertTrue(is_section_header("SIGNATURE"))
        self.assertTrue(is_section_header("KEY PAIR"))

    def test_is_section_header_variable_format(self):
        """Test detection of variable format section headers."""
        self.assertTrue(is_section_header("MESSAGE DIGEST - ALG_SHA - variable data - BEGIN"))
        self.assertTrue(is_section_header("CIPHER - TYPE_DES LENGTH_DES ALG_DES_CBC_NOPAD - variable data - BEGIN"))

    def test_is_section_header_invalid(self):
        """Test rejection of non-section headers."""
        self.assertFalse(is_section_header("method name:; ALG_SHA"))
        self.assertFalse(is_section_header("baseline measurements (ms):;27.00"))
        self.assertFalse(is_section_header(""))

    def test_is_section_end(self):
        """Test detection of section end markers."""
        self.assertTrue(is_section_end("MESSAGE DIGEST - END"))
        self.assertTrue(is_section_end("CIPHER - TYPE_DES - variable data - END"))
        self.assertFalse(is_section_end("MESSAGE DIGEST"))
        self.assertFalse(is_section_end(""))

    def test_is_method_name_line(self):
        """Test detection of method name lines."""
        self.assertTrue(is_method_name_line("method name:; ALG_SHA MessageDigest_doFinal()"))
        self.assertTrue(is_method_name_line("method name:; ALG_SHA MessageDigest_doFinal();16;"))
        self.assertFalse(is_method_name_line("baseline measurements (ms):;27.00"))
        self.assertFalse(is_method_name_line(""))

    def test_extract_section_name_fixed(self):
        """Test extraction of section name from fixed format."""
        self.assertEqual(extract_section_name("MESSAGE DIGEST"), "MESSAGE DIGEST")
        self.assertEqual(extract_section_name("CIPHER"), "CIPHER")

    def test_extract_section_name_variable(self):
        """Test extraction of section name from variable format."""
        self.assertEqual(
            extract_section_name("MESSAGE DIGEST - ALG_SHA - variable data - BEGIN"),
            "MESSAGE DIGEST - ALG_SHA"
        )
        self.assertEqual(
            extract_section_name("CIPHER - TYPE_DES LENGTH_DES ALG_DES_CBC_NOPAD - variable data - BEGIN"),
            "CIPHER - TYPE_DES LENGTH_DES ALG_DES_CBC_NOPAD"
        )

    def test_parse_measurement_config(self):
        """Test parsing of measurement config lines."""
        line = "measurement config:;appletPrepareINS;34;appletMeasureINS;41;config;00 15 00 01"
        result = parse_measurement_config(line, DEFAULT_DELIMITER)

        self.assertEqual(result["appletPrepareINS"], "34")
        self.assertEqual(result["appletMeasureINS"], "41")
        self.assertEqual(result["config"], "00 15 00 01")

    def test_parse_measurements_dot_decimal(self):
        """Test parsing of measurements with dot decimal separator."""
        line = "baseline measurements (ms):;27.00;7.00;7.00;9.00;9.00;"
        result = parse_measurements(line, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], "27.00")
        self.assertEqual(result[1], "7.00")

    def test_parse_measurements_comma_decimal(self):
        """Test parsing of measurements with comma decimal separator (European format)."""
        line = "baseline measurements (ms):;103,00;115,00;101,00;104,00;102,00;"
        result = parse_measurements(line, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], "103.00")  # Converted to dot
        self.assertEqual(result[1], "115.00")

    def test_parse_measurements_with_check(self):
        """Test that CHECK is filtered from measurements."""
        line = "baseline measurements (ms):;27.00;7.00;7.00;;;CHECK"
        result = parse_measurements(line, DEFAULT_DELIMITER)

        self.assertEqual(len(result), 3)
        self.assertNotIn("CHECK", result)

    def test_parse_stats_baseline(self):
        """Test parsing of baseline stats."""
        line = "baseline stats (ms):;avg:;11.80;min:;7.00;max:;27.00;;;CHECK"
        result = parse_stats(line, DEFAULT_DELIMITER)

        self.assertEqual(result["avg"], "11.80")
        self.assertEqual(result["min"], "7.00")
        self.assertEqual(result["max"], "27.00")

    def test_parse_stats_operation(self):
        """Test parsing of operation stats."""
        line = "operation stats (ms/op):;avg op:;1.05;min op:;0.96;max op:;1.38;;CHECK"
        result = parse_stats(line, DEFAULT_DELIMITER)

        self.assertEqual(result["avg op"], "1.05")
        self.assertEqual(result["min op"], "0.96")
        self.assertEqual(result["max op"], "1.38")

    def test_parse_stats_comma_decimal(self):
        """Test parsing of stats with comma decimal separator."""
        line = "baseline stats (ms):;avg:;105,00;min:;101,00;max:;115,00"
        result = parse_stats(line, DEFAULT_DELIMITER)

        self.assertEqual(result["avg"], "105.00")
        self.assertEqual(result["min"], "101.00")
        self.assertEqual(result["max"], "115.00")

    def test_parse_operation_info(self):
        """Test parsing of operation info line."""
        line = "operation info:;data length;256;total iterations;250;total invocations;250;"
        result = parse_operation_info(line, DEFAULT_DELIMITER)

        self.assertEqual(result["data length"], "256")
        self.assertEqual(result["total iterations"], "250")
        self.assertEqual(result["total invocations"], "250")


class TestJcperfParserMethodBlock(unittest.TestCase):
    """Tests for parse_method_block function."""

    def test_parse_method_block_supported(self):
        """Test parsing of a supported method block."""
        lines = [
            "method name:; ALG_SHA MessageDigest_doFinal()",
            "measurement config:;appletPrepareINS;34;appletMeasureINS;41;config;00 15",
            "baseline measurements (ms):;27.00;7.00;7.00;",
            "baseline stats (ms):;avg:;11.80;min:;7.00;max:;27.00",
            "operation raw measurements (ms):;69.20;49.20;48.20;",
            "operation stats (ms/op):;avg op:;1.05;min op:;0.96;max op:;1.38",
            "operation info:;data length;256;total iterations;250;total invocations;250"
        ]
        result = parse_method_block(lines, DEFAULT_DELIMITER)

        self.assertEqual(result["method name"], "ALG_SHA MessageDigest_doFinal()")
        self.assertTrue(result["supported"])
        self.assertIn("baseline measurements", result)
        self.assertIn("operation stats", result)

    def test_parse_method_block_unsupported(self):
        """Test parsing of an unsupported method block."""
        lines = [
            "method name:; ALG_MD5 MessageDigest_doFinal()",
            "measurement config:;appletPrepareINS;34;appletMeasureINS;41;config;00 15",
            "NO_SUCH_ALGORITHM"
        ]
        result = parse_method_block(lines, DEFAULT_DELIMITER)

        self.assertEqual(result["method name"], "ALG_MD5 MessageDigest_doFinal()")
        self.assertFalse(result["supported"])

    def test_parse_method_block_variable_format(self):
        """Test parsing of variable format method block with data length."""
        lines = [
            "method name:; ALG_SHA MessageDigest_doFinal();16;",
            "measurement config:;appletPrepareINS;34;appletMeasureINS;41;config;00 15",
            "baseline measurements (ms):;103,00;115,00;",
            "baseline stats (ms):;avg:;105,00;min:;101,00;max:;115,00",
            "operation raw measurements (ms):;22,00;21,00;",
            "operation stats (ms/op):;avg op:;4,16;min op:;4,00;max op:;4,40",
            "operation info:;data length;16;total iterations;25;total invocations;25"
        ]
        result = parse_method_block(lines, DEFAULT_DELIMITER)

        self.assertEqual(result["method name"], "ALG_SHA MessageDigest_doFinal()")
        self.assertEqual(result["data length"], "16")
        self.assertTrue(result["supported"])


class TestJcperfParserConvertToMap(unittest.TestCase):
    """Tests for the main convert_to_map_jcperf function."""

    def test_convert_to_map_jcperf_basic(self):
        """Test basic conversion with simple performance data."""
        groups = [
            # Basic info
            ["Card name; Test Card", "Card ATR; 3b 00 00"],
            # JCSystem group (triggers end of basic info)
            ["JCSystem.getVersion()[Major.Minor];3.0;"],
            # Section header
            ["MESSAGE DIGEST"],
            # Method block
            [
                "method name:; ALG_SHA MessageDigest_doFinal()",
                "measurement config:;appletPrepareINS;34;appletMeasureINS;41",
                "baseline measurements (ms):;27.00;7.00;",
                "baseline stats (ms):;avg:;11.80;min:;7.00;max:;27.00",
                "operation stats (ms/op):;avg op:;1.05;min op:;0.96;max op:;1.38",
                "operation info:;data length;256;total iterations;250;total invocations;250"
            ]
        ]

        result = convert_to_map_jcperf(groups, DEFAULT_DELIMITER)

        self.assertEqual(result["_type"], "javacard-performance")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("MESSAGE DIGEST", result)
        self.assertEqual(len(result["MESSAGE DIGEST"]), 1)
        self.assertEqual(result["MESSAGE DIGEST"][0]["method name"], "ALG_SHA MessageDigest_doFinal()")

    def test_convert_to_map_jcperf_multiple_sections(self):
        """Test conversion with multiple sections."""
        groups = [
            ["Card name; Test Card"],
            ["JCSystem.getVersion()[Major.Minor];3.0;"],
            ["MESSAGE DIGEST"],
            ["method name:; ALG_SHA MessageDigest_doFinal()", "NO_SUCH_ALGORITHM"],
            ["MESSAGE DIGEST - END"],
            ["RANDOM GENERATOR"],
            ["method name:; ALG_PSEUDO_RANDOM RandomData_generateData()", "NO_SUCH_ALGORITHM"]
        ]

        result = convert_to_map_jcperf(groups, DEFAULT_DELIMITER)

        self.assertIn("MESSAGE DIGEST", result)
        self.assertIn("RANDOM GENERATOR", result)

    def test_convert_to_map_jcperf_variable_sections(self):
        """Test conversion with variable format sections."""
        groups = [
            ["Card name; Test Card"],
            ["JCSystem.getVersion()[Major.Minor];3.0;"],
            ["MESSAGE DIGEST"],
            ["MESSAGE DIGEST - ALG_SHA - variable data - BEGIN"],
            [
                "method name:; ALG_SHA MessageDigest_doFinal();16;",
                "measurement config:;appletPrepareINS;34",
                "baseline measurements (ms):;103,00;",
                "baseline stats (ms):;avg:;105,00;min:;101,00;max:;115,00",
                "operation stats (ms/op):;avg op:;4,16;min op:;4,00;max op:;4,40",
                "operation info:;data length;16;total iterations;25;total invocations;25"
            ],
            ["MESSAGE DIGEST - ALG_SHA - variable data - END"]
        ]

        result = convert_to_map_jcperf(groups, DEFAULT_DELIMITER)

        self.assertIn("MESSAGE DIGEST - ALG_SHA", result)
        self.assertEqual(result["MESSAGE DIGEST - ALG_SHA"][0]["data length"], "16")


if __name__ == '__main__':
    unittest.main()

