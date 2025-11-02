import json, argparse
from pathlib import Path
import logging
from typing import Optional, Set


BASIC_INFO = "Basic information"
END_OF_BASIC_INFO = "JavaCard support version"

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
        attributes.append(create_attribute(content[0], content[1]))

    return group_name, attributes, finished

# Convert the list of groups into a dictionary mapping group names to their attributes
def convert_to_map(groups: list[list[str]], delimiter: str):
    finished_basic_info = False
    result = {}

    for group in groups:
        if len(group) < 2 and finished_basic_info:
            continue

        key, attributes, finished = parse_group(group, finished_basic_info, delimiter)
        finished_basic_info = finished
        if key in result:
            result[key].extend(attributes)
        else:
            result[key] = attributes
    return result


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


def process_files(file_paths: list[str], delimiter: str = ';', excluded_properties: Optional[Set[str]] = None) -> list[Path]:
    """Process given files and write JSON outputs next to inputs.

    Returns a list of written output Paths.
    """
    outputs: list[Path] = []
    for file_path in file_paths:
        logger.info(f"Processing file: {file_path}")
        groups = load_file(file_path)
        if groups is None:
            logger.warning(f"Skipping {file_path} due to previous error.")
            continue
        final_result = convert_to_map(groups, delimiter)
        if excluded_properties:
            final_result = apply_exclusions(final_result, excluded_properties)
        logger.info("Processing completed.")
        out_path = Path(file_path).with_suffix('.json')
        try:
            with open(out_path, "w", encoding='utf-8') as f:
                json.dump(final_result, f, indent=4, ensure_ascii=False)
            logger.info(f"Result saved to {out_path}")
            outputs.append(out_path)
        except Exception as e:
            logger.exception(f"Failed to write output for {file_path}: {e}")
    return outputs


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')

    parser = argparse.ArgumentParser(description='Process one or more files with customizable delimiter')
    parser.add_argument('file_paths', nargs='+', help='Path(s) to the file(s) to process')
    parser.add_argument('-d', '--delimiter', default=';', help='Delimiter to use (default: ;)')
    parser.add_argument('-x', '--exclude-file', default=None, help='Path to a file with property names to exclude')

    args = parser.parse_args()
    files = args.file_paths
    delimiter = args.delimiter

    if not files:
        logger.error("Please provide at least one file path.")
        exit(1)

    excluded = load_exclusions(args.exclude_file) if args.exclude_file else None
    process_files(files, delimiter, excluded_properties=excluded)
