#!/usr/bin/env python3
"""Setup test database."""

from sqlalchemy import create_engine, text
from app.core.config import settings

def main():
    # Connect to postgres database to create test database
    db_url = settings.DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Check if test database exists
        result = conn.execute(text(
            "SELECT 1 FROM pg_database WHERE datname = 'samadhanx_test'"
        )).fetchone()
        
        if not result:
            print("Creating test database...")
            conn.execute(text("CREATE DATABASE samadhanx_test"))
            print("✓ Test database created")
        else:
            print("✓ Test database already exists")
    
    # Connect to test database and enable pgvector
    test_db_url = settings.DATABASE_URL.rsplit('/', 1)[0] + '/samadhanx_test'
    test_engine = create_engine(test_db_url)
    
    with test_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("✓ pgvector extension enabled on test database")

if __name__ == "__main__":
    main()
