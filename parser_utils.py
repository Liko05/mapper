import logging

logger = logging.getLogger(__name__)


def load_file(path: str):
    try:
        logger.info(f"Loading file: {path}")
        with open(path, 'r') as file:
            content = file.read()
        return prepare_lines(content.splitlines())

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
    except Exception as e:
        logger.exception(f"An error occurred while reading {path}: {e}")

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
        "value": value
    }

def load_exclusions(path: str) -> set[str]:
    """Load exclusion property names from a file, ignoring empty and comment lines (#...)."""
    excluded: set[str] = set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                trimmed = line.strip()
                if not trimmed or trimmed.startswith('#'):
                    continue
                excluded.add(trimmed)
        logger.info(f"Loaded {len(excluded)} excluded propertie(s) from {path}")
    except FileNotFoundError:
        logger.error(f"Exclusion file not found: {path}")
    except Exception as e:
        logger.exception(f"Failed to read exclusion file {path}: {e}")
    return excluded


def apply_exclusions(result: dict, excluded: set[str]) -> dict:
    """Return a new result dict with attributes filtered by excluded property names."""
    if not excluded:
        return result
    filtered: dict = {}
    removed_count = 0
    for group, attrs in result.items():
        kept_attrs = []
        for attr in attrs:
            if attr.get('name') in excluded:
                removed_count += 1
                continue
            kept_attrs.append(attr)
        filtered[group] = kept_attrs
    logger.info(f"Excluded {removed_count} attribute(s) by name")
    return filtered