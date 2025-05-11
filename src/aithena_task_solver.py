"""AITHENA Task Solver implementation using Pydantic AI."""

import logging
from typing import List, Optional

from src.agents.code_translator import rewrite_to_rust
from src.agents.copyright_extractor import extract_copyright_holder
from src.agents.function_analyzer import count_functions, extract_functions_with_args

# Import refactored agent functions
from src.agents.license_detector import detect_license
from src.data_models.analysis_models import FileAnalysisResult
from src.data_models.response_models import LicenseType
from src.services import ResultSaver


def process_file(
    file_name: str, file_content: str, output_dir: str = "results"
) -> tuple[FileAnalysisResult, list[str]]:
    """Process a file according to the AITHENA task requirements.

    This is the main function that implements the logic described in task.md.
    Processing steps:
    1. Extract license type and copyright holder
    2. If license is permissive (MIT, Apache, etc.):
       - Extract function names with argument counts
    3. If license is copyleft (GPL, LGPL, etc.):
       - Count functions
       - If more than 2 functions:
         - Extract function names with argument counts
       - If 2 or fewer functions:
         - Rewrite to Rust
    4. Save analysis results in structured form

    Args:
        file_name: The name of the file being processed
        file_content: The content of the file to analyze
        output_dir: The directory to save the results to (default is "results")

    Returns:
        A tuple of (FileAnalysisResult, list of saved file paths)
    """
    saved_files = []
    result_saver = ResultSaver()

    # Extract license information
    try:
        license_info = detect_license(file_content)
        # Use the license_type directly as it's now an enum
        license_type = license_info.license_type
        license_name = license_info.license_name
    except Exception as e:
        logging.error("Failed to detect license in %s: %s", file_name, str(e))
        license_type = LicenseType.UNKNOWN
        license_name = "Unknown License"

    # Extract copyright holder
    try:
        copyright_info = extract_copyright_holder(file_content)
        copyright_holder = copyright_info.copyright_holder
    except Exception as e:
        logging.error("Failed to extract copyright holder from %s: %s", file_name, str(e))
        copyright_holder = "Unknown"

    # Create the result object
    result = FileAnalysisResult(
        file_name=file_name, copyright_holder=copyright_holder, license_name=license_name, license_type=license_type
    )

    # Process based on license type
    match license_type:
        case LicenseType.PERMISSIVE:
            logging.info("Processing permissive license file: %s", file_name)

            # Count functions
            try:
                function_count_info = count_functions(file_content)
                result.function_count = function_count_info.function_count
            except Exception as e:
                logging.error("Failed to count functions in %s: %s", file_name, str(e))

            # Extract function information
            try:
                function_list = extract_functions_with_args(file_content)
                result.functions = function_list

                # Save function extraction results separately
                if function_list:
                    functions_file_path = result_saver.save_to_json(
                        result_data={"file_name": file_name, "functions": [f.model_dump() for f in function_list]},
                        output_dir=output_dir,
                        file_name=file_name,
                        suffix="functions",
                    )
                    saved_files.append(functions_file_path)
            except Exception as e:
                logging.error("Failed to extract functions from %s: %s", file_name, str(e))

        case LicenseType.COPYLEFT:
            logging.info("Processing copyleft license file: %s", file_name)

            # Count functions
            try:
                function_count_info = count_functions(file_content)
                result.function_count = function_count_info.function_count

                if result.function_count > 2:
                    # If more than 2 functions: extract function information
                    logging.info("File %s has %d functions, extracting function info", file_name, result.function_count)

                    try:
                        function_list = extract_functions_with_args(file_content)
                        result.functions = function_list

                        # Save function extraction results separately
                        if function_list:
                            functions_file_path = result_saver.save_to_json(
                                result_data={
                                    "file_name": file_name,
                                    "functions": [f.model_dump() for f in function_list],
                                },
                                output_dir=output_dir,
                                file_name=file_name,
                                suffix="functions",
                            )
                            saved_files.append(functions_file_path)
                    except Exception as e:
                        logging.error("Failed to extract functions from %s: %s", file_name, str(e))
                else:
                    # If 2 or fewer functions: rewrite to Rust
                    logging.info("File %s has %d functions, rewriting to Rust", file_name, result.function_count)

                    try:
                        rust_translation = rewrite_to_rust(file_content)
                        rust_file_path = result_saver.save_rust_code(file_name, rust_translation.rust_code, output_dir)
                        saved_files.append(rust_file_path)
                    except Exception as e:
                        logging.error("Failed to rewrite %s to Rust: %s", file_name, str(e))
            except Exception as e:
                logging.error("Failed to count functions in %s: %s", file_name, str(e))

    # Save the analysis JSON file for all license types
    result_dict = result.model_dump(exclude_none=True)
    json_file_path = result_saver.save_to_json(result_data=result_dict, output_dir=output_dir, file_name=file_name)
    saved_files.append(json_file_path)

    return result, saved_files
