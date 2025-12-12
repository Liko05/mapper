"""
Unit tests for main.py parser detection and processing logic.
"""
import unittest
import tempfile
import os
import json
from pathlib import Path
from main import detect_parser_type, process_files, process_folder


class TestDetectParserType(unittest.TestCase):
    """Tests for parser type detection logic."""

    def test_detect_tpm_parser(self):
        """Test detection of TPM files."""
        self.assertEqual(detect_parser_type("path/to/tpm/file.csv"), "tpm")
        self.assertEqual(detect_parser_type("path/to/TPM/file.csv"), "tpm")
        self.assertEqual(detect_parser_type("/tpm/profiles/performance/test.csv"), "tpm")

    def test_detect_javacard_aid_parser(self):
        """Test detection of JavaCard AID files."""
        self.assertEqual(detect_parser_type("path/to/aid/file.csv"), "javacard-aid")
        self.assertEqual(detect_parser_type("path/to/Profiles/aid/test.csv"), "javacard-aid")
        self.assertEqual(detect_parser_type("Card_AIDSUPPORT_3B00.csv"), "javacard-aid")
        self.assertEqual(detect_parser_type("test_aidsupport_file.csv"), "javacard-aid")

    def test_detect_javacard_performance_parser(self):
        """Test detection of JavaCard performance files."""
        self.assertEqual(detect_parser_type("path/to/performance/file.csv"), "javacard-performance")
        self.assertEqual(detect_parser_type("path/to/PERFORMANCE/file.csv"), "javacard-performance")
        self.assertEqual(detect_parser_type("/Profiles/performance/fixed/test.csv"), "javacard-performance")
        self.assertEqual(detect_parser_type("/Profiles/performance/variable/test.csv"), "javacard-performance")

    def test_detect_javacard_algsupport_parser(self):
        """Test detection of default JavaCard algorithm support files."""
        self.assertEqual(detect_parser_type("path/to/results/file.csv"), "javacard-algsupport")
        self.assertEqual(detect_parser_type("Card_ALGSUPPORT_3B00.csv"), "javacard-algsupport")
        self.assertEqual(detect_parser_type("some_random_file.csv"), "javacard-algsupport")

    def test_detect_parser_priority(self):
        """Test that detection priority is correct (aid before performance)."""
        # AID should be detected before performance if both are in path
        self.assertEqual(
            detect_parser_type("performance/aid/file.csv"),
            "javacard-aid"
        )

        # TPM should be detected first
        self.assertEqual(
            detect_parser_type("tpm/performance/file.csv"),
            "tpm"
        )


class TestProcessFiles(unittest.TestCase):
    """Tests for the process_files function."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_process_tpm_file(self):
        """Test processing of a simple TPM file."""
        csv_content = """Manufacturer; INTC
Firmware version; 11.0.0.1202

TPM2_Create

Key parameters:;RSA 1024
operation stats (ms/op):;avg op:;100.00;min op:;90.00;max op:;110.00
operation info:;total iterations:;100;successful:;100;failed:;0;error:;None
"""
        csv_path = os.path.join(self.temp_dir, "tpm_test.csv")
        with open(csv_path, "w") as f:
            f.write(csv_content)

        outputs = process_files([csv_path])

        self.assertEqual(len(outputs), 1)
        json_path = outputs[0]
        self.assertTrue(json_path.exists())

        with open(json_path) as f:
            result = json.load(f)

        self.assertEqual(result["_type"], "tpm")
        self.assertIn("TPM2_Create", result)

    def test_process_aid_file(self):
        """Test processing of a simple AID file."""
        csv_content = """jcAIDScan version; 0.1.1
Card ATR; 3BFC1800
Card name; Test Card

***** KEY INFO

VER;255 ID;1 TYPE;DES3 LEN;16

PACKAGE AID; MAJOR VERSION; MINOR VERSION; PACKAGE NAME; INTRODUCING JC API VERSION;
a0000000620001; 1; 0; java.lang; 2.1

