# AITHENA License Analysis Tool

Python tool that analyzes source files to extract license information and conditionally process them based on license type. Uses Pydantic AI for type-safe LLM interactions.

## Setup

```bash
# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (production only)
pip install .

# Install with development dependencies
pip install ".[dev]"

# Configure API keys
cp .env.example .env
# Edit .env to add your API keys
```

## Running the Application

```bash
# Run with default settings (Anthropic model)
python main_async.py

# Specify model provider
python main_async.py --provider anthropic
python main_async.py --provider openai

# Specify custom input/output directories
python main_async.py --data-dir custom_data --output-dir custom_results
```

## Testing

```bash
# Run unit tests
pytest tests/unit

# Run example tests (semi-integration, slow)
pytest examples

# Altogether (with coverage)
pytest
```

## Docker

```bash
# Build Docker image
docker build -t aithena-analyzer .

# Run container (with default settings)
docker run -it --rm aithena-analyzer

# Mount custom data and results directories and specify environment variables
docker run -it --rm \
  -v $(pwd)/custom_results:/app/results \
  -e ANTHROPIC_MODEL_NAME=claude-3-7-sonnet-20250219 \
  -e ANTHROPIC_API_KEY=your_key_here \
  aithena-analyzer
```

## Pydantic AI Integration

This project uses Pydantic AI to interact with Large Language Models in a type-safe way, offering:

1. **Type Safety**: All LLM responses are validated against Pydantic models, ensuring proper structure.
2. **Error Handling**: Robust error handling with fallbacks for common failure scenarios.
3. **Flexible Provider Support**: Easy switching between different LLM providers (Anthropic, OpenAI).
4. **Declarative Approach**: Clean code via declarative models and function definitions.

### Architecture

The application is structured into several key components:

1. **AI Services**:
   - Uses Pydantic AI's `Agent` class to create services for tasks like license detection and code translation
   - Each service has a corresponding Pydantic model for type-safe responses
   - Includes fallback mechanisms for testing environments

2. **Task Solver**:
   - Orchestrates the execution of AI services based on license type
   - Applies business rules to determine which operations to perform
   - Manages results storage and output formatting

3. **Configuration**:
   - Dynamic configuration of Pydantic AI based on selected provider
   - Environment variable integration for API keys and model settings

4. **Async Processing**:
   - Asynchronous file processing for optimal performance
   - Thread pools to avoid blocking the event loop during CPU-intensive tasks

### Benefits of Pydantic AI

- **Reduced Boilerplate**: No need for custom validation and parsing of LLM responses
- **Improved Reliability**: Structured responses with proper validation
- **Better Testing**: Easier to mock and test LLM interactions
- **Developer Experience**: More intuitive and type-safe API for LLM interactions