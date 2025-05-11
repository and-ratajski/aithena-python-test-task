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
from src.agents.utils import configure_pydantic_ai, ANTHROPIC, OPENAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


async def process_files_async(input_dir: str, output_dir: str, max_workers: int = 3) -> list[FileAnalysisResult]:
    """Process multiple files in parallel using a thread pool.

    Limits the maximum number of concurrent requests to stay within API rate limits.

    Args:
        input_dir: Directory containing files to process
        output_dir: Directory to save results to
        max_workers: Maximum number of concurrent workers

    Returns:
        List of FileAnalysisResult objects
    """
    input_path = Path(input_dir)
    files = list(input_path.glob("*.py"))
    
    if not files:
        logging.warning(f"No Python files found in {input_dir}")
        return []
    logging.info(f"Found {len(files)} Python files to process")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Function to process a single file
    def process_file_wrapper(file_path: Path) -> FileAnalysisResult:
        file_name = file_path.name
        with open(file_path, "r") as f:
            file_content = f.read()
        
        logging.info(f"Processing {file_name}...")
        result, saved_files = process_file(file_name, file_content, output_dir)
        logging.info(f"Completed {file_name}, saved {len(saved_files)} files")
        return result
    
    # Process files in parallel with limited concurrency
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a list of tasks using ThreadPoolExecutor
        tasks = [
            loop.run_in_executor(executor, partial(process_file_wrapper, file_path))
            for file_path in files
        ]
        results = await asyncio.gather(*tasks)
    
    return results


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AITHENA Python Test Task")
    parser.add_argument("--input", "-i", default="data", help="Directory containing Python files to process")
    parser.add_argument("--output", "-o", default="results", help="Directory to save results to")
    parser.add_argument("--provider", "-p", default=ANTHROPIC, choices=[ANTHROPIC, OPENAI], 
                        help="LLM provider to use")
    parser.add_argument("--max-workers", "-w", type=int, default=2,
                        help="Maximum number of concurrent workers")
    return parser.parse_args()


async def main() -> None:
    """Main entry point for the AITHENA Python Test Task."""
    args = parse_args()

    configure_pydantic_ai(args.provider)
    results = await process_files_async(args.input, args.output, args.max_workers)

    logging.info(f"Processed {len(results)} files")
    logging.info("Done!")


if __name__ == "__main__":
    asyncio.run(main())