# AITHENA License Analysis Tool

This project analyzes Python files to extract license information and perform code analysis based on license type.

## Features

- Extracts copyright holder and license information from source files
- Identifies license types (permissive vs. copyleft)
- For permissive licenses: extracts function names with argument counts
- For copyleft licenses:
  - If file has >2 functions: extracts function names with argument counts
  - If file has ≤2 functions: rewrites the file in Rust using LLM

## Installation

```bash
# Clone the repository
git clone [repository-url]

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the main analysis
python main.py

# Run tests
pytest tests/
```

## Project Structure

```
aithena-python-test-task/
├── src/                  # Main source code
│   ├── license/          # License detection and analysis
│   ├── parser/           # Code parsing and function extraction
│   ├── llm/              # LLM integration
│   └── output/           # Output formatting
├── tests/                # Test files
├── data/                 # Input files
├── results/              # Processed output files
└── main.py               # Entry point
```

## License

This project is for assessment purposes. All rights reserved.