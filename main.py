import json, argparse
from pathlib import Path
import logging
import shutil
from typing import Optional, Set
import parser_utils
from jcres_parser import convert_to_map
from tpm_parser import convert_to_map_tpm
from jcperf_parser import convert_to_map_jcperf
from jcaid_parser import convert_to_map_aid

logger = logging.getLogger(__name__)


def detect_parser_type(file_path: str) -> str:
    """Detect which parser to use based on file path and content.

    Returns:
        str: 'tpm', 'javacard-performance', 'javacard-aid', or 'javacard-algsupport'
    """
    file_path_lower = file_path.lower()

    # Check for TPM files
    if 'tpm' in file_path_lower:
        return 'tpm'

    # Check for JavaCard AID support files
    if '/aid/' in file_path_lower or '\\aid\\' in file_path_lower or 'aidsupport' in file_path_lower:
        return 'javacard-aid'

    # Check for JavaCard performance files
    if 'performance' in file_path_lower:
        return 'javacard-performance'

    # Default to JavaCard algorithm support parser
    return 'javacard-algsupport'


def process_files(file_paths: list[str], delimiter: str = ';', excluded_properties: Optional[Set[str]] = None,
                  output_dir: Optional[Path] = None, source_base: Optional[Path] = None) -> list[Path]:
    """Process given files and write JSON outputs.

    Args:
        file_paths: List of file paths to process
        delimiter: CSV delimiter character
        excluded_properties: Set of property names to exclude from output
        output_dir: If provided, write outputs to this directory preserving relative structure
        source_base: Base path for calculating relative paths (used with output_dir)

    Returns a list of written output Paths.
    """
    outputs: list[Path] = []
    for file_path in file_paths:
        logger.info(f"Processing file: {file_path}")
        groups = parser_utils.load_file(file_path)
        if groups is None:
            logger.warning(f"Skipping {file_path} due to previous error.")
            continue

        parser_type = detect_parser_type(file_path)
        logger.info(f"Detected parser type: {parser_type}")

        if parser_type == 'tpm':
            final_result = convert_to_map_tpm(groups, delimiter)
        elif parser_type == 'javacard-performance':
            final_result = convert_to_map_jcperf(groups, delimiter)
        elif parser_type == 'javacard-aid':
            final_result = convert_to_map_aid(groups, delimiter)
        else:
            final_result = convert_to_map(groups, delimiter)

        if excluded_properties:
            final_result = parser_utils.apply_exclusions(final_result, excluded_properties)
        logger.info("Processing completed.")

        # Determine output path
        if output_dir and source_base:
            # Calculate relative path from source base and create in output dir
            rel_path = Path(file_path).relative_to(source_base)
            out_path = (output_dir / rel_path).with_suffix('.json')
            # Ensure parent directories exist
            out_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Default: write next to input file
            out_path = Path(file_path).with_suffix('.json')

        try:
            with open(out_path, "w", encoding='utf-8') as f:
                json.dump(final_result, f, indent=4, ensure_ascii=False)
            logger.info(f"Result saved to {out_path}")
            outputs.append(out_path)
        except Exception as e:
            logger.exception(f"Failed to write output for {file_path}: {e}")
    return outputs


def process_folder(folder_path: str, output_folder: Optional[str] = None,
                   delimiter: str = ';', excluded_properties: Optional[Set[str]] = None) -> list[Path]:
    """Process all CSV files in a folder and create mirrored structure with JSON outputs.

    Args:
        folder_path: Path to the source folder containing CSV files
        output_folder: Path to output folder (default: folder name + '_parsed' in current directory)
        delimiter: CSV delimiter character
        excluded_properties: Set of property names to exclude from output

    Returns a list of written output Paths.
    """
    source_path = Path(folder_path).resolve()

    if not source_path.exists():
        logger.error(f"Source folder does not exist: {source_path}")
        return []

    if not source_path.is_dir():
        logger.error(f"Path is not a directory: {source_path}")
        return []

    # Determine output folder
    if output_folder:
        output_path = Path(output_folder).resolve()
    else:
        # Default: create folder with same name + '_parsed' in current working directory
        output_path = Path.cwd() / f"{source_path.name}_parsed"

    logger.info(f"Source folder: {source_path}")
    logger.info(f"Output folder: {output_path}")

    # Find all CSV files recursively
    csv_files = list(source_path.rglob('*.csv'))

    if not csv_files:
        logger.warning(f"No CSV files found in {source_path}")
        return []

    logger.info(f"Found {len(csv_files)} CSV file(s) to process")

    # Create output folder structure
    output_path.mkdir(parents=True, exist_ok=True)

    # Process all files
    file_paths = [str(f) for f in csv_files]
    outputs = process_files(
        file_paths,
        delimiter=delimiter,
        excluded_properties=excluded_properties,
        output_dir=output_path,
        source_base=source_path
    )

    logger.info(f"Processing complete. {len(outputs)} file(s) converted.")
    return outputs


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')

    parser = argparse.ArgumentParser(
        description='Parse CSV files from smartcard/TPM testing tools and convert to JSON format.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process individual files (output saved next to input):
  python main.py file1.csv file2.csv

  # Process entire folder (creates mirrored structure in current directory):
  python main.py --folder /path/to/csv/folder

  # Process folder with custom output location:
  python main.py --folder /path/to/csv/folder --output /path/to/output
        '''
    )

    # Input options
    parser.add_argument('file_paths', nargs='*', default=[],
                        help='Path(s) to CSV file(s) to process')
    parser.add_argument('-f', '--folder', dest='folder_path',
                        help='Path to folder containing CSV files (processes recursively)')

    # Output options
    parser.add_argument('-o', '--output', dest='output_path',
                        help='Output folder path (only used with --folder)')

    # Processing options
    parser.add_argument('-d', '--delimiter', default=';',
                        help='Delimiter to use (default: ;)')
    parser.add_argument('-x', '--exclude-file', default=None,
                        help='Path to a file with property names to exclude')

    args = parser.parse_args()
    delimiter = args.delimiter
    excluded = parser_utils.load_exclusions(args.exclude_file) if args.exclude_file else None

    if args.folder_path:
        # Folder mode: process all CSV files in folder
        process_folder(
            args.folder_path,
            output_folder=args.output_path,
            delimiter=delimiter,
            excluded_properties=excluded
        )
    elif args.file_paths:
        # File mode: process individual files
        process_files(args.file_paths, delimiter, excluded_properties=excluded)
    else:
        parser.error("Please provide either file paths or use --folder option.")
