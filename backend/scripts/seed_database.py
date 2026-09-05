"""
Seed database script - run directly to populate demo data.
Usage: python -m scripts.seed_database
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.seed import seed_database


if __name__ == "__main__":
    print("Seeding TechKart database with demo data...")
    asyncio.run(seed_database())
    print("Done!")