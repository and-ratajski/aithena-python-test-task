# AITHENA License Analysis Tool

Python tool that analyzes source files to extract license information and conditionally process them based on license type.

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

# Run example tests (semi-integration)
pytest examples
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
  -e LLM_PROVIDER=anthropic \
  -e ANTHROPIC_MODEL_NAME=claude-3-7-sonnet-20250219 \
  -e ANTHROPIC_API_KEY=your_key_here \
  aithena-analyzer
```