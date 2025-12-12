# Smartcard & TPM Profile Parser

A Python tool to parse CSV profile files from smartcard and TPM testing tools (like [JCAlgTest](https://github.com/crocs-muni/JCAlgTest)) and convert them into structured JSON format.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd crocs-mapper

# (Optional) Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
```

## Usage

### Process Individual Files

Process one or more CSV files (output saved next to input files):

```bash
python main.py file1.csv file2.csv
```

### Process Entire Folder

Process all CSV files in a folder recursively, creating a mirrored directory structure with JSON outputs:

```bash
# Creates <folder_name>_parsed/ in current directory
python main.py --folder /path/to/csv/folder

# Specify custom output location
python main.py --folder /path/to/csv/folder --output /path/to/output
```

### Command Line Options

```
usage: main.py [-h] [-f FOLDER_PATH] [-o OUTPUT_PATH] [-d DELIMITER] [-x EXCLUDE_FILE] [file_paths ...]

positional arguments:
  file_paths                    Path(s) to CSV file(s) to process

options:
  -h, --help                    Show this help message and exit
  -f, --folder FOLDER_PATH      Path to folder containing CSV files (processes recursively)
  -o, --output OUTPUT_PATH      Output folder path (only used with --folder)
  -d, --delimiter DELIMITER     Delimiter to use (default: ;)
  -x, --exclude-file FILE       Path to a file with property names to exclude
```

### Examples

```bash
# Process a single TPM profile
python main.py jcalg_results/tpm/profiles/performance/INTC_Intel.csv

# Process all profiles in a folder
python main.py --folder jcalg_results/

# Process with custom delimiter
python main.py --delimiter "," data.csv

# Process folder with custom output location
python main.py -f ./input_profiles -o ./parsed_results
```

## Output Format

All output JSON files include a `_type` field indicating the parser used:

- `"tpm"` - TPM performance profiles
- `"javacard-aid"` - JavaCard AID support profiles  
- `"javacard-performance"` - JavaCard performance profiles
- `"javacard"` - JavaCard algorithm support profiles

### Example Output Structure

**TPM Performance:**
```json
{
    "_type": "tpm",
    "Basic information": [...],
    "TPM2_Create": [
        {
            "Key parameters": "RSA 1024",
            "avg op": "996.97",
            "min op": "192.47",
            "max op": "4708.57",
            "total iterations": "1000"
        }
    ]
}
```

**JavaCard AID Support:**
```json
{
    "_type": "javacard-aid",
    "Basic information": [...],
    "Key info": {"keys": [...], "notes": [...]},
    "Package AID": [...],
    "Full package AID support": [...]
}
```

## Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Run specific test file:
```bash
python -m pytest tests/test_tpm_parser.py -v
```

## Requirements

- Python 3.9 or higher

## Project Structure

```
crocs-mapper/
├── main.py              # Main entry point and CLI
├── parser_utils.py      # Shared utility functions
├── jcres_parser.py      # JavaCard algorithm support parser
├── jcperf_parser.py     # JavaCard performance parser
├── jcaid_parser.py      # JavaCard AID support parser
├── tpm_parser.py        # TPM performance parser
├── tests/               # Unit and integration tests
│   ├── test_main.py
│   ├── test_tpm_parser.py
│   ├── test_jcperf_parser.py
│   ├── test_jcaid_parser.py
│   └── ...
└── jcalg_results/       # Sample data files
```

## License

[Add your license here]
