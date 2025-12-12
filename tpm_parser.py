from parser_utils import create_attribute

BASIC_INFO = "Basic information"

# Keywords that indicate the start of a configuration parameter line
CONFIG_KEYWORDS = ["Key parameters:", "Algorithm:", "Hash algorithm:", "Data length (bytes):"]


def is_tpm_operation(line: str) -> bool:
    """Check if a line is a TPM operation header (e.g., TPM2_Create, TPM2_Sign, etc.)"""
    stripped = line.strip()
    return stripped.startswith("TPM2_") and ";" not in stripped


def is_config_line(line: str) -> bool:
    """Check if a line is a configuration parameter line"""
    return any(line.startswith(kw) for kw in CONFIG_KEYWORDS)


def parse_basic_info(group: list[str], delimiter: str) -> list[dict]:
    """Parse the basic information group (first group in the file)"""
    attributes = []
    for line in group:
        content = line.split(delimiter)
        if content:
            name = content[0].strip()
            value = content[1].strip() if len(content) > 1 else ''
            attributes.append(create_attribute(name, value))
    return attributes


def parse_key_value_pairs(line: str, delimiter: str) -> dict:
    """Parse a line with format 'name:;value;name:;value;...' into a dictionary.

    Example: 'Key parameters:;ECC 0x0003' -> {'Key parameters': 'ECC 0x0003'}
    Example: 'Algorithm:;0x0006;Key length:;128;Mode:;0x0040' ->
             {'Algorithm': '0x0006', 'Key length': '128', 'Mode': '0x0040'}
    """
    parts = line.split(delimiter)
    result = {}

    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if part.endswith(':'):
            # This is a key, next part is the value
            key = part[:-1]  # Remove trailing colon
            value = parts[i + 1].strip() if i + 1 < len(parts) else ''
            result[key] = value
            i += 2
        else:
            # Standalone value or malformed, skip
            i += 1

    return result


def parse_stats_line(line: str, delimiter: str) -> dict:
    """Parse operation stats or info line into a dictionary.

    Example: 'operation stats (ms/op):;avg op:;315.61;min op:;308.45;max op:;340.50'
    Returns: {'avg op': '315.61', 'min op': '308.45', 'max op': '340.50'}

    Example: 'operation info:;total iterations:;1000;successful:;1000;failed:;0;error:;None'
    Returns: {'total iterations': '1000', 'successful': '1000', 'failed': '0', 'error': 'None'}
    """
    parts = line.split(delimiter)
    result = {}

    # Skip the first part (e.g., "operation stats (ms/op):" or "operation info:")
    i = 1
    while i < len(parts):
        part = parts[i].strip()
        if part.endswith(':'):
            # This is a key, next part is the value
            key = part[:-1]  # Remove trailing colon
            value = parts[i + 1].strip() if i + 1 < len(parts) else ''
            result[key] = value
            i += 2
        else:
            i += 1

    return result


def parse_data_group(group: list[str], delimiter: str) -> dict:
    """Parse a data group (config params + operation stats + operation info).

    Returns a structured object with parsed configuration and stats.
    """
    if not group:
        return None

    result = {}

    # First line contains configuration parameters
    config_line = group[0].strip()
    config_params = parse_key_value_pairs(config_line, delimiter)
    result.update(config_params)

    # Parse remaining lines (operation stats and operation info)
    for line in group[1:]:
        if line.startswith("operation stats"):
            stats = parse_stats_line(line, delimiter)
            result.update(stats)
        elif line.startswith("operation info"):
            info = parse_stats_line(line, delimiter)
            result.update(info)

    return result


def convert_to_map_tpm(groups: list[list[str]], delimiter: str) -> dict:
    """Convert TPM CSV data to a structured JSON-compatible dictionary.

    The output structure:
    - "_type": "tpm" - indicates this is a TPM performance profile
    - "Basic information": list of {name, value} attributes
    - "TPM2_Create": array of test result objects with parsed properties
    - "TPM2_Sign": array of test result objects with parsed properties
    - etc.

    Each test result object contains:
    - Configuration parameters (e.g., "Key parameters": "ECC 0x0003", "Scheme": "0x0018")
    - Stats (e.g., "avg op": "315.61", "min op": "308.45", "max op": "340.50")
    - Info (e.g., "total iterations": "1000", "successful": "1000", "failed": "0", "error": "None")
    """
    result = {"_type": "tpm"}
    current_operation = None  # Track the current TPM operation

    for i, group in enumerate(groups):
        if not group:
            continue

        first_line = group[0].strip()

        if i == 0:
            # First group is always basic information
            result[BASIC_INFO] = parse_basic_info(group, delimiter)
        elif is_tpm_operation(first_line):
            # This is an operation header group (just "TPM2_Create" etc.)
            current_operation = first_line
            # Initialize array for this operation if not exists
            if current_operation not in result:
                result[current_operation] = []
        elif is_config_line(first_line):
            # This is a data group belonging to the current operation
            test_result = parse_data_group(group, delimiter)

            if current_operation and test_result:
                result[current_operation].append(test_result)
        else:
            # Handle any other groups - try to parse them similarly
            if current_operation:
                test_result = parse_data_group(group, delimiter)
                if test_result:
                    result[current_operation].append(test_result)

    return result
