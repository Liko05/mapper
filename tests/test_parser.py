import json
import unittest
from main import prepare_lines, create_attribute, parse_group, convert_to_map, BASIC_INFO, END_OF_BASIC_INFO, load_file


class TestParser(unittest.TestCase):

    def test_infineon_example_csv(self):
        test_file_path = "tests/test-data/infineon-example.csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups)

        self.assertIn(BASIC_INFO, result)

        with open("infineon_test_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_prepare_lines(self):
        lines = [
            "line1",
            "line2",
            "",
            "line3",
            "",
            "",
            "line4"
        ]
        expected = [
            ["line1", "line2"],
            ["line3"],
            ["line4"]
        ]
        self.assertEqual(prepare_lines(lines), expected)

    def test_create_attribute(self):
        attr = create_attribute("foo", "bar")
        self.assertEqual(attr, {"name": "foo", "c2": "bar"})

    def test_parse_group_basic_info(self):
        group = [
            "Name;Value",
            f"Something;Else",
            f"{END_OF_BASIC_INFO};1.0"
        ]
        group_name, attributes, finished = parse_group(group, False)
        self.assertEqual(group_name, BASIC_INFO)
        self.assertTrue(finished)
        self.assertEqual(attributes, [
            {"name": "Name", "c2": "Value"},
            {"name": "Something", "c2": "Else"},
            {"name": END_OF_BASIC_INFO, "c2": "1.0"}
        ])

    def test_parse_group_after_basic_info(self):
        group = [
            "GroupName",
            "attr1;val1",
            "attr2;val2"
        ]
        group_name, attributes, finished = parse_group(group, True)
        self.assertEqual(group_name, "GroupName")
        self.assertEqual(attributes, [
            {"name": "attr1", "c2": "val1"},
            {"name": "attr2", "c2": "val2"}
        ])
        self.assertTrue(finished)

    def test_convert_to_map(self):
        groups = [
            ["Name;Value", f"{END_OF_BASIC_INFO};1.0"],
            ["Group1", "a;1", "b;2"],
            ["Group2", "c;3"]
        ]
        result = convert_to_map(groups)
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertIn("Group2", result)
        self.assertEqual(result["Group1"], [
            {"name": "a", "c2": "1"},
            {"name": "b", "c2": "2"}
        ])
        self.assertEqual(result["Group2"], [
            {"name": "c", "c2": "3"}
        ])

if __name__ == "__main__":
    unittest.main()