import sys
import os

print("Testing imports...")

# обавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# роверяем структуру
print(f"Current dir: {os.getcwd()}")
print(f"Database dir exists: {os.path.exists('database')}")
print(f"Database/__init__.py exists: {os.path.exists('database/__init__.py')}")
print(f"Database/database.py exists: {os.path.exists('database/database.py')}")

# робуем импорт
try:
    from database.database import DatabaseManager
    print("✅ SUCCESS: DatabaseManager imported!")
except ImportError as e:
    print(f"❌ ImportError: {e}")
    # робуем альтернативный импорт
    try:
        import database.database
        print("✅ Alternative import works")
    except Exception as e2:
        print(f"❌ Alternative also failed: {e2}")
