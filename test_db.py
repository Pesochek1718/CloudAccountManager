#!/usr/bin/env python3
"""
Test script to check database functionality
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from database.database import DatabaseManager

def test_database():
    """Test database operations"""
    print("=" * 50)
    print("DATABASE TEST SCRIPT")
    print("=" * 50)
    
    # Create database manager
    db = DatabaseManager()
    
    # Print database info
    print(f"\n📁 Database file: {db.db_path}")
    print(f"�� File exists: {os.path.exists(db.db_path)}")
    
    if os.path.exists(db.db_path):
        file_size = os.path.getsize(db.db_path)
        print(f"📁 File size: {file_size} bytes")
    
    # Print all current accounts
    print("\n" + "=" * 50)
    print("CURRENT ACCOUNTS IN DATABASE")
    print("=" * 50)
    
    accounts = db.get_all_accounts()
    print(f"Total accounts: {len(accounts)}")
    for acc in accounts:
        print(f"  - ID: {acc.id}, Provider: {acc.provider}, Email: {acc.email}")
    
    db.close()
    print("\n✅ Test complete")

if __name__ == "__main__":
    test_database()
