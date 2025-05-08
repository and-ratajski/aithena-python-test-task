"""Integration test example for AITHENA task solver.

Example:
    Run this doctest with (mind that you need to create .env file with your API keys):
    
    ```
    python -m doctest -v examples/process_files_sync.py
    ```
"""

import doctest
import json
import os
import shutil
import tempfile

from src.aithena_task_solver import process_file
from src.llm.utlis import get_llm_client


def test_processing_file_1() -> None:
    """
    Demonstrate the full workflow of processing file 1.py with the AITHENA task solver.

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


def test_processing_file_2() -> None:
    """
    Demonstrate the full workflow of processing file 2.py with the AITHENA task solver.

    This test:
    1. Reads a Python file from the data directory
    2. Processes it with a real LLM client
    3. Verifies the expected results

    >>> temp_dir = tempfile.mkdtemp()
    >>> try:
    ...     file_name='2.py'
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
    Copyright holder: Guido Musk
    License name: GNU GPL v3
    License type: COPYLEFT
    Function count: 4
    Number of saved files: 2
    - 2_functions.json
      - File contains function entries
    - 2_analysis.json
      - File contains copyright_holder: True
      - File contains license_name: True
    """
    pass


def test_processing_file_3() -> None:
    """
    Demonstrate the full workflow of processing file 3.py with the AITHENA task solver.

    This test:
    1. Reads a JavaScript file with JavaScript-style comments (.py extension)
    2. Processes it with a real LLM client
    3. Verifies the expected results

    >>> temp_dir = tempfile.mkdtemp()
    >>> try:
    ...     file_name='3.py'
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
    Copyright holder: Brendan Eich
    License name: MIT License
    License type: PERMISSIVE
    Function count: 1
    Number of saved files: 2
    - 3_functions.json
      - File contains function entries
    - 3_analysis.json
      - File contains copyright_holder: True
      - File contains license_name: True
    """
    pass


def read_test_file(file_name: str) -> str:
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", file_name)
    with open(file_path, "r") as f:
        file_content = f.read()
    return file_content


def check_saved_files(saved_files) -> None:
    print(f"Number of saved files: {len(saved_files)}")
    for file_path in saved_files:
        file_name = os.path.basename(file_path)
        print(f"- {file_name}")

        # For the analysis JSON file, verify its content
        if file_name.endswith("_analysis.json"):
            with open(file_path, "r") as f:
                data = json.load(f)
            print(f"  - File contains copyright_holder: {'copyright_holder' in data}")
            print(f"  - File contains license_name: {'license_name' in data}")

        # For the functions JSON file, verify it contains function entries
        elif file_name.endswith("_functions.json"):
            print(f"  - File contains function entries")

        # For the Rust file, check that it contains the expected content
        elif file_name.endswith(".rs"):
            with open(file_path, "r") as f:
                content = f.read()
            print(f"  - Contains fn foo(): {'fn foo()' in content}")
            print(f"  - Contains fn bar(): {'fn bar()' in content}")


if __name__ == "__main__":
    doctest.testmod(verbose=True)
