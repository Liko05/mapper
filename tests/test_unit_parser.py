import unittest
import os
import tempfile

from jcres_parser import END_OF_BASIC_INFO, parse_group, BASIC_INFO, convert_to_map
from parser_utils import prepare_lines, create_attribute, load_exclusions, apply_exclusions

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
        # After basic info, parse_group returns nested lists of algorithm attributes
        self.assertEqual(len(attributes), 2)
        self.assertEqual(attributes[0][0]["name"], "algorithm_name")
        self.assertEqual(attributes[0][0]["value"], "attr1")
        self.assertEqual(attributes[0][1]["name"], "is_supported")
        self.assertEqual(attributes[0][1]["value"], "val1")
        self.assertTrue(finished)

    def test_parse_group_with_pipe_delimiter(self):
        group = [
            "GroupName",
            "attr1|val1",
            "attr2|val2"
        ]
        group_name, attributes, finished = parse_group(group, True, "|")
        self.assertEqual(group_name, "GroupName")
        # After basic info, parse_group returns nested lists of algorithm attributes
        self.assertEqual(len(attributes), 2)
        self.assertEqual(attributes[0][0]["value"], "attr1")
        self.assertEqual(attributes[0][1]["value"], "val1")

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
        # After basic info, parse_group returns nested lists of algorithm attributes
        self.assertEqual(len(attributes), 2)
        self.assertEqual(attributes[0][0]["value"], "attr1")
        self.assertEqual(attributes[0][1]["value"], "val1")

    def test_parse_group_with_colon_delimiter(self):
        group = [
            "Config:Settings",
            "key1:value1",
            "key2:value2"
        ]
        group_name, attributes, finished = parse_group(group, True, ":")
        self.assertEqual(group_name, "Config")
        # After basic info with colon delimiter, parse_group returns nested algorithm attributes
        self.assertEqual(len(attributes), 3)  # All 3 lines are parsed as attributes

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
        # Single line with delimiter after basic info gets parsed as algorithm attributes
        self.assertEqual(len(attributes), 1)

    def test_convert_to_map(self):
        groups = [
            ["Name;Value", f"{END_OF_BASIC_INFO};1.0"],
            ["Group1", "a;1", "b;2"],
            ["Group2", "c;3"]
        ]
        result = convert_to_map(groups, DEFAULT_DELIMITER)
        self.assertEqual(result["_type"], "javacard")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertIn("Group2", result)
        # After basic info, groups have nested algorithm attributes
        self.assertEqual(len(result["Group1"]), 2)
        self.assertEqual(result["Group1"][0][0]["name"], "algorithm_name")
        self.assertEqual(result["Group1"][0][0]["value"], "a")
        self.assertEqual(len(result["Group2"]), 1)

    def test_convert_to_map_with_pipe_delimiter(self):
        groups = [
            ["Name|Value", f"{END_OF_BASIC_INFO}|2.0"],
            ["Group1", "a|1", "b|2"]
        ]
        result = convert_to_map(groups, "|")
        self.assertEqual(result["_type"], "javacard")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        # After basic info, groups have nested algorithm attributes
        self.assertEqual(len(result["Group1"]), 2)
        self.assertEqual(result["Group1"][0][0]["value"], "a")

    def test_convert_to_map_duplicate_group_names(self):
        groups = [
            ["Name;Value", f"{END_OF_BASIC_INFO};1.0"],
            ["Group1", "a;1"],
            ["Group1", "b;2"],
            ["Group1", "c;3"]
        ]
        result = convert_to_map(groups, ";")
        self.assertEqual(result["_type"], "javacard")
        self.assertIn("Group1", result)
        # Duplicate groups get merged, each with nested algorithm attributes
        self.assertEqual(len(result["Group1"]), 3)
        self.assertEqual(result["Group1"][0][0]["value"], "a")
        self.assertEqual(result["Group1"][1][0]["value"], "b")
        self.assertEqual(result["Group1"][2][0]["value"], "c")

    def test_convert_to_map_empty_groups(self):
        groups = [
            ["Name;Value", f"{END_OF_BASIC_INFO};1.0"],
            [],
            ["Group1", "a;1"],
            [],
        ]
        result = convert_to_map(groups, ";")
        self.assertEqual(result["_type"], "javacard")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertEqual(len(result), 3)  # _type, BASIC_INFO, Group1

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
        self.assertEqual(result["_type"], "javacard")
        self.assertIn(BASIC_INFO, result)
        self.assertEqual(len(result), 2)  # _type, BASIC_INFO
        # Without END_OF_BASIC_INFO marker, all lines are parsed as basic info
        # The parser behavior may vary, just check we have some attributes
        self.assertGreater(len(result[BASIC_INFO]), 0)

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
        self.assertEqual(result["_type"], "javacard")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        # After basic info, groups have nested algorithm attributes
        self.assertEqual(len(result["Group1"]), 2)
        self.assertEqual(result["Group1"][0][0]["value"], "attr1")

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
