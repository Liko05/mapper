from parser_utils import create_attribute

BASIC_INFO = "Basic information"
END_OF_BASIC_INFO = "JCSystem.getVersion()"

# Section markers - these lines indicate new sections
SECTION_MARKERS = [
    "MESSAGE DIGEST",
    "RANDOM GENERATOR",
    "CIPHER",
    "SIGNATURE",
    "CHECKSUM",
    "UTIL",
    "SWALGS",
    "KEY PAIR",
    "KEYAGREEMENT",
]

# Key-related sections that appear after CHECKSUM
KEY_SECTIONS = [
    "AESKey",
    "DESKey",
    "KoreanSEEDKey",
    "DSAPrivateKey",
    "DSAPublicKey",
    "ECF2MPublicKey",
    "ECF2MPrivateKey",
    "ECFPPublicKey",
    "ECFPPrivateKey",
    "HMACKey",
    "RSAPrivateCRTKey",
    "RSAPrivateKey",
    "RSAPublicKey",
]


def is_section_header(line: str) -> bool:
    """Check if a line is a section header.

    Handles both fixed format (e.g., "MESSAGE DIGEST") and
    variable format (e.g., "MESSAGE DIGEST - ALG_SHA - variable data - BEGIN")
    """
    stripped = line.strip()

    # Check for variable data BEGIN marker
    if " - variable data - BEGIN" in stripped:
        return True

    # Check for standard section markers
    if stripped in SECTION_MARKERS or stripped in KEY_SECTIONS:
        return True

    return False


def is_section_end(line: str) -> bool:
    """Check if a line is a section end marker."""
    return " - END" in line


def extract_section_name(line: str) -> str:
    """Extract the section name from a header line.

    For fixed format: "MESSAGE DIGEST" -> "MESSAGE DIGEST"
    For variable format: "MESSAGE DIGEST - ALG_SHA - variable data - BEGIN"
                        -> "MESSAGE DIGEST - ALG_SHA"
    """
    stripped = line.strip()

    # Handle variable data format
    if " - variable data - BEGIN" in stripped:
        return stripped.replace(" - variable data - BEGIN", "")

    return stripped


def is_method_name_line(line: str) -> bool:
    """Check if a line is a method name line."""
    return line.startswith("method name:")


def parse_basic_info(groups: list[list[str]], delimiter: str) -> tuple[list[dict], int]:
    """Parse the basic information section at the start of the file.

    Returns:
        tuple: (list of attributes, index of first non-basic-info group)
    """
    attributes = []
    end_index = 0
    found_end = False

    for i, group in enumerate(groups):
        if found_end:
            end_index = i
            break

        for line in group:
            # Check if we've reached the end of basic info
            if END_OF_BASIC_INFO in line or is_section_header(line):
                found_end = True
                end_index = i
                break

            content = line.split(delimiter)
            if content:
                name = content[0].strip()
                value = content[1].strip() if len(content) > 1 else ''
                attributes.append(create_attribute(name, value))

    return attributes, end_index


def parse_measurement_config(line: str, delimiter: str) -> dict:
    """Parse measurement config line.

    Example: 'measurement config:;appletPrepareINS;34;appletMeasureINS;41;config;00 15 00 01...'
    Returns: {'appletPrepareINS': '34', 'appletMeasureINS': '41', 'config': '00 15 00 01...'}
    """
    parts = line.split(delimiter)
    result = {}

    # Skip "measurement config:" prefix
    i = 1
    while i < len(parts) - 1:
        key = parts[i].strip()
        value = parts[i + 1].strip() if i + 1 < len(parts) else ''
        if key and value:
            result[key] = value
        i += 2

    return result


def parse_key_value_pairs(line: str, delimiter: str) -> dict:
    """Parse a line with format 'name:;value;name:;value;...' into a dictionary."""
    parts = line.split(delimiter)
    result = {}

    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if part.endswith(':'):
            key = part[:-1]
            value = parts[i + 1].strip() if i + 1 < len(parts) else ''
            result[key] = value
            i += 2
        else:
            i += 1

    return result


def parse_measurements(line: str, delimiter: str) -> list[str]:
    """Parse a measurements line and extract the numeric values.

    Example: 'baseline measurements (ms):;27.00;7.00;7.00;9.00;9.00;'
    Returns: ['27.00', '7.00', '7.00', '9.00', '9.00']

    Also handles European format with comma as decimal separator:
    Example: 'baseline measurements (ms):;103,00;115,00;101,00;'
    Returns: ['103.00', '115.00', '101.00']
    """
    parts = line.split(delimiter)
    values = []

    # Skip the first part (label) and collect numeric values
    for part in parts[1:]:
        part = part.strip()
        if part and part not in ['CHECK', '']:
            # Convert comma to dot for European decimal format
            normalized = part.replace(',', '.')
            try:
                # Verify it's a number
                float(normalized)
                values.append(normalized)
            except ValueError:
                continue

    return values


