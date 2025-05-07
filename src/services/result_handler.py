"""Result handler implementation.

This module contains functionality for saving analysis results to various file formats.
"""
import json
import os
from pathlib import Path
from typing import Dict


class ResultHandlerError(Exception):
    """Exception raised for errors in result handling."""
    pass


class ResultSaver:
    """Saves analysis results to various file formats."""
    
    @staticmethod
    def save_to_json(result_data: Dict, output_dir: str, file_name: str, suffix: str = "analysis") -> str:
        """Save analysis result to a JSON file.
        
        Args:
            result_data: The data to save as a dictionary
            output_dir: The directory to save the result to
            file_name: The base name for the output file
            suffix: Optional suffix to add to the output file name
            
        Returns:
            The path to the saved file
            
        Raises:
            ResultHandlerError: If saving fails
        """
        # Create directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create output file path
        file_name_stem = Path(file_name).stem
        output_file = os.path.join(output_dir, f"{file_name_stem}_{suffix}.json")
        
        try:
            with open(output_file, 'w') as f:
                json.dump(result_data, f, indent=2)
            return output_file
        except Exception as e:
            raise ResultHandlerError(f"Failed to save result to JSON: {str(e)}")
    
    @staticmethod
    def save_text_file(content: str, output_dir: str, file_name: str, suffix: str, extension: str) -> str:
        """Save text content to a file.
        
        Args:
            content: The text content to save
            output_dir: The directory to save the result to
            file_name: The base name for the output file
            suffix: Suffix to add to the output file name
            extension: File extension to use
            
        Returns:
            The path to the saved file
            
        Raises:
            ResultHandlerError: If saving fails
        """
        # Create directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create output file path
        file_name_stem = Path(file_name).stem
        output_file = os.path.join(output_dir, f"{file_name_stem}_{suffix}.{extension}")
        
        try:
            with open(output_file, 'w') as f:
                f.write(content)
            return output_file
        except Exception as e:
            raise ResultHandlerError(f"Failed to save text file: {str(e)}")
        
    @staticmethod
    def save_rust_code(file_name: str, rust_code: str, output_dir: str) -> str:
        """Save Rust code to a file.
        
        Args:
            file_name: The original file name
            rust_code: The Rust code to save
            output_dir: The directory to save the code to
            
        Returns:
            The path to the saved file
            
        Raises:
            ResultHandlerError: If saving fails
        """
        return ResultSaver.save_text_file(
            content=rust_code,
            output_dir=output_dir,
            file_name=file_name,
            suffix="rust_functions",
            extension="rs"
        )