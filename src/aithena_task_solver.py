"""AITHENA Task Solver implementation (synchronous)."""

import logging

from src.data_models.analysis_models import FileAnalysisResult
from src.data_models.license_types import LicenseType
from src.llm.protocols import LlmClient, LLMClientError
from src.services import (
    CopyrightExtractor,
    FunctionCounter,
    FunctionCounterError,
    FunctionExtractor,
    FunctionExtractorError,
    LicenseDetector,
    ResultSaver,
)


def process_file(
    llm_client: LlmClient, file_name: str, file_content: str, output_dir: str = "results"
) -> tuple[FileAnalysisResult, list[str]]:
    """Process a file according to the AITHENA task requirements.

    This is the main function that implements the logic described in task.md.
    Processing steps:
    1. Detect code language
    2. Extract license type and copyright holder
    3. If license is permissive (MIT, Apache, etc.):
       - Extract function names with argument counts
    4. If license is copyleft (GPL, LGPL, etc.):
       - Count functions
       - If more than 2 functions:
         - Extract function names with argument counts
       - If 2 or fewer functions:
         - Rewrite to Rust
    5. Save analysis results in structured form

    Args:
        llm_client: An implementation of the LlmClient Protocol
        file_name: The name of the file being processed
        file_content: The content of the file to analyze
        output_dir: The directory to save the results to (default is "results")

    Returns:
        A tuple of (FileAnalysisResult, list of saved file paths)

    Raises:
        TaskSolverError: If processing fails
    """
    saved_files = []
    license_detector = LicenseDetector(llm_client)
    function_counter = FunctionCounter(llm_client)
    copyright_extractor = CopyrightExtractor(llm_client)
    function_extractor = FunctionExtractor(llm_client)
    result_saver = ResultSaver()

    license_type, license_name = license_detector.get_license_type(file_content)
    copyright_holder = copyright_extractor.extract_copyright_holder(file_content)

    result = FileAnalysisResult(
        file_name=file_name, copyright_holder=copyright_holder, license_name=license_name, license_type=license_type
    )

    match license_type:
        case LicenseType.PERMISSIVE:
            logging.info("Processing permissive license file: %s", file_name)
            try:
                function_count = function_counter.count_functions(file_content)
                result.function_count = function_count
            except FunctionCounterError as e:
                logging.error("Failed to count functions in %s: %s", file_name, str(e))

            try:
                functions = function_extractor.extract_functions_with_args(file_content)
                result.functions = functions

                # Save function extraction results separately
                if functions:
                    functions_file_path = result_saver.save_to_json(
                        result_data={"file_name": file_name, "functions": [f.model_dump() for f in functions]},
                        output_dir=output_dir,
                        file_name=file_name,
                        suffix="functions",
                    )
                    saved_files.append(functions_file_path)
            except FunctionExtractorError as e:
                logging.error("Failed to extract functions from %s: %s", file_name, str(e))

        case LicenseType.COPYLEFT:
            logging.info("Processing copyleft license file: %s", file_name)
            try:
                function_count = function_counter.count_functions(file_content)
                result.function_count = function_count

                if function_count > 2:
                    # If more than 2 functions: extract function names with arg counts
                    logging.info("File %s has %d functions, extracting function info", file_name, function_count)

                    try:
                        functions = function_extractor.extract_functions_with_args(file_content)
                        result.functions = functions

                        # Save function extraction results separately
                        if functions:
                            functions_file_path = result_saver.save_to_json(
                                result_data={"file_name": file_name, "functions": [f.model_dump() for f in functions]},
                                output_dir=output_dir,
                                file_name=file_name,
                                suffix="functions",
                            )
                            saved_files.append(functions_file_path)
                    except FunctionExtractorError as e:
                        logging.error("Failed to extract functions from %s: %s", file_name, str(e))
                else:
                    # If 2 or fewer functions: rewrite to Rust
                    logging.info("File %s has %d functions, rewriting to Rust", file_name, function_count)

                    try:
                        rust_code = llm_client.rewrite_to_rust(file_content)
                        rust_file_path = result_saver.save_rust_code(file_name, rust_code, output_dir)
                        saved_files.append(rust_file_path)
                    except LLMClientError as e:
                        logging.error("Failed to rewrite %s to Rust: %s", file_name, str(e))
            except FunctionCounterError as e:
                logging.error("Failed to count functions in %s: %s", file_name, str(e))

    # Save the analysis JSON file for all license types
    result_dict = result.model_dump(exclude_none=True)
    json_file_path = result_saver.save_to_json(result_data=result_dict, output_dir=output_dir, file_name=file_name)
    saved_files.append(json_file_path)

    return result, saved_files
