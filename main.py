"""Main entry point for the license analysis tool."""

import os
from dotenv import load_dotenv


def main() -> None:
    """Execute the main application flow."""
    # Load environment variables
    load_dotenv()
    
    # Validate environment
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required.")
        print("Please create a .env file based on .env.example")
        return
    
    print("Starting license analysis...")
    # TODO: Implement main application logic
    
    print("Analysis completed!")


if __name__ == "__main__":
    main()