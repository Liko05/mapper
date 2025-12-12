import unittest
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List

from main import process_files


class TestIntegrationParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Enable INFO logs during integration tests
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')

    def setUp(self):
        # Temporary workspace for copying test data and writing outputs
        self.tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmpdir_obj.name)

        self.repo_root = Path(__file__).resolve().parents[1]
        self.test_data_dir = self.repo_root / 'tests' / 'test-data'
        self.assertTrue(self.test_data_dir.exists(), f"Missing test-data at {self.test_data_dir}")

        # Collect CSV input files
        all_csvs: List[Path] = list(self.test_data_dir.rglob('*.csv'))
        self.assertGreater(len(all_csvs), 0, "No CSV files found in test-data/")

        # Copy to temp dir preserving relative structure to avoid name collisions
        self.inputs: List[Path] = []
        for src in all_csvs:
            rel = src.relative_to(self.test_data_dir)
            dst = self.tmpdir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            self.inputs.append(dst)

    def tearDown(self):
        self.tmpdir_obj.cleanup()

    def test_process_files_writes_json_outputs(self):
        outputs = process_files([str(p) for p in self.inputs], delimiter=';')

        # Assert outputs created for each input
        self.assertEqual(len(outputs), len(self.inputs))
        for out in outputs:
            self.assertTrue(out.exists(), f"Output missing: {out}")
            self.assertEqual(out.suffix, '.json')

        # Sanity-check contents of one output file
        sample_out = outputs[0]
        content = sample_out.read_text(encoding='utf-8')
        import json
        data = json.loads(content)
        self.assertIsInstance(data, dict)
        # Check that _type exists
        self.assertIn('_type', data)
        # Basic information should be a list of name/value dicts
        if 'Basic information' in data:
            for item in data['Basic information']:
                self.assertIsInstance(item, dict)
                self.assertIn('name', item)
                self.assertIn('value', item)


if __name__ == '__main__':
    unittest.main()
