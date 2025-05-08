from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from src.data_models.license_types import LicenseType


class FunctionInfo(BaseModel):
    """Information about a function extracted from code."""

    name: str = Field(description="The name of the function", examples=["calculate_sum", "processData"])
    arg_count: int = Field(description="The number of arguments the function accepts", ge=0, examples=[0, 1, 2, 3])

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate that the function name is not empty."""
        if not value.strip():
            raise ValueError("Function name cannot be empty")
        return value


class FileAnalysisResult(BaseModel):
    """Result of file analysis, containing all extracted information."""

    file_name: str = Field(description="The name of the analyzed file", examples=["main.py", "app.js"])
    copyright_holder: str = Field(
        description="The copyright holder of the code", examples=["OpenAI", "Anthropic", "Individual Developer"]
    )
    license_name: str = Field(
        description="The name of the license", examples=["MIT License", "GNU GPL v3", "Apache 2.0"]
    )
    license_type: LicenseType = Field(description="The type of the license (permissive, copyleft, etc.)")
    function_count: Optional[int] = Field(
        None, description="The number of functions in the code", ge=0, examples=[2, 5, 10]
    )
    functions: Optional[List[FunctionInfo]] = Field(
        None, description="Detailed information about each function in the code"
    )

    @model_validator(mode="after")
    def validate_functions_count(self) -> "FileAnalysisResult":
        """Validate that function_count matches the length of functions if both are present."""
        if self.functions is not None and self.function_count is not None:
            if len(self.functions) != self.function_count:
                raise ValueError(
                    f"Function count ({self.function_count}) does not match number of functions ({len(self.functions)})"
                )
        return self

    def model_dump(self, **kwargs) -> dict:
        """Convert to a dictionary for JSON serialization."""
        result = super().model_dump(**kwargs)
        # Convert enum to string for better JSON serialization
        if "license_type" in result and result["license_type"] is not None:
            result["license_type"] = result["license_type"].name
        return result