def parse_stats(line: str, delimiter: str) -> dict:
    """Parse a stats line into a dictionary.

    Example: 'baseline stats (ms):;avg:;11.80;min:;7.00;max:;27.00;;;CHECK'
    Returns: {'avg': '11.80', 'min': '7.00', 'max': '27.00'}

    Example: 'operation stats (ms/op):;avg op:;1.05;min op:;0.96;max op:;1.38;;CHECK'
    Returns: {'avg op': '1.05', 'min op': '0.96', 'max op': '1.38'}

    Also handles European format with comma as decimal separator.
    """
    parts = line.split(delimiter)
    result = {}

    i = 1  # Skip the label
    while i < len(parts):
        part = parts[i].strip()
        if part.endswith(':'):
            key = part[:-1]
            value = parts[i + 1].strip() if i + 1 < len(parts) else ''
            if value and value not in ['CHECK', '']:
                # Convert comma to dot for European decimal format
                result[key] = value.replace(',', '.')
            i += 2
        else:
            i += 1

    return result


def parse_operation_info(line: str, delimiter: str) -> dict:
    """Parse operation info line.

    Example: 'operation info:;data length;256;total iterations;250;total invocations;250;'
    Returns: {'data length': '256', 'total iterations': '250', 'total invocations': '250'}
    """
    parts = line.split(delimiter)
    result = {}

    i = 1  # Skip "operation info:"
    while i < len(parts) - 1:
        key = parts[i].strip()
        value = parts[i + 1].strip() if i + 1 < len(parts) else ''
        if key and value:
            result[key] = value
        i += 2

    return result


def parse_method_block(lines: list[str], delimiter: str) -> dict:
    """Parse a method block into a structured object.

    A method block consists of:
    - method name line
    - measurement config line
    - Either NO_SUCH_ALGORITHM or measurement data
    """
    result = {}

    for line in lines:
        line = line.strip()

        if line.startswith("method name:"):
            # Extract method name
            # Fixed format: "method name:; ALG_NAME MethodName()"
            # Variable format: "method name:; ALG_NAME MethodName();16;"
            parts = line.split(delimiter)
            if len(parts) > 1:
                method_name = parts[1].strip()
                result["method name"] = method_name

                # Check for data length in variable format (third part after method name)
                if len(parts) > 2 and parts[2].strip():
                    data_length = parts[2].strip()
                    # Only add if it looks like a number
                    if data_length.isdigit():
                        result["data length"] = data_length

        elif line.startswith("measurement config:"):
            # Parse measurement config
            config = parse_measurement_config(line, delimiter)
            if config:
                result["measurement config"] = config

        elif line == "NO_SUCH_ALGORITHM":
            result["supported"] = False

        elif line.startswith("baseline measurements"):
            result["baseline measurements"] = parse_measurements(line, delimiter)

        elif line.startswith("baseline stats"):
            stats = parse_stats(line, delimiter)
            result["baseline stats"] = stats

        elif line.startswith("operation raw measurements"):
            result["operation raw measurements"] = parse_measurements(line, delimiter)

        elif line.startswith("operation stats"):
            stats = parse_stats(line, delimiter)
            result["operation stats"] = stats

        elif line.startswith("operation info:"):
            info = parse_operation_info(line, delimiter)
            result["operation info"] = info

    # If we got measurement data, mark as supported
    if "baseline measurements" in result or "operation stats" in result:
        result["supported"] = True

    return result


def convert_to_map_jcperf(groups: list[list[str]], delimiter: str) -> dict:
    """Convert JavaCard performance CSV data to a structured JSON-compatible dictionary.

    The output structure:
    - "_type": "javacard-performance"
    - "Basic information": list of {name, value} attributes
    - "MESSAGE DIGEST": array of method test results
    - "CIPHER": array of method test results
    - etc.

    Each method test result contains:
    - "method name": the algorithm and method being tested
    - "measurement config": configuration parameters
    - "supported": boolean indicating if algorithm is supported
    - "baseline measurements": array of baseline timing values
    - "baseline stats": {avg, min, max}
    - "operation raw measurements": array of operation timing values
    - "operation stats": {avg op, min op, max op}
    - "operation info": {data length, total iterations, total invocations}
    """
    result = {"_type": "javacard-performance"}

    # Parse basic info
    basic_info, start_index = parse_basic_info(groups, delimiter)
    result[BASIC_INFO] = basic_info

    current_section = None
    current_method_lines = []

    for i in range(start_index, len(groups)):
        group = groups[i]
        if not group:
            continue

        for line in group:
            line_stripped = line.strip()

            # Check for section headers
            if is_section_header(line_stripped):
                # Save previous method if exists
                if current_method_lines and current_section:
                    method_result = parse_method_block(current_method_lines, delimiter)
                    if method_result:
                        result[current_section].append(method_result)
                    current_method_lines = []

                current_section = extract_section_name(line_stripped)
                if current_section not in result:
                    result[current_section] = []
                continue

            # Skip section end markers
            if is_section_end(line_stripped):
                # Save previous method if exists
                if current_method_lines and current_section:
                    method_result = parse_method_block(current_method_lines, delimiter)
                    if method_result:
                        result[current_section].append(method_result)
                    current_method_lines = []
                continue

            # Skip empty lines within groups
            if not line_stripped:
                continue

            # If we hit a new method name, save the previous one
            if is_method_name_line(line_stripped):
                if current_method_lines and current_section:
                    method_result = parse_method_block(current_method_lines, delimiter)
                    if method_result:
                        result[current_section].append(method_result)
                current_method_lines = [line_stripped]
            elif current_section:
                # Accumulate lines for current method
                current_method_lines.append(line_stripped)

    # Don't forget the last method
    if current_method_lines and current_section:
        method_result = parse_method_block(current_method_lines, delimiter)
        if method_result:
            result[current_section].append(method_result)

    return result

