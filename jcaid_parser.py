from typing import Optional
from parser_utils import create_attribute

BASIC_INFO = "Basic information"

# Section markers
SECTION_CARD_INFO = "***** Card info"
SECTION_CARD_DATA = "***** CARD DATA"
SECTION_KEY_INFO = "***** KEY INFO"
SECTION_PACKAGE_AID = "PACKAGE AID;"
SECTION_FULL_PACKAGE_AID = "FULL PACKAGE AID;"


def is_section_marker(line: str) -> Optional[str]:
    """Check if a line is a section marker and return the section name.

    Returns the section name or None if not a section marker.
    """
    stripped = line.strip()

    if stripped.startswith("***** Card info"):
        return "Card info"
    elif stripped.startswith("***** CARD DATA"):
        return "Card data"
    elif stripped.startswith("***** KEY INFO"):
        return "Key info"
    elif stripped.startswith("PACKAGE AID;"):
        return "Package AID"
    elif stripped.startswith("FULL PACKAGE AID;"):
        return "Full package AID support"

    return None


def parse_basic_info(lines: list[str], delimiter: str) -> list[dict]:
    """Parse basic information lines into name-value pairs."""
    attributes = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("*****") or line.startswith("http"):
            continue

        # Skip lines that are headers or section markers
        if line.startswith("PACKAGE AID;") or line.startswith("FULL PACKAGE AID;"):
            break

        parts = line.split(delimiter)
        if len(parts) >= 2:
            name = parts[0].strip()
            value = parts[1].strip()
            if name:
                attributes.append(create_attribute(name, value))
        elif len(parts) == 1 and parts[0].strip():
            # Single value line (like "NO CPLC")
            attributes.append(create_attribute(parts[0].strip(), ""))

    return attributes


def parse_key_info(lines: list[str], delimiter: str) -> list[dict]:
    """Parse key info section.

    Example lines:
    VER;255 ID;1 TYPE;DES3 LEN;16
    Key version suggests factory keys
    """
    keys = []
    notes = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("VER;"):
            # Parse key entry: VER;255 ID;1 TYPE;DES3 LEN;16
            key_info = {}
            # Split by space first to get key-value pairs
            pairs = line.split(" ")
            for pair in pairs:
                if ";" in pair:
                    parts = pair.split(";")
                    if len(parts) == 2:
                        key_info[parts[0].strip()] = parts[1].strip()
            if key_info:
                keys.append(key_info)
        elif line.startswith("*****") or line.startswith("PACKAGE AID"):
            break
        else:
            # Note lines like "Key version suggests factory keys"
            notes.append(line)

    result = {"keys": keys}
    if notes:
        result["notes"] = notes

    return result


def parse_package_aid_table(lines: list[str], delimiter: str) -> list[dict]:
    """Parse the package AID table.

    Header: PACKAGE AID; MAJOR VERSION; MINOR VERSION; PACKAGE NAME; INTRODUCING JC API VERSION;
    Data: a0000000620001; 1; 0; java.lang; 2.1
    """
    packages = []
    header_found = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip header line
        if line.startswith("PACKAGE AID;"):
            header_found = True
            continue

        # Stop at next section
        if line.startswith("FULL PACKAGE AID;") or line.startswith("*****"):
            break

        if header_found:
            parts = [p.strip() for p in line.split(delimiter)]
            if len(parts) >= 5:
                packages.append({
                    "package_aid": parts[0],
                    "major_version": parts[1],
                    "minor_version": parts[2],
                    "package_name": parts[3],
                    "jc_api_version": parts[4]
                })

    return packages


def parse_full_package_aid_table(lines: list[str], delimiter: str) -> list[dict]:
    """Parse the full package AID support table.

    Header: FULL PACKAGE AID; IS SUPPORTED?; PACKAGE NAME WITH VERSION;
    Data: 000107A0000000620001; 	yes; 	java.lang v1.0 a0000000620001;
    """
    packages = []
    header_found = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip header line
        if line.startswith("FULL PACKAGE AID;"):
            header_found = True
            continue

        if header_found:
            parts = [p.strip() for p in line.split(delimiter)]
            if len(parts) >= 3:
                is_supported = parts[1].lower() == "yes"
                packages.append({
                    "full_package_aid": parts[0],
                    "supported": is_supported,
                    "package_name_version": parts[2]
                })

    return packages


def convert_to_map_aid(groups: list[list[str]], delimiter: str) -> dict:
    """Convert JavaCard AID support CSV data to a structured JSON-compatible dictionary.

    The output structure:
    - "_type": "javacard-aid"
    - "Basic information": list of {name, value} attributes
    - "Key info": {keys: [...], notes: [...]}
    - "Package AID": array of package info objects
    - "Full package AID support": array of support status objects
    """
    result = {"_type": "javacard-aid"}

    # Flatten all groups into a single list of lines for easier processing
    all_lines = []
    for group in groups:
        all_lines.extend(group)

    # Find section boundaries
    basic_info_lines = []
    key_info_lines = []
    package_aid_lines = []
    full_package_aid_lines = []

    current_section = "basic"

    for line in all_lines:
        stripped = line.strip()

        # Check for section markers
        section = is_section_marker(stripped)
        if section:
            if section == "Card info":
                current_section = "card_info"
            elif section == "Card data":
                current_section = "card_data"
            elif section == "Key info":
                current_section = "key_info"
            elif section == "Package AID":
                current_section = "package_aid"
            elif section == "Full package AID support":
                current_section = "full_package_aid"
            continue

        # Add line to appropriate section
        if current_section == "basic" or current_section == "card_info" or current_section == "card_data":
            basic_info_lines.append(line)
        elif current_section == "key_info":
            key_info_lines.append(line)
        elif current_section == "package_aid":
            package_aid_lines.append(line)
        elif current_section == "full_package_aid":
            full_package_aid_lines.append(line)

    # Parse each section
    result[BASIC_INFO] = parse_basic_info(basic_info_lines, delimiter)

    if key_info_lines:
        result["Key info"] = parse_key_info(key_info_lines, delimiter)

    if package_aid_lines:
        result["Package AID"] = parse_package_aid_table(
            [SECTION_PACKAGE_AID] + package_aid_lines, delimiter
        )

    if full_package_aid_lines:
        result["Full package AID support"] = parse_full_package_aid_table(
            [SECTION_FULL_PACKAGE_AID] + full_package_aid_lines, delimiter
        )

    return result

