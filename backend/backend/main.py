"""
Database Reactivation Project
Main application entry point
"""

import logging
import os

import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)

logger = logging.getLogger(__name__)


def main():
    """Run the application."""
    try:
        # Check for required environment variables
        required_vars = [
            "OPENAI_API_KEY",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
            "BOOKING_LINK",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            logger.error(
                "Please set these variables in a .env file or in your environment."
            )
            return

        # Start the API server
        logger.info("Starting Database Reactivation API server")

        # Import the API module
        from backend.api import app

        # Run the server
        uvicorn.run(
            "backend.api:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            reload=os.getenv("ENV", "development") == "development",
        )

    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        raise


if __name__ == "__main__":
    main()
