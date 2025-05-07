"""Integration test example for AITHENA task solver.

Example:
    Run this doctest with:
    
    ```
    python -m doctest -v examples/process_file.py
    ```
"""
import os
import doctest
import sys
import shutil
import tempfile
import json

# Add the parent directory to sys.path so we can import the src module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.utlis import get_llm_client
from src.aithena_task_solver import process_file


def test_processing_file() -> None:
    """
    Demonstrate the full workflow of processing a file with the AITHENA task solver.
    
    This test:
    1. Reads a Python file from the data directory
    2. Processes it with a real LLM client
    3. Verifies the expected results

    >>> temp_dir = tempfile.mkdtemp()
    >>> try:
    ...     file_name='1.py'
    ...     file_content = read_test_file(file_name)
    ...     client = get_llm_client()
    ...
    ...     result, saved_files = process_file(client, file_name, file_content, temp_dir)
    ...
    ...     print(f"Copyright holder: {result.copyright_holder}")
    ...     print(f"License name: {result.license_name}")
    ...     print(f"License type: {result.license_type.name}")
    ...     print(f"Function count: {result.function_count}")
    ...     check_saved_files(saved_files)
    ... finally:
    ...     shutil.rmtree(temp_dir)
    Copyright holder: Elon Musk
    License name: GNU GPL v3
    License type: COPYLEFT
    Function count: 2
    Number of saved files: 2
    - 1_rust_functions.rs
      - Contains fn foo(): True
      - Contains fn bar(): True
    - 1_analysis.json
      - File contains copyright_holder: True
      - File contains license_name: True
    """
    pass


def read_test_file(file_name: str) -> str:
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', file_name)
    with open(file_path, 'r') as f:
        file_content = f.read()
    return file_content

def check_saved_files(saved_files) -> None:
    print(f"Number of saved files: {len(saved_files)}")
    for file_path in saved_files:
        file_name = os.path.basename(file_path)
        print(f"- {file_name}")

        # For the JSON file, verify its content
        if file_name.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"  - File contains copyright_holder: {'copyright_holder' in data}")
            print(f"  - File contains license_name: {'license_name' in data}")

        # For the Rust file, check that it contains the expected content
        if file_name.endswith('.rs'):
            with open(file_path, 'r') as f:
                content = f.read()
            print(f"  - Contains fn foo(): {'fn foo()' in content}")
            print(f"  - Contains fn bar(): {'fn bar()' in content}")

if __name__ == "__main__":
    doctest.testmod(verbose=True)