FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml README.md ./

# Install only required dependencies (no dev dependencies)
RUN pip install --no-cache-dir .

COPY src/ ./src/
COPY data/ ./data/
COPY main_async.py .

# Create results directory
RUN mkdir -p results

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main_async.py", "--provider", "anthropic"]