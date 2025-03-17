#!/usr/bin/env python
"""
Script to initialize the database tables in Neon PostgreSQL.
Make sure to set the DATABASE_URL environment variable before running this script.

Usage:
    python init_neon_db.py [--force]
"""

import argparse
import os
import sys

# Add the parent directory to sys.path to import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db
from backend.models import Base, Conversation, Lead, Message


def main():
    parser = argparse.ArgumentParser(
        description="Initialize database tables in Neon PostgreSQL"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreate all tables (WARNING: This will delete all data)",
    )
    args = parser.parse_args()

    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("ERROR: DATABASE_URL environment variable is not set.")
        print("Please set it to your Neon PostgreSQL connection string.")
        print(
            "Example: export DATABASE_URL=postgres://user:password@hostname:port/database"
        )
        sys.exit(1)

    try:
        print(f"Initializing database tables (force={args.force})...")
        init_db(force_create_tables=args.force)
        print("Database tables initialized successfully.")

        # Print the models that were created
        print("\nCreated tables for the following models:")
        for model in [Lead, Conversation, Message]:
            print(f"  - {model.__tablename__}")

        print("\nDatabase setup complete!")
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
