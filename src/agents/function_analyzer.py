import logging
from typing import List

from pydantic_ai import Agent

from src.agents.utils import get_model_from_settings
from src.data_models.analysis_models import FunctionInfo
from src.data_models.response_models import FunctionCountInfo

FUNCTION_COUNT_SYSTEM_PROMPT = """You are an expert code analyzer specialized in identifying functions in code.
Your task is to count the exact number of UNIQUE function definitions in the provided code.
Focus only on function counting. Be precise and return only the count as a number.
If a function with the same name is defined multiple times, count it only ONCE.

Analyze the following code and count the number of UNIQUE function definitions it contains.
If a function is defined multiple times with the same name, count it only ONCE.
Respond ONLY with a JSON object with a single field "function_count" which contains the integer number of unique functions found.

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
Response: {"function_count": 2}  # Only count unique function names: foo and bar
"""


FUNCTION_EXTRACTION_SYSTEM_PROMPT = """You are an expert code analyzer specialized in identifying functions in code.
Your task is to extract all function names and count the number of arguments for each function.
Include class methods but exclude built-in special methods (like __init__, __str__, etc.) unless explicitly required.
Be precise and focus only on the function extraction task.

Analyze the following code and extract all function names along with the number of arguments each function takes.
Count only real parameters, not self or cls for methods.
Include standalone functions and class methods but exclude built-in special methods (like __init__, __str__, etc.) unless explicitly asked.

Respond ONLY with a JSON array where each element is an object with two fields:
1. "name": The function name as a string
2. "arg_count": The number of arguments as an integer

Examples:
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
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}, {"name": "multiply", "arg_count": 2}]

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
Response: [{"name": "add", "arg_count": 2}, {"name": "subtract", "arg_count": 2}, {"name": "multiply", "arg_count": 2}]
"""


# Create Agents for function analysis
function_count_agent = Agent(
    output_type=FunctionCountInfo,
    system_prompt=FUNCTION_COUNT_SYSTEM_PROMPT,
    name="function_count_agent",
    defer_model_check=True,
)

function_extractor_agent = Agent(
    output_type=List[FunctionInfo],
    system_prompt=FUNCTION_EXTRACTION_SYSTEM_PROMPT,
    name="function_extractor_agent",
    defer_model_check=True,
)


def _enrich_count_prompt(file_content: str) -> str:
    """Enrich the function count prompt with file content."""
    return f"""
---
Now count the unique functions in this code:
```
{file_content}
```
"""


def _enrich_extraction_prompt(file_content: str) -> str:
    """Enrich the function extraction prompt with file content."""
    return f"""
---
Now extract the functions from this code:
```
{file_content}
```
"""


def count_functions(file_content: str) -> FunctionCountInfo:
    """Count the number of unique functions defined in the code."""
    try:
        # Get model from settings and run the agent
        model = get_model_from_settings()
        result = function_count_agent.run_sync(_enrich_count_prompt(file_content), model=model)
        return result.output
    except Exception as e:
        # Log the error and return zero functions
        logging.error("Error using function count agent: %s", str(e))
        return FunctionCountInfo(function_count=0)


def extract_functions_with_args(file_content: str) -> List[FunctionInfo]:
    """Extract all function names and the number of arguments they take."""
    try:
        model = get_model_from_settings()
        result = function_extractor_agent.run_sync(_enrich_extraction_prompt(file_content), model=model)
        return result.output
    except Exception as e:
        logging.error("Error using function extractor agent: %s", str(e))
        return []
