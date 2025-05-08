"""Function counter implementation.

This module contains functionality for counting functions in code files using LLM.
"""
import json

from src.data_models import FunctionInfo
from src.llm.protocols import LlmClient, LLMClientError
from src.services.language_detector import LanguageDetector, ProgrammingLanguage


class FunctionCounterError(Exception):
    """Exception raised for errors in the function counter."""
    pass

class FunctionExtractorError(Exception):
    """Exception raised for errors in the function extractor."""
    pass


class FunctionCounter:
    """Counts functions in code files using LLM."""
    
    def __init__(self, llm_client: LlmClient) -> None:
        """Initialize the function counter with an LLM client.
        
        Args:
            llm_client: An implementation of the LlmClient Protocol
        """
        self.llm_client = llm_client
        self.language_detector = LanguageDetector(llm_client)
    
    def count_functions(self, file_content: str) -> int:
        """Count the number of functions in a file using LLM.
        
        Args:
            file_content: The content of the file to analyze
            
        Returns:
            The number of functions in the file
            
        Raises:
            FunctionCounterError: If counting functions fails
        """
        try:
            # Detect language to provide better examples
            detected_language = self.language_detector.detect_language(file_content)
            
            # Use LLM for function counting
            return self._count_functions_with_llm(file_content, detected_language)
            
        except Exception as e:
            # Ensure all exceptions are properly wrapped
            if isinstance(e, FunctionCounterError):
                raise  # Re-raise FunctionCounterError directly
            else:
                # Wrap any other exception in FunctionCounterError
                raise FunctionCounterError(f"Error counting functions: {str(e)}")
    
    def _count_functions_with_llm(self, file_content: str, language: ProgrammingLanguage = None) -> int:
        """Count functions using the LLM, with language-specific prompting if language is known.
        
        Args:
            file_content: The content of the file to analyze
            language: The detected programming language, if known
            
        Returns:
            The number of functions in the file
            
        Raises:
            FunctionCounterError: If counting functions fails
        """
        system_prompt = """You are an expert code analyzer specialized in identifying functions in code.
Your task is to count the exact number of UNIQUE function definitions in the provided code.
Focus only on function counting. Be precise and return only the count as a number.
If a function with the same name is defined multiple times, count it only ONCE.
"""
        
        language_specific_examples = ""
        if language == ProgrammingLanguage.PYTHON:
            language_specific_examples = """
Examples:
---
Code: 
```python
def add(a, b):
    return a + b
    
def subtract(a, b):
    return a - b
```
Response: {"function_count": 2}

---
Code:
```python
class Calculator:
    def add(self, a, b):
        return a + b
        
    def subtract(self, a, b):
        return a - b
        
def multiply(a, b):
    return a * b
```
Response: {"function_count": 3}
"""
        elif language == ProgrammingLanguage.JAVASCRIPT:
            language_specific_examples = """
Examples:
---
Code: 
```javascript
function add(a, b) {
    return a + b;
}

const subtract = (a, b) => {
    return a - b;
}

// This is a method in an object
const calculator = {
    multiply: function(a, b) {
        return a * b;
    }
};
```
Response: {"function_count": 3}

---
Code:
```javascript
class Calculator {
    add(a, b) {
        return a + b;
    }
    
    subtract(a, b) {
        return a - b;
    }
}

function multiply(a, b) {
    return a * b;
}
```
Response: {"function_count": 3}
"""
        elif language == ProgrammingLanguage.JAVA:
            language_specific_examples = """
Examples:
---
Code: 
```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    private double subtract(double a, double b) {
        return a - b;
    }
    
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
```
Response: {"function_count": 3}
"""
        elif language == ProgrammingLanguage.RUST:
            language_specific_examples = """
Examples:
---
Code: 
```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn subtract(a: i32, b: i32) -> i32 {
    a - b
}

impl Calculator {
    fn multiply(&self, a: i32, b: i32) -> i32 {
        a * b
    }
}
```
Response: {"function_count": 3}
"""
        else:
            # Generic examples for unknown language
            language_specific_examples = """
Examples:
---
Code: 
```
def add(a, b):
    return a + b
    
def subtract(a, b):
    return a - b
```
Response: {"function_count": 2}

---
Code:
```
function add(a, b) {
    return a + b;
}

const subtract = (a, b) => {
    return a - b;
}
```
Response: {"function_count": 2}

---
Code:
```
public int add(int a, int b) {
    return a + b;
}

private double subtract(double a, double b) {
    return a - b;
}
```
Response: {"function_count": 2}
"""
        
        prompt = f"""Analyze the following code and count the number of UNIQUE function definitions it contains.
If a function is defined multiple times with the same name, count it only ONCE.
Respond ONLY with a JSON object with a single field "function_count" which contains the integer number of unique functions found.

{language_specific_examples}

---
Here's an example with duplicate function definitions:
```python
def foo():
    print("foo version 1")
    
def bar():
    print("bar")
    
def foo():  # This is a duplicate definition of foo
    print("foo version 2")
```
Response: {{"function_count": 2}}  # Only count unique function names: foo and bar

---
Now count the unique functions in this code:
```
{file_content}
```
"""
        
        try:
            response = self.llm_client.generate_response(prompt, system_prompt)
            
            # Parse the response - we expect a JSON object
            try:
                result = json.loads(response)
                function_count = result.get("function_count")
                
                # Validate the response
                if function_count is None or not isinstance(function_count, int) or function_count < 0:
                    raise FunctionCounterError("Invalid function count returned by LLM")
                
                return function_count
                
            except json.JSONDecodeError as e:
                # If the response isn't valid JSON, raise an error
                raise FunctionCounterError(f"Failed to parse LLM response as JSON: {str(e)}")
                
        except LLMClientError as e:
            # If LLM request fails, raise a specific error
            raise FunctionCounterError(f"LLM request failed: {str(e)}")
        except Exception as e:
            # Catch any other unexpected errors
            raise FunctionCounterError(f"Unexpected error counting functions: {str(e)}")


