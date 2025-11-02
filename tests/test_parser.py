"""
Deprecated. Tests have been split into:
- tests/test_unit_parser.py
- tests/test_integration_parser.py
"""

import unittest

class DeprecatedTestSuite(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()