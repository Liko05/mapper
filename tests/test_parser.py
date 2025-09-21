import json
import unittest
from main import prepare_lines, create_attribute, parse_group, convert_to_map, BASIC_INFO, END_OF_BASIC_INFO, load_file

DEFAULT_DELIMITER = ";"


class TestParser(unittest.TestCase):

    def test_real_data_one(self):
        """Test parsing the provided Infineon results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Infineon_CJTOP_80K_INF_SLJ_52GLA080AL_M8.4_ICFabDate_2012_001_ALGSUPPORT__3b_fe_18_00_00_80_31_fe_45_80_31_80_66_40_90_a5_10_2e_10_83_01_90_00_f2_(provided_by_PetrS).csv
        """
        test_file_path = "tests/test-data/infineon/Infineon_CJTOP_80K_INF_SLJ_52GLA080AL_M8.4_ICFabDate_2012_001_ALGSUPPORT__3b_fe_18_00_00_80_31_fe_45_80_31_80_66_40_90_a5_10_2e_10_83_01_90_00_f2_(provided_by_PetrS).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("one_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_two(self):
        """Test parsing the provided Infineon results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Infineon_JTOPV2_16K_3B%206D%2000%2000%2080%2031%2080%2065%2040%2090%2086%2001%2051%2083%2007%2090%2000_(provided_by_PetrS).csv
        """
        test_file_path = "tests/test-data/infineon/Infineon_JTOPV2_16K_3B 6D 00 00 80 31 80 65 40 90 86 01 51 83 07 90 00_(provided_by_PetrS).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("two_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_three(self):
        """Test parsing the provided Infineon results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Infineon_SECORA_ID_S_(SCP02_with_RSA2k_JC305_GP230_NOT_FOR_SALE_-_PROTOTYPE_ONLY)_ALGSUPPORT__3b_b8_97_00_c0_08_31_fe_45_ff_ff_13_57_30_50_23_00_6a_(provided_by_Thoth).csv
        """
        test_file_path = "tests/test-data/infineon/Infineon_SECORA_ID_S_(SCP02_with_RSA2k_JC305_GP230_NOT_FOR_SALE_-_PROTOTYPE_ONLY)_ALGSUPPORT__3b_b8_97_00_c0_08_31_fe_45_ff_ff_13_57_30_50_23_00_6a_(provided_by_Thoth).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("three_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_four(self):
        """Test parsing the provided Infineon results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Infineon_SECORA_ID_X_ALGSUPPORT__3b_b8_97_00_c0_08_31_fe_45_ff_ff_13_58_30_50_23_00_65_(provided_by_Thoth).csv
        """
        test_file_path = "tests/test-data/infineon/Infineon_SECORA_ID_X_ALGSUPPORT__3b_b8_97_00_c0_08_31_fe_45_ff_ff_13_58_30_50_23_00_65_(provided_by_Thoth).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("four_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_five(self):
        """Test parsing the provided Infineon results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Infineon_SECORA_ID_X_Batch_16072021_SALES_ALGSUPPORT__3b_88_80_01_00_00_00_11_77_81_c3_00_2d_(provided_by_Thoth).csv
        """
        test_file_path = "tests/test-data/infineon/Infineon_SECORA_ID_X_Batch_16072021_SALES_ALGSUPPORT__3b_88_80_01_00_00_00_11_77_81_c3_00_2d_(provided_by_Thoth).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("five_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_six(self):
        """Test parsing the provided NXP results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/NXP_JCOP_J2A080_3b%20f6%2018%2000%20ff%2081%2031%20fe%2045%204a%2032%2041%2030%2038%2030%201b_(provided_by_Pierre-d).csv
        """
        test_file_path = "tests/test-data/nxp/NXP_JCOP_J2A080_3b f6 18 00 ff 81 31 fe 45 4a 32 41 30 38 30 1b_(provided_by_Pierre-d).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("six_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_seven(self):
        """Test parsing the provided NXP results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/NXP_JCOP_J2A080_80K_ICFabDate_2011_070_ALGSUPPORT__3b_f8_18_00_00_81_31_fe_45_4a_43_4f_50_76_32_34_31_bc__(provided_by_PetrS).csv
        """
        test_file_path = "tests/test-data/nxp/NXP_JCOP_J2A080_80K_ICFabDate_2011_070_ALGSUPPORT__3b_f8_18_00_00_81_31_fe_45_4a_43_4f_50_76_32_34_31_bc__(provided_by_PetrS).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("seven_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_eight(self):
        """Test parsing the provided NXP results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/NXP_JCOP_J2A080_ICFabDate_2018_ALGSUPPORT__3b_f9_13_00_00_81_31_fe_45_4a_43_4f_50_76_32_34_31_b7_01_(provided_by_Toporin).csv
        """
        test_file_path = "tests/test-data/nxp/NXP_JCOP_J2A080_ICFabDate_2018_ALGSUPPORT__3b_f9_13_00_00_81_31_fe_45_4a_43_4f_50_76_32_34_31_b7_01_(provided_by_Toporin).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("eight_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_nine(self):
        """Test parsing the provided NXP results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/NXP_JCOP_J2D081_80K_ICFabDate_2014_126_ALGSUPPORT__3b_f9_18_00_00_81_31_fe_45_4a_32_44_30_38_31_5f_50_56_b6_(provided_by_PetrS_and_Paul_Crocker).csv
        """
        test_file_path = "tests/test-data/nxp/NXP_JCOP_J2D081_80K_ICFabDate_2014_126_ALGSUPPORT__3b_f9_18_00_00_81_31_fe_45_4a_32_44_30_38_31_5f_50_56_b6_(provided_by_PetrS_and_Paul_Crocker).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("nine_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_ten(self):
        """Test parsing the provided NXP results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/NXP_JCOP_J2D081_ICFabDate_2017_ALGSUPPORT__3b_f9_18_00_00_81_31_fe_45_4a_32_44_30_38_31_5f_50_56_b6_(provided_by_Toporin).csv
        """
        test_file_path = "tests/test-data/nxp/NXP_JCOP_J2D081_ICFabDate_2017_ALGSUPPORT__3b_f9_18_00_00_81_31_fe_45_4a_32_44_30_38_31_5f_50_56_b6_(provided_by_Toporin).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("ten_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_eleven(self):
        """Test parsing the provided FeiTian results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/FeiTian_Ltd_JavaCard_Token_V1.0_0_ALGSUPPORT__3b_fc_18_00_00_81_31_80_45_90_67_46_4a_01_01_68_06_00_00_00_00_04_(provided_by_Thoth_Tay).csv.csv
        """
        test_file_path = "tests/test-data/feitian/FeiTian_Ltd_JavaCard_Token_V1.0_0_ALGSUPPORT__3b_fc_18_00_00_81_31_80_45_90_67_46_4a_01_01_68_06_00_00_00_00_04_(provided_by_Thoth_Tay).csv.csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("eleven_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_twelve(self):
        """Test parsing the provided FeiTian results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Feitian-FTJCOS_ICFabDate_2018_ALGSUPPORT__3b_fc_18_00_00_81_31_80_45_90_67_46_4a_01_00_87_06_00_00_00_00_ea_(provided_by_Toporin).csv
        """
        test_file_path = "tests/test-data/feitian/Feitian-FTJCOS_ICFabDate_2018_ALGSUPPORT__3b_fc_18_00_00_81_31_80_45_90_67_46_4a_01_00_87_06_00_00_00_00_ea_(provided_by_Toporin).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("twelve_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_thirteen(self):
        """Test parsing the provided FeiTian results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Feitian_A40CR_ICFabDate_2018_ALGSUPPORT__3b_9c_95_80_81_1f_03_90_67_46_4a_01_00_41_06_f2_72_7e_00_57.csv
        """
        test_file_path = "tests/test-data/feitian/Feitian_A40CR_ICFabDate_2018_ALGSUPPORT__3b_9c_95_80_81_1f_03_90_67_46_4a_01_00_41_06_f2_72_7e_00_57.csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("thirteen_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_fourteen(self):
        """Test parsing the provided FeiTian results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Feitian_A40_ICFabDate_2018_ALGSUPPORT__3b_9f_95_81_31_fe_9f_00_66_46_53_05_10_00_ff_71_df_00_00_00_00_00_ec__(provided_by_Radboud_University).csv
        """
        test_file_path = "tests/test-data/feitian/Feitian_A40_ICFabDate_2018_ALGSUPPORT__3b_9f_95_81_31_fe_9f_00_66_46_53_05_10_00_ff_71_df_00_00_00_00_00_ec__(provided_by_Radboud_University).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("fourteen_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_fifteen(self):
        """Test parsing the provided FeiTian results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Feitian_C21C_Samsung_S3FS91J_ALGSUPPORT__3b_fc_18_00_00_81_31_80_45_90_67_46_4a_01_00_05_24_c0_72_7e_00_86_(provided_by_Thotheolh_Tay).csv
        """
        test_file_path = "tests/test-data/feitian/Feitian_C21C_Samsung_S3FS91J_ALGSUPPORT__3b_fc_18_00_00_81_31_80_45_90_67_46_4a_01_00_05_24_c0_72_7e_00_86_(provided_by_Thotheolh_Tay).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("fifteen_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_sixteen(self):
        """Test parsing the provided gemplus results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Gemplus_GXPE64PK_TOP_IM_GX3_3B%207E%2094%2000%2000%2080%2025%20A0%2000%2000%2000%2028%2056%2080%2010%2021%2000%2001%2008_(provided_by_PetrS).csv
        """
        test_file_path = "tests/test-data/gemplus/Gemplus_GXPE64PK_TOP_IM_GX3_3B 7E 94 00 00 80 25 A0 00 00 00 28 56 80 10 21 00 01 08_(provided_by_PetrS).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("sixteen_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_seventeen(self):
        """Test parsing the provided gemplus results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Gemplus_GXPLiteGeneric_3B%207D%2094%2000%2000%2080%2031%2080%2065%20B0%2083%2001%2002%2090%2083%2000%2090%2000_(provided_by_PetrS).csv
        """
        test_file_path = "tests/test-data/gemplus/Gemplus_GXPLiteGeneric_3B 7D 94 00 00 80 31 80 65 B0 83 01 02 90 83 00 90 00_(provided_by_PetrS).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("seventeen_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_eighteen(self):
        """Test parsing the provided gemplus results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Gemplus_GXPR3_3B%207B%2094%2000%2000%2080%2065%20B0%2083%2001%2001%2074%2083%2000%2090%2000_(provided_by_PetrS).csv
        """
        test_file_path = "tests/test-data/gemplus/Gemplus_GXPR3_3B 7B 94 00 00 80 65 B0 83 01 01 74 83 00 90 00_(provided_by_PetrS).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("eighteen_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_nineteen(self):
        """Test parsing the provided gemplus results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Gemplus_GXPR3r32_TOP_IS_GX3_3B%207D%2094%2000%2000%2080%2031%2080%2065%20B0%2083%2001%2002%2090%2083%2000%2090%2000_(provided_by_PetrS).csv
        """
        test_file_path = "tests/test-data/gemplus/Gemplus_GXPR3r32_TOP_IS_GX3_3B 7D 94 00 00 80 31 80 65 B0 83 01 02 90 83 00 90 00_(provided_by_PetrS).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("nineteen_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_real_data_twenty(self):
        """Test parsing the provided gemplus results CSV file
        Link: https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/Gemplus_GXP_R4_72K_ICFabDate_2007_291_ALGSUPPORT__3b_7d_94_00_00_80_31_80_65_b0_83_11_c0_a9_83_00_90_00_(provided_by_PetrS).csv
        """
        test_file_path = "tests/test-data/gemplus/Gemplus_GXP_R4_72K_ICFabDate_2007_291_ALGSUPPORT__3b_7d_94_00_00_80_31_80_65_b0_83_11_c0_a9_83_00_90_00_(provided_by_PetrS).csv"

        groups = load_file(test_file_path)
        result = convert_to_map(groups, DEFAULT_DELIMITER)

        self.assertIn(BASIC_INFO, result)

        with open("twenty_result.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def test_prepare_lines(self):
        """Test splitting lines into groups based on empty lines"""
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
        """Test with completely empty input"""
        self.assertEqual(prepare_lines([]), [])
        self.assertEqual(prepare_lines([""]), [])
        self.assertEqual(prepare_lines(["", "", ""]), [])

    def test_prepare_lines_no_empty_lines(self):
        """Test when there are no empty lines to split on"""
        lines = ["line1", "line2", "line3"]
        expected = [["line1", "line2", "line3"]]
        self.assertEqual(prepare_lines(lines), expected)

    def test_prepare_lines_whitespace_only(self):
        """Test with lines containing only whitespace"""
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
        self.assertEqual(attr, {"name": "foo", "c2": "bar"})

    def test_create_attribute_with_special_chars(self):
        """Test attribute creation with special characters"""
        attr = create_attribute("foo@bar", "value#123")
        self.assertEqual(attr, {"name": "foo@bar", "c2": "value#123"})

        attr = create_attribute("", "")
        self.assertEqual(attr, {"name": "", "c2": ""})

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
        group_name, attributes, finished = parse_group(group, True, DEFAULT_DELIMITER)
        self.assertEqual(group_name, "GroupName")
        self.assertEqual(attributes, [
            {"name": "attr1", "c2": "val1"},
            {"name": "attr2", "c2": "val2"}
        ])
        self.assertTrue(finished)

    def test_parse_group_with_pipe_delimiter(self):
        """Test parsing with pipe delimiter"""
        group = [
            "GroupName",
            "attr1|val1",
            "attr2|val2"
        ]
        group_name, attributes, finished = parse_group(group, True, "|")
        self.assertEqual(group_name, "GroupName")
        self.assertEqual(attributes, [
            {"name": "attr1", "c2": "val1"},
            {"name": "attr2", "c2": "val2"}
        ])

    def test_parse_group_with_comma_delimiter(self):
        """Test parsing with comma delimiter"""
        group = [
            "Name,Value",
            f"{END_OF_BASIC_INFO},2.0"
        ]
        group_name, attributes, finished = parse_group(group, False, ",")
        self.assertEqual(group_name, BASIC_INFO)
        self.assertTrue(finished)
        self.assertEqual(attributes, [
            {"name": "Name", "c2": "Value"},
            {"name": END_OF_BASIC_INFO, "c2": "2.0"}
        ])

    def test_parse_group_with_tab_delimiter(self):
        """Test parsing with tab delimiter"""
        group = [
            "GroupName",
            "attr1\tval1",
            "attr2\tval2"
        ]
        group_name, attributes, finished = parse_group(group, True, "\t")
        self.assertEqual(group_name, "GroupName")
        self.assertEqual(attributes, [
            {"name": "attr1", "c2": "val1"},
            {"name": "attr2", "c2": "val2"}
        ])

    def test_parse_group_with_colon_delimiter(self):
        """Test parsing with colon delimiter"""
        group = [
            "Config:Settings",
            "key1:value1",
            "key2:value2"
        ]
        group_name, attributes, finished = parse_group(group, True, ":")
        self.assertEqual(group_name, "Config")
        self.assertEqual(attributes, [
            {"name": "Config", "c2": "Settings"},
            {"name": "key1", "c2": "value1"},
            {"name": "key2", "c2": "value2"}
        ])

    def test_parse_group_no_delimiter_in_line(self):
        """Test parsing when lines don't contain the delimiter"""
        group = [
            "GroupNameOnly",
            "line_without_delimiter",
            "another_line_no_delim"
        ]
        group_name, attributes, finished = parse_group(group, True, ";")
        self.assertEqual(group_name, "GroupNameOnly")
        self.assertEqual(attributes, [])


    def test_parse_group_with_dot_in_name(self):
        """Test parsing when group name contains dots"""
        group = [
            "com.example.ClassName;value",
            "attr1;val1"
        ]
        group_name, attributes, finished = parse_group(group, True, ";")
        self.assertEqual(group_name, "com")
        self.assertEqual(len(attributes), 2)

    def test_parse_group_empty_group(self):
        """Test parsing an empty group"""
        group = []
        group_name, attributes, finished = parse_group(group, True, ";")
        self.assertIsNone(group_name)
        self.assertEqual(attributes, [])
        self.assertTrue(finished)

    def test_parse_group_single_line_group(self):
        """Test parsing a group with only one line"""
        group = ["SingleLine;WithValue"]
        group_name, attributes, finished = parse_group(group, True, ";")
        self.assertEqual(group_name, "SingleLine")
        self.assertEqual(attributes, [{"name": "SingleLine", "c2": "WithValue"}])

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
            {"name": "a", "c2": "1"},
            {"name": "b", "c2": "2"}
        ])
        self.assertEqual(result["Group2"], [
            {"name": "c", "c2": "3"}
        ])

    def test_convert_to_map_with_pipe_delimiter(self):
        """Test convert_to_map with pipe delimiter"""
        groups = [
            ["Name|Value", f"{END_OF_BASIC_INFO}|2.0"],
            ["Group1", "a|1", "b|2"]
        ]
        result = convert_to_map(groups, "|")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertEqual(result["Group1"], [
            {"name": "a", "c2": "1"},
            {"name": "b", "c2": "2"}
        ])

    def test_convert_to_map_duplicate_group_names(self):
        """Test when multiple groups have the same name"""
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
            {"name": "a", "c2": "1"},
            {"name": "b", "c2": "2"},
            {"name": "c", "c2": "3"}
        ])

    def test_convert_to_map_empty_groups(self):
        """Test with empty groups in the input"""
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
        """Test with groups containing only one line after basic info"""
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
        """Test when END_OF_BASIC_INFO marker is never found"""
        groups = [
            ["Name;Value", "Another;Thing"],
            ["StillBasic;Info"],
        ]
        result = convert_to_map(groups, ";")
        self.assertIn(BASIC_INFO, result)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[BASIC_INFO]), 3)

    def test_convert_to_map_custom_delimiter_with_spaces(self):
        """Test with custom delimiter including spaces"""
        groups = [
            ["Name :: Value", f"{END_OF_BASIC_INFO} :: 1.0"],
            ["Group1", "a :: 1", "b :: 2"]
        ]
        result = convert_to_map(groups, " :: ")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)

    def test_convert_to_map_delimiter_not_found(self):
        """Test behavior when delimiter is not found in most lines"""
        groups = [
            ["NameValue", f"{END_OF_BASIC_INFO}"],
            ["Group1", "a1", "b2"]
        ]
        result = convert_to_map(groups, ";")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertEqual(result["Group1"], [])

    def test_convert_to_map_multichar_delimiter(self):
        """Test with multi-character delimiters"""
        groups = [
            ["Name<->Value", f"{END_OF_BASIC_INFO}<->3.0"],
            ["Group1", "attr1<->val1", "attr2<->val2"]
        ]
        result = convert_to_map(groups, "<->")
        self.assertIn(BASIC_INFO, result)
        self.assertIn("Group1", result)
        self.assertEqual(result["Group1"], [
            {"name": "attr1", "c2": "val1"},
            {"name": "attr2", "c2": "val2"}
        ])

    def test_convert_to_map_special_char_delimiter(self):
        """Test with special character delimiters"""
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


if __name__ == "__main__":
    unittest.main()