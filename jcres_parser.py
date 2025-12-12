from parser_utils import create_attribute

BASIC_INFO = "Basic information"
END_OF_BASIC_INFO = "JavaCard support version"
ATTRIBUTE_NAMES = ["algorithm_name","is_supported", "time_elapsed", "persistent_mem_allocated", "ram_deselect_allocated", "ram_reset_allocated"]

# Parse a group of lines into a name, attributes, and whether basic info is finished
def parse_group(group: list[str], finished_basic_info, delimiter: str):
    finished = finished_basic_info
    attributes = []
    group_name = None if finished else BASIC_INFO

    for index, line in enumerate(group):
        if not finished:
            if END_OF_BASIC_INFO in line:
                finished = True
        else:
            if group_name is None:
                if delimiter not in line:
                    group_name = line.strip()
                else:
                    name, _ = line.split(delimiter, 1)
                    if '.' in name:
                        group_name = name.split('.')[0].strip()
                    else:
                        group_name = name.strip()

        content = line.split(delimiter)
        if len(content) < 2:
            continue
        if group_name == "JCSystem" or group_name == "CPLC" or not finished or content[0] == "JavaCard support version":
            attributes.append(create_attribute(content[0], content[1]))
            continue

        alg_values = []
        for i, val in enumerate(content):
            if val == group_name:
                continue
            alg_values.append(create_attribute(ATTRIBUTE_NAMES[i], content[i]))
        if len(alg_values) != 0:
            attributes.append(alg_values)

    return group_name, attributes, finished

# Convert the list of groups into a dictionary mapping group names to their attributes
def convert_to_map(groups: list[list[str]], delimiter: str):
    finished_basic_info = False
    result = {"_type": "javacard"}
    first = True

    for group in groups:
        if len(group) < 2 and finished_basic_info:
            continue

        key, attributes, finished = parse_group(group, finished_basic_info, delimiter)
        if first:
            finished_basic_info = True
            first = False
        else:
            finished_basic_info = finished
        if key in result:
            result[key].extend(attributes)
        else:
            result[key] = attributes
    return result
