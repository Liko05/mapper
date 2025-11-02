import unittest
import os
import tempfile
from main import prepare_lines, create_attribute, parse_group, convert_to_map, BASIC_INFO, END_OF_BASIC_INFO, load_exclusions, apply_exclusions

DEFAULT_DELIMITER = ";"


class TestUnitParser(unittest.TestCase):

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

    def test_prepare_lines_empty_input(self):
        self.assertEqual(prepare_lines([]), [])
        self.assertEqual(prepare_lines([""]), [])
        self.assertEqual(prepare_lines(["", "", ""]), [])

    def test_prepare_lines_no_empty_lines(self):
        lines = ["line1", "line2", "line3"]
        expected = [["line1", "line2", "line3"]]
        self.assertEqual(prepare_lines(lines), expected)

    def test_prepare_lines_whitespace_only(self):
        lines = [
            "line1",
            "   ",
            "line2",
            "\t",
            "line3"
        ]
        expected = [["line1"], ["line2"], ["line3"]]
        self.assertEqual(prepare_lines(lines), expected)

    def test_create_attribute(self):
        attr = create_attribute("foo", "bar")
        self.assertEqual(attr, {"name": "foo", "value": "bar"})

    def test_create_attribute_with_special_chars(self):
        attr = create_attribute("foo@bar", "value#123")
        self.assertEqual(attr, {"name": "foo@bar", "value": "value#123"})

        attr = create_attribute("", "")
        self.assertEqual(attr, {"name": "", "value": ""})

    def test_parse_group_basic_info(self):
        group = [
            "Name;Value",
            f"Something;Else",
            f"{END_OF_BASIC_INFO};1.0"
        ]
        group_name, attributes, finished = parse_group(group, False, DEFAULT_DELIMITER)
        self.assertEqual(group_name, BASIC_INFO)
        self.assertTrue(finished)
        self.assertEqual(attributes, [
            {"name": "Name", "value": "Value"},
            {"name": "Something", "value": "Else"},
            {"name": END_OF_BASIC_INFO, "value": "1.0"}
        ])

    def test_parse_group_after_basic_info(self):
        group = [
            "GroupName",
            "attr1;val1",
            "attr2;val2"
        ]
        group_name, attributes, finished = parse_group(group, True, DEFAULT_DELIMITER)
        self.assertEqual(group_name, "GroupName")
        self.assertEqual(attributes, [
            {"name": "attr1", "value": "val1"},
            {"name": "attr2", "value": "val2"}
        ])
        self.assertTrue(finished)

    def test_parse_group_with_pipe_delimiter(self):
        group = [
            "GroupName",
            "attr1|val1",
            "attr2|val2"
        ]
        group_name, attributes, finished = parse_group(group, True, "|")
        self.assertEqual(group_name, "GroupName")
        self.assertEqual(attributes, [
            {"name": "attr1", "value": "val1"},
            {"name": "attr2", "value": "val2"}
        ])

    def test_parse_group_with_comma_delimiter(self):
        group = [
            "Name,Value",
            f"{END_OF_BASIC_INFO},2.0"
        ]
        group_name, attributes, finished = parse_group(group, False, ",")
        self.assertEqual(group_name, BASIC_INFO)
        self.assertTrue(finished)
        self.assertEqual(attributes, [
            {"name": "Name", "value": "Value"},
            {"name": END_OF_BASIC_INFO, "value": "2.0"}
        ])

    def test_parse_group_with_tab_delimiter(self):
        group = [
            "GroupName",
            "attr1\tval1",
            "attr2\tval2"
        ]
        group_name, attributes, finished = parse_group(group, True, "\t")
        self.assertEqual(group_name, "GroupName")
        self.assertEqual(attributes, [
            {"name": "attr1", "value": "val1"},
            {"name": "attr2", "value": "val2"}
        ])

    def test_parse_group_with_colon_delimiter(self):
        group = [
            "Config:Settings",
            "key1:value1",
            "key2:value2"
        ]
        group_name, attributes, finished = parse_group(group, True, ":")
        self.assertEqual(group_name, "Config")
        self.assertEqual(attributes, [
            {"name": "Config", "value": "Settings"},
            {"name": "key1", "value": "value1"},
            {"name": "key2", "value": "value2"}
        ])

    def test_parse_group_no_delimiter_in_line(self):
        group = [
            "GroupNameOnly",
            "line_without_delimiter",
            "another_line_no_delim"
        ]
        group_name, attributes, finished = parse_group(group, True, ";")
        self.assertEqual(group_name, "GroupNameOnly")
        self.assertEqual(attributes, [])

    def test_parse_group_with_dot_in_name(self):
        group = [
            "com.example.ClassName;value",
            "attr1;val1"
        ]
        group_name, attributes, finished = parse_group(group, True, ";")
        self.assertEqual(group_name, "com")
        self.assertEqual(len(attributes), 2)

    def test_parse_group_empty_group(self):
        group = []
        group_name, attributes, finished = parse_group(group, True, ";")
        self.assertIsNone(group_name)
        self.assertEqual(attributes, [])
        self.assertTrue(finished)

    def test_parse_group_single_line_group(self):
        group = ["SingleLine;WithValue"]
        group_name, attributes, finished = parse_group(group, True, ";")
        self.assertEqual(group_name, "SingleLine")
        self.assertEqual(attributes, [{"name": "SingleLine", "value": "WithValue"}])

    def test_convert_to_map(self):
        groups = [
            ["Name;Value", f"{END_OF_BASIC_INFO};1.0"],
            ["Group1", "a;1", "b;2"],
            ["Group2", "c;3"]
        ]
        result = convert_to_map(groups, DEFAULT_DELIMITER)
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertIn("Group2", result)
        self.assertEqual(result["Group1"], [
            {"name": "a", "value": "1"},
            {"name": "b", "value": "2"}
        ])
        self.assertEqual(result["Group2"], [
            {"name": "c", "value": "3"}
        ])

    def test_convert_to_map_with_pipe_delimiter(self):
        groups = [
            ["Name|Value", f"{END_OF_BASIC_INFO}|2.0"],
            ["Group1", "a|1", "b|2"]
        ]
        result = convert_to_map(groups, "|")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertEqual(result["Group1"], [
            {"name": "a", "value": "1"},
            {"name": "b", "value": "2"}
        ])

    def test_convert_to_map_duplicate_group_names(self):
        groups = [
            ["Name;Value", f"{END_OF_BASIC_INFO};1.0"],
            ["Group1", "a;1"],
            ["Group1", "b;2"],
            ["Group1", "c;3"]
        ]
        result = convert_to_map(groups, ";")
        self.assertIn("Group1", result)
        self.assertEqual(len(result["Group1"]), 3)
        self.assertEqual(result["Group1"], [
            {"name": "a", "value": "1"},
            {"name": "b", "value": "2"},
            {"name": "c", "value": "3"}
        ])

    def test_convert_to_map_empty_groups(self):
        groups = [
            ["Name;Value", f"{END_OF_BASIC_INFO};1.0"],
            [],
            ["Group1", "a;1"],
            [],
        ]
        result = convert_to_map(groups, ";")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertEqual(len(result), 2)

    def test_convert_to_map_single_line_groups(self):
        groups = [
            ["Name;Value", f"{END_OF_BASIC_INFO};1.0"],
            ["x"],
            ["Group1", "a;1"],
        ]
        result = convert_to_map(groups, ";")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertNotIn("x", result)

    def test_convert_to_map_no_basic_info_end(self):
        groups = [
            ["Name;Value", "Another;Thing"],
            ["StillBasic;Info"],
        ]
        result = convert_to_map(groups, ";")
        self.assertIn(BASIC_INFO, result)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[BASIC_INFO]), 3)

    def test_convert_to_map_custom_delimiter_with_spaces(self):
        groups = [
            ["Name :: Value", f"{END_OF_BASIC_INFO} :: 1.0"],
            ["Group1", "a :: 1", "b :: 2"]
        ]
        result = convert_to_map(groups, " :: ")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)

    def test_convert_to_map_delimiter_not_found(self):
        groups = [
            ["NameValue", f"{END_OF_BASIC_INFO}"],
            ["Group1", "a1", "b2"]
        ]
        result = convert_to_map(groups, ";")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertEqual(result["Group1"], [])

    def test_convert_to_map_multichar_delimiter(self):
        groups = [
            ["Name<->Value", f"{END_OF_BASIC_INFO}<->3.0"],
            ["Group1", "attr1<->val1", "attr2<->val2"]
        ]
        result = convert_to_map(groups, "<->")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertEqual(result["Group1"], [
            {"name": "attr1", "value": "val1"},
            {"name": "attr2", "value": "val2"}
        ])

    def test_convert_to_map_special_char_delimiter(self):
        groups = [
            ["Name@Value", f"{END_OF_BASIC_INFO}@1.0"],
            ["Group1", "a@1"]
        ]
        result = convert_to_map(groups, "@")
        self.assertIn("Group1", result)

        groups = [
            ["Name#Value", f"{END_OF_BASIC_INFO}#1.0"],
            ["Group2", "b#2"]
        ]
        result = convert_to_map(groups, "#")
        self.assertIn("Group2", result)

    def test_load_exclusions_basic(self):
        with tempfile.NamedTemporaryFile('w+', delete=False) as f:
            f.write("""
            # a comment line
            
            foo
            bar 
            \tbaz\n
            # another comment
            """.strip())
            path = f.name
        try:
            excluded = load_exclusions(path)
            self.assertEqual(excluded, {"foo", "bar", "baz"})
        finally:
            os.unlink(path)

    def test_load_exclusions_missing_file(self):
        path = os.path.join(tempfile.gettempdir(), "nonexistent_exclusions_123456.txt")
        if os.path.exists(path):
            os.unlink(path)
        excluded = load_exclusions(path)
        self.assertEqual(excluded, set())

    def test_apply_exclusions_filters_attributes(self):
        result = {
            "Group1": [
                {"name": "a", "value": "1"},
                {"name": "b", "value": "2"},
                {"name": "c", "value": "3"},
            ],
            BASIC_INFO: [
                {"name": "x", "value": "y"},
                {"name": "keep", "value": "z"},
            ],
        }
        filtered = apply_exclusions(result, {"a", "x"})
        self.assertEqual([a["name"] for a in filtered["Group1"]], ["b", "c"])
        self.assertEqual([a["name"] for a in filtered[BASIC_INFO]], ["keep"])

    def test_apply_exclusions_noop_when_empty(self):
        result = {
            "Group1": [
                {"name": "a", "value": "1"}
            ]
        }
        filtered = apply_exclusions(result, set())
        self.assertIs(filtered, result)


if __name__ == "__main__":
    unittest.main()