class FunctionExtractor:
    """Extracts function information from code files using LLM with language-aware capabilities."""

    def __init__(self, llm_client: LlmClient) -> None:
        """Initialize the function extractor with an LLM client.

        Args:
            llm_client: An implementation of the LlmClient Protocol
        """
        self.llm_client = llm_client
        self.language_detector = LanguageDetector(llm_client)

    def extract_functions_with_args(self, file_content: str) -> list[FunctionInfo]:
        """Extract function names and argument counts from code using LLM.
        Automatically detects the programming language and adjusts extraction accordingly.

        Args:
            file_content: The content of the file to analyze

        Returns:
            A list of FunctionInfo objects with function names and argument counts

        Raises:
            FunctionExtractorError: If extracting function information fails
        """
        # Detect the programming language
        detected_language = self.language_detector.detect_language(file_content)

        # Create language-specific system prompt
        system_prompt = """You are an expert code analyzer specialized in identifying functions in code.
Your task is to extract all function names and count the number of arguments for each function.
Include class methods but exclude built-in special methods (like __init__, __str__, etc.) unless explicitly required.
Be precise and focus only on the function extraction task.
"""

        language_specific_examples = self._get_language_examples(detected_language)

        prompt = f"""Analyze the following code and extract all function names along with the number of arguments each function takes.
Count only real parameters, not self or cls for methods.
Include standalone functions and class methods but exclude built-in special methods (like __init__, __str__, etc.) unless explicitly asked.

Respond ONLY with a JSON array where each element is an object with two fields:
1. "name": The function name as a string
2. "arg_count": The number of arguments as an integer

{language_specific_examples}

---
Now extract the functions from this code:
```
{file_content}
```
"""

        try:
            response = self.llm_client.generate_response(prompt, system_prompt)

            # Parse the response - we expect a JSON array
            try:
                result = json.loads(response)

                # Validate the response
                if not isinstance(result, list):
                    raise FunctionExtractorError("Invalid function information returned by LLM")

                functions = []
                for item in result:
                    name = item.get("name")
                    arg_count = item.get("arg_count")

                    if (name is None or not isinstance(name, str) or
                            arg_count is None or not isinstance(arg_count, int) or arg_count < 0):
                        raise FunctionExtractorError("Invalid function information format")

                    functions.append(FunctionInfo(name=name, arg_count=arg_count))

                return functions

            except json.JSONDecodeError as e:
                # If the response isn't valid JSON, raise an error
                raise FunctionExtractorError(f"Failed to parse LLM response as JSON: {str(e)}")

        except Exception as e:
            # Catch any errors
            raise FunctionExtractorError(f"Error extracting function information: {str(e)}")

    def _get_language_examples(self, language: ProgrammingLanguage) -> str:
        """Get language-specific examples for the LLM prompt.

        Args:
            language: The detected programming language

        Returns:
            A string with language-specific examples
        """
        if language == ProgrammingLanguage.PYTHON:
            return """Examples:
---
Code: 
```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
```
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}]

---
Code:
```python
class Calculator:
    def __init__(self, initial=0):
        self.value = initial

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

def multiply(a, b):
    return a * b
```
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}, {"name": "multiply", "arg_count": 2}]"""

        elif language == ProgrammingLanguage.JAVASCRIPT:
            return """Examples:
---
Code: 
```javascript
function add(a, b) {
    return a + b;
}

const subtract = (a, b) => {
    return a - b;
}

// This is a method in an object
const calculator = {
    multiply: function(a, b) {
        return a * b;
    }
};
```
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}, {"name": "multiply", "arg_count": 2}]

---
Code:
```javascript
class Calculator {
    constructor(initial = 0) {
        this.value = initial;
    }

    add(a, b) {
        return a + b;
    }

    subtract(a, b) {
        return a - b;
    }
}

function multiply(a, b) {
    return a * b;
}

const divide = (a, b) => a / b;
```
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}, {"name": "multiply", "arg_count": 2}, {"name": "divide", "arg_count": 2}]"""

        elif language == ProgrammingLanguage.JAVA:
            return """Examples:
---
Code: 
```java
public class Calculator {
    private int value;

    public Calculator(int initial) {
        this.value = initial;
    }

    public int add(int a, int b) {
        return a + b;
    }

    private double subtract(double a, double b) {
        return a - b;
    }

    public static int multiply(int a, int b) {
        return a * b;
    }
}
```
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}, {"name": "multiply", "arg_count": 2}]"""

        elif language == ProgrammingLanguage.RUST:
            return """Examples:
---
Code: 
```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn subtract(a: i32, b: i32) -> i32 {
    a - b
}

struct Calculator {
    value: i32,
}

impl Calculator {
    fn new(initial: i32) -> Self {
        Calculator { value: initial }
    }

    fn multiply(&self, a: i32, b: i32) -> i32 {
        a * b
    }

    fn divide(&self, a: i32, b: i32) -> i32 {
        a / b
    }
}
```
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}, {"name": "multiply", "arg_count": 2}, {"name": "divide", "arg_count": 2}]"""

        else:
            return """Examples:
---
Code: 
```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
```
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}]

---
Code:
```javascript
function add(a, b) {
    return a + b;
}

const subtract = (a, b) => {
    return a - b;
}
```
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}]"""