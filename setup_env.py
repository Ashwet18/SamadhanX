#!/usr/bin/env python3
"""Setup environment file with PostgreSQL credentials."""

import getpass
import secrets
import string
from pathlib import Path

def generate_jwt_secret(length=48):
    """Generate a secure random JWT secret."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("SamadhanX Environment Setup")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path(".env")
    if env_file.exists():
        overwrite = input("\n.env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
        # Backup existing file
        env_file.rename(".env.backup")
        print("✓ Backed up existing .env to .env.backup")
    
    # Get PostgreSQL password
    print("\nEnter PostgreSQL credentials:")
    password = getpass.getpass("PostgreSQL password for user 'postgres': ")
    
    if not password:
        print("ERROR: Password cannot be empty")
        return
    
    # Generate JWT secret
    jwt_secret = generate_jwt_secret()
    
    # Create DATABASE_URL
    database_url = f"postgresql://postgres:{password}@localhost:5432/samadhanx"
    test_database_url = f"postgresql://postgres:{password}@localhost:5432/samadhanx_test"
    
    # Create .env content
    env_content = f"""# SamadhanX Environment Configuration
# Generated automatically - DO NOT COMMIT TO GIT

# ===================================
# APPLICATION CONFIGURATION
# ===================================
APP_NAME=SamadhanX
VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# ===================================
# DATABASE CONFIGURATION
# ===================================
DATABASE_URL={database_url}
POSTGRES_USER=postgres
POSTGRES_PASSWORD={password}
POSTGRES_DB=samadhanx
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Database Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ===================================
# AUTHENTICATION & SECURITY
# ===================================
JWT_SECRET_KEY={jwt_secret}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_MIN_LENGTH=8

# ===================================
# CORS CONFIGURATION
# ===================================
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080

# ===================================
# AI/ML SERVICES
# ===================================
OPENAI_API_KEY=sk-your-openai-api-key-here
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-4
MAX_TOKENS=2000
AI_TEMPERATURE=0.7

# ===================================
# TESTING
# ===================================
TEST_DATABASE_URL={test_database_url}

# ===================================
# FILE STORAGE
# ===================================
STORAGE_BACKEND=local
UPLOAD_MAX_SIZE=10485760
LOCAL_STORAGE_PATH=./uploads

# ===================================
# API CONFIGURATION
# ===================================
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
DOCS_ENABLED=true

# ===================================
# LOGGING
# ===================================
LOG_LEVEL=INFO
"""
    
    # Write .env file
    env_file.write_text(env_content, encoding='utf-8')
    
    print("\n" + "=" * 50)
    print("✓ .env file created successfully")
    print("✓ DATABASE_URL configured for PostgreSQL 18")
    print("✓ JWT secret generated")
    print(f"✓ Configuration saved to: {env_file.absolute()}")
    print("\nNext steps:")
    print("1. cd backend")
    print("2. alembic revision --autogenerate -m 'initial migration'")
    print("3. alembic upgrade head")
    print("4. pytest tests/test_industry.py -v")

if __name__ == "__main__":
    main()
