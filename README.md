# JavaCard Info Parser

A Python script to parse JavaCard information files and convert them into structured JSON.
## Usage

1. Place your input file in the project directory.
2. Run the script from the command line:
```bash
    python main.py <input_file>
```
3. The output will be saved as `result.json`.

## Testing

Run all tests using:
```bash
    python -m unittest discover tests
```

## Requirements

- Python 3.9 or higher

## Project Structure

- `main.py` - Main parsing logic
- `tests/test_parser.py` - Unit tests