#!/usr/bin/env python3
"""Check database connectivity and pgvector extension."""

from sqlalchemy import create_engine, text
from app.core.config import settings

def main():
    print("Checking database connection...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check PostgreSQL version
        result = conn.execute(text("SELECT version()")).fetchone()
        print(f"✓ PostgreSQL: {result[0][:70]}")
        
        # Check pgvector extension
        result = conn.execute(text(
            "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"
        )).fetchone()
        
        if result:
            print(f"✓ pgvector extension: v{result[1]}")
        else:
            print("⚠ pgvector extension not installed")
            print("  Installing pgvector...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("✓ pgvector extension installed")
        
        # Check database
        result = conn.execute(text("SELECT current_database()")).fetchone()
        print(f"✓ Current database: {result[0]}")

if __name__ == "__main__":
    main()
