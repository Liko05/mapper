import sys, json


BASIC_INFO = "Basic information"
END_OF_BASIC_INFO = "JavaCard support version"

def load_file(path: str):
    try:
        with open(path, 'r') as file:
            content = file.read()
        return prepare_lines(content.splitlines())

    except FileNotFoundError:
        print(f"File not found: {path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Prepare lines by splitting them into groups based on empty lines
def prepare_lines(lines: list[str]) -> list[list[str]]:
    result = []
    current = []
    for line in lines:
        if line.strip() == "":
            if current:
                result.append(current)
                current = []
        else:
            current.append(line.strip())
    if current:
        result.append(current)
    return result


# create an attribute dictionary from name and value
def create_attribute(name: str, value: str):
    return {
        "name": name,
        "c2": value
    }

# Parse a group of lines into a name, attributes, and whether basic info is finished
def parse_group(group: list[str], finished_basic_info):
    finished = finished_basic_info
    attributes = []
    group_name = None if finished else BASIC_INFO

    for index, line in enumerate(group):
        if not finished:
            if END_OF_BASIC_INFO in line:
                finished = True
        else:
            if group_name is None:
                if ';' not in line:
                    group_name = line.strip()
                else:
                    name, _ = line.split(";", 1)
                    if '.' in name:
                        group_name = name.split('.')[0].strip()
                    else:
                        group_name = name.strip()

        content = line.split(";")
        if len(content) < 2:
            continue
        attributes.append(create_attribute(content[0], content[1]))

    return group_name, attributes, finished

# Convert the list of groups into a dictionary mapping group names to their attributes
def convert_to_map(groups: list[list[str]]):
    finished_basic_info = False
    result = {}

    for group in groups:
        if len(group) < 2 and finished_basic_info:
            continue

        key, attributes, finished = parse_group(group, finished_basic_info)
        finished_basic_info = finished
        if key in result:
            result[key].extend(attributes)
        else:
            result[key] = attributes
    return result


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Only the path to file is allowed")
        exit(1)

    print("Processing file:", sys.argv[1])
    final_result = convert_to_map(load_file(sys.argv[1]))
    print("Processing completed.")
    print(json.dumps(final_result, indent=4, ensure_ascii=False))
    with open("result.json", "w") as file:
        json.dump(final_result, file, indent=4, ensure_ascii=False)
    print("Result saved to result.json")