FULL PACKAGE AID; IS SUPPORTED?; PACKAGE NAME WITH VERSION;
000107A0000000620001; yes; java.lang v1.0;
"""
        csv_path = os.path.join(self.temp_dir, "aid", "test_AIDSUPPORT.csv")
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "w") as f:
            f.write(csv_content)

        outputs = process_files([csv_path])

        self.assertEqual(len(outputs), 1)

        with open(outputs[0]) as f:
            result = json.load(f)

        self.assertEqual(result["_type"], "javacard-aid")
        self.assertIn("Package AID", result)

    def test_process_nonexistent_file(self):
        """Test handling of non-existent file."""
        outputs = process_files(["/nonexistent/path/file.csv"])
        self.assertEqual(len(outputs), 0)

    def test_process_multiple_files(self):
        """Test processing of multiple files."""
        # Create two test files
        csv1_path = os.path.join(self.temp_dir, "tpm_test.csv")
        csv2_path = os.path.join(self.temp_dir, "aid", "aid_test.csv")
        os.makedirs(os.path.dirname(csv2_path), exist_ok=True)

        with open(csv1_path, "w") as f:
            f.write("Manufacturer; INTC\n")

        with open(csv2_path, "w") as f:
            f.write("jcAIDScan version; 0.1.1\n")

        outputs = process_files([csv1_path, csv2_path])

        self.assertEqual(len(outputs), 2)


class TestProcessFolder(unittest.TestCase):
    """Tests for the process_folder function."""

    def setUp(self):
        """Create temporary directories for test files."""
        import shutil
        self.source_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.source_dir, ignore_errors=True)
        shutil.rmtree(self.output_dir, ignore_errors=True)

    def test_process_folder_creates_mirrored_structure(self):
        """Test that folder processing creates mirrored directory structure."""
        # Create source structure
        tpm_dir = os.path.join(self.source_dir, "tpm", "performance")
        jc_dir = os.path.join(self.source_dir, "javacard", "results")
        os.makedirs(tpm_dir)
        os.makedirs(jc_dir)

        # Create test CSV files
        with open(os.path.join(tpm_dir, "test_tpm.csv"), "w") as f:
            f.write("Manufacturer; INTC\n")
        with open(os.path.join(jc_dir, "test_jc.csv"), "w") as f:
            f.write("Card name; Test\n")

        outputs = process_folder(self.source_dir, self.output_dir)

        self.assertEqual(len(outputs), 2)

        # Check that output files exist in mirrored structure
        expected_tpm = Path(self.output_dir) / "tpm" / "performance" / "test_tpm.json"
        expected_jc = Path(self.output_dir) / "javacard" / "results" / "test_jc.json"

        self.assertTrue(expected_tpm.exists(), f"Expected {expected_tpm} to exist")
        self.assertTrue(expected_jc.exists(), f"Expected {expected_jc} to exist")

    def test_process_folder_empty_folder(self):
        """Test handling of empty folder."""
        outputs = process_folder(self.source_dir, self.output_dir)
        self.assertEqual(len(outputs), 0)

    def test_process_folder_nonexistent(self):
        """Test handling of non-existent folder."""
        outputs = process_folder("/nonexistent/folder", self.output_dir)
        self.assertEqual(len(outputs), 0)

    def test_process_folder_default_output(self):
        """Test that default output folder is created correctly."""
        # Create a CSV file
        os.makedirs(os.path.join(self.source_dir, "subdir"))
        with open(os.path.join(self.source_dir, "subdir", "test.csv"), "w") as f:
            f.write("Card name; Test\n")

        # Save current directory and change to output dir
        original_cwd = os.getcwd()
        os.chdir(self.output_dir)

        try:
            # Process without specifying output folder
            outputs = process_folder(self.source_dir)

            self.assertEqual(len(outputs), 1)

            # Check default output folder name
            source_name = os.path.basename(self.source_dir)
            expected_output_dir = Path(self.output_dir) / f"{source_name}_parsed"
            self.assertTrue(expected_output_dir.exists())
        finally:
            os.chdir(original_cwd)

    def test_process_folder_filters_csv_only(self):
        """Test that only CSV files are processed."""
        # Create various files
        with open(os.path.join(self.source_dir, "test.csv"), "w") as f:
            f.write("Card name; Test\n")
        with open(os.path.join(self.source_dir, "test.txt"), "w") as f:
            f.write("Not a CSV\n")
        with open(os.path.join(self.source_dir, "test.json"), "w") as f:
            f.write("{}\n")

        outputs = process_folder(self.source_dir, self.output_dir)

        # Only the CSV should be processed
        self.assertEqual(len(outputs), 1)
        self.assertTrue(outputs[0].name.endswith(".json"))


if __name__ == '__main__':
    unittest.main()
