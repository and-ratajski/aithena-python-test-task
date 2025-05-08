"""AITHENA Python Test Task entry point (asynchronous)."""
import argparse
import asyncio
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

from src.aithena_task_solver import process_file
from src.data_models.analysis_models import FileAnalysisResult
from src.llm import LlmClient, ProviderType, get_llm_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


async def process_file_async(
    llm_client: LlmClient, file_path: Path, output_dir: str = "results"
) -> tuple[FileAnalysisResult, list[str]]:
    """Asynchronous wrapper for processing a single file."""
    file_name = file_path.name
    loop = asyncio.get_event_loop()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = await loop.run_in_executor(None, f.read)
    except Exception as e:
        logging.error("Failed to read file %s: %s", file_path, str(e))
        raise

    # Process file in a ThreadPoolExecutor to avoid blocking the event loop
    process_func = partial(process_file, llm_client, file_name, file_content, output_dir)
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, process_func)

    return result


async def process_files_async(
    llm_client: LlmClient, data_dir: str = "data", output_dir: str = "results", file_pattern: str = "*.py"
) -> list[tuple[FileAnalysisResult, list[str]]]:
    """Process all files in the data directory concurrently."""
    # Get all files matching the pattern
    data_path = Path(data_dir)
    if not data_path.exists() or not data_path.is_dir():
        raise ValueError("Data directory %s does not exist or is not a directory" % data_dir)

    files = list(data_path.glob(file_pattern))
    if not files:
        logging.warning("No files found matching pattern %s in %s", file_pattern, data_dir)
        return []

    # Process files concurrently
    logging.info("Processing %d files from %s", len(files), data_dir)
    tasks = [process_file_async(llm_client, file_path, output_dir) for file_path in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results


async def main(model_provider: ProviderType, data_dir: str, output_dir: str) -> None:
    """
    Main async entry point for the application.

    Args:
        model_provider: The model provider to use ("anthropic" or "openai")
        data_dir: Directory containing files to process
        output_dir: Directory to save results to
    """
    try:
        llm_client = get_llm_client(model_provider)
        logging.info("Using %s LLM client", model_provider)

        results = await process_files_async(llm_client, data_dir, output_dir)

        num_files_saved = sum(len(saved_files) for _, saved_files in results)
        logging.info("Successfully processed %d files, saved %d result files", len(results), num_files_saved)
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        raise


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AITHENA Python Test Task")
    parser.add_argument(
        "--provider",
        type=str,
        choices=["anthropic", "openai"],
        default="anthropic",
        help="Model provider to use (default: anthropic)",
    )
    parser.add_argument(
        "--data-dir", type=str, default="data", help="Directory containing files to process (default: data)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="results", help="Directory to save results to (default: results)"
    )
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the async main function
    asyncio.run(main(args.provider, args.data_dir, args.output_dir))
