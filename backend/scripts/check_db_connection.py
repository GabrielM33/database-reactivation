#!/usr/bin/env python
"""
Script to check database connection and list existing tables.
Make sure to set the DATABASE_URL environment variable before running this script.

Usage:
    python check_db_connection.py
"""

import os
import sys
from urllib.parse import urlparse

# Add the parent directory to sys.path to import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def main():
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        sys.exit(1)

    # Handle Postgres URL format for SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Determine database type
    is_postgres = database_url.startswith("postgresql://")
    db_type = "PostgreSQL" if is_postgres else "SQLite"

    # Parse the URL for connection info
    if is_postgres:
        parsed_url = urlparse(database_url)
        host = parsed_url.hostname
        port = parsed_url.port
        dbname = parsed_url.path[1:]  # Remove leading '/'
        username = parsed_url.username
        print(f"Checking connection to {db_type} database:")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  Database: {dbname}")
        print(f"  Username: {username}")
    else:
        print(f"Checking connection to {db_type} database")

    try:
        # Create an engine and connect
        engine = create_engine(database_url, echo=False)
        with engine.connect() as connection:
            # Get database version
            if is_postgres:
                version_query = text("SELECT version();")
            else:
                version_query = text("SELECT sqlite_version();")

            version = connection.execute(version_query).scalar()
            print(f"\nSuccessfully connected to {db_type}!")
            print(f"Database version: {version}")

            # List tables
            if is_postgres:
                table_query = text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
                )
            else:
                table_query = text("SELECT name FROM sqlite_master WHERE type='table';")

            tables = [row[0] for row in connection.execute(table_query).fetchall()]

            if tables:
                print(f"\nFound {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table}")

                    # For each table, count rows
                    try:
                        count_query = text(f"SELECT COUNT(*) FROM {table};")
                        count = connection.execute(count_query).scalar()
                        print(f"    ({count} rows)")
                    except:
                        print("    (unable to count rows)")
            else:
                print("\nNo tables found in the database.")
                print(
                    "You may need to initialize tables using the init_neon_db.py script."
                )

    except SQLAlchemyError as e:
        print(f"\nERROR: Failed to connect to the database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
