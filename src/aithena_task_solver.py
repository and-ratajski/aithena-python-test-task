"""AITHENA Task Solver implementation.

This module contains the main logic for solving the AITHENA test task as described in task.md.
It coordinates the use of various services to analyze Python files according to their licenses.
"""
from src.data_models.analysis_models import FileAnalysisResult
from src.data_models.license_types import LicenseType
from src.llm.protocols import LlmClient
from src.services.code_analyzer import CopyrightExtractor, FunctionExtractor
from src.services.function_counter import FunctionCounter
from src.services.license_detector import LicenseDetector
from src.services.result_handler import ResultSaver


class TaskSolverError(Exception):
    """Exception raised for errors in the task solver."""
    pass


def process_file(llm_client: LlmClient, file_name: str, file_content: str, output_dir: str = "results") -> tuple[FileAnalysisResult, list[str]]:
    """Process a file according to the AITHENA task requirements.
    
    This is the main function that implements the logic described in task.md.
    
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
    
    try:
        # Initialize services
        license_detector = LicenseDetector(llm_client)
        function_counter = FunctionCounter(llm_client)
        copyright_extractor = CopyrightExtractor(llm_client)
        function_extractor = FunctionExtractor(llm_client)
        result_saver = ResultSaver()
        
        # Detect license
        license_type, license_name = license_detector.get_license_type(file_content)
        
        # Extract copyright holder
        copyright_holder = copyright_extractor.extract_copyright_holder(file_content)
        
        # Initialize result
        result = FileAnalysisResult(
            file_name=file_name,
            copyright_holder=copyright_holder,
            license_name=license_name,
            license_type=license_type
        )
        
        # Apply logic based on license type
        if license_type == LicenseType.PERMISSIVE:
            # For permissive licenses: extract function names with arg counts
            result.functions = function_extractor.extract_functions_with_args(file_content)
        
        elif license_type == LicenseType.COPYLEFT:
            # For copyleft licenses: count functions first
            function_count = function_counter.count_functions(file_content)
            result.function_count = function_count
            
            if function_count > 2:
                # If more than 2 functions: extract function names with arg counts
                result.functions = function_extractor.extract_functions_with_args(file_content)
            else:
                # If 2 or fewer functions: rewrite to Rust
                rust_code = llm_client.rewrite_to_rust(file_content)
                result.rust_code = rust_code
                
                # Save Rust code
                rust_file_path = result_saver.save_rust_code(file_name, rust_code, output_dir)
                saved_files.append(rust_file_path)
        
        # For all cases: save structured data
        result_dict = {
            "file_name": result.file_name,
            "copyright_holder": result.copyright_holder,
            "license_name": result.license_name,
            "license_type": result.license_type.name,
        }
        
        # Add function information if available
        if result.function_count is not None:
            result_dict["function_count"] = result.function_count
            
        if result.functions is not None:
            result_dict["functions"] = [
                {"name": f.name, "arg_count": f.arg_count}
                for f in result.functions
            ]
        
        json_file_path = result_saver.save_to_json(
            result_data=result_dict,
            output_dir=output_dir,
            file_name=file_name
        )
        saved_files.append(json_file_path)
        
        return result, saved_files
        
    except Exception as e:
        raise TaskSolverError(f"Failed to process file {file_name}: {str(e)}")