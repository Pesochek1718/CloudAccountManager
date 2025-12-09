"""
Cloud Account Manager - Main Application Entry Point
"""

import sys
import os
from pathlib import Path

# Debug: Print current working directory and paths
print("=" * 50)
print("CLOUD ACCOUNT MANAGER - STARTING")
print("=" * 50)
print(f"📁 Current working directory: {os.getcwd()}")
print(f"📁 Script location: {os.path.dirname(os.path.abspath(__file__))}")
print(f"📁 Python version: {sys.version}")

# Check if we're running from PyInstaller bundle
if getattr(sys, 'frozen', False):
    print("⚡ Running as bundled executable")
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    print(f"🐍 Running as Python script from: {application_path}")

# Add project directories to Python path
sys.path.insert(0, application_path)
sys.path.insert(0, os.path.join(application_path, 'ui'))
sys.path.insert(0, os.path.join(application_path, 'models'))
sys.path.insert(0, os.path.join(application_path, 'database'))
sys.path.insert(0, os.path.join(application_path, 'services'))
sys.path.insert(0, os.path.join(application_path, 'utils'))

try:
    import yaml
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    
    from ui.main_window import MainWindow
    from database.database import DatabaseManager
    
    print("✅ All imports successful")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages:")
    print("pip install PyQt6 pyyaml")
    sys.exit(1)

def load_config():
    """Load configuration from YAML file"""
    config_paths = [
        'config.yaml',
        os.path.join(application_path, 'config.yaml'),
        os.path.join(os.path.dirname(application_path), 'config.yaml')
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                print(f"✅ Config loaded from: {config_path}")
                return config
            except Exception as e:
                print(f"⚠️ Error loading config from {config_path}: {e}")
    
    print("⚠️ Config file not found, using defaults")
    return {
        'database': {'url': 'sqlite:///cloud_accounts.db'},
        'ui': {'theme': 'dark', 'language': 'ru'},
        'cloud_providers': {
            'aws': {'enabled': True},
            'digitalocean': {'enabled': True},
            'linode': {'enabled': True},
            'azure': {'enabled': True}
        }
    }

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import pyotp
    except ImportError:
        missing_deps.append("pyotp")
        print("⚠️ pyotp not installed. MFA TOTP codes will not be generated.")
        print("   Install with: pip install pyotp")
    
    try:
        import boto3
    except ImportError:
        missing_deps.append("boto3")
        print("⚠️ boto3 not installed. AWS checking will not work.")
        print("   Install with: pip install boto3")
    
    return missing_deps

def setup_database(config):
    """Setup and initialize database"""
    print("\n" + "=" * 50)
    print("DATABASE SETUP")
    print("=" * 50)
    
    try:
        db_manager = DatabaseManager()
        
        # Print database info
        if hasattr(db_manager, 'db_path'):
            print(f"📁 Database file: {db_manager.db_path}")
            if os.path.exists(db_manager.db_path):
                file_size = os.path.getsize(db_manager.db_path)
                print(f"📁 Database exists, size: {file_size} bytes")
            else:
                print("📁 Database file does not exist yet (will be created)")
        
        # Test database connection
        print("🔍 Testing database connection...")
        test_accounts = db_manager.get_all_accounts()
        print(f"✅ Database connected. Found {len(test_accounts)} existing accounts.")
        
        return db_manager
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to create database in current directory
        print("\n🔄 Trying alternative database location...")
        try:
            # Force SQLite to use current directory
            config['database']['url'] = 'sqlite:///cloud_accounts.db'
            db_manager = DatabaseManager()
            print("✅ Database created in current directory")
            return db_manager
        except Exception as e2:
            print(f"❌ Alternative database setup also failed: {e2}")
            return None

def main():
    """Main application entry point"""
    print("\n" + "=" * 50)
    print("APPLICATION INITIALIZATION")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    print(f"🎨 UI Theme: {config.get('ui', {}).get('theme', 'dark')}")
    print(f"🌐 Language: {config.get('ui', {}).get('language', 'ru')}")
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    # Setup database
    db_manager = setup_database(config)
    if not db_manager:
        print("❌ Failed to initialize database. Exiting.")
        sys.exit(1)
    
    # Create Qt application
    print("\n" + "=" * 50)
    print("STARTING QT APPLICATION")
    print("=" * 50)
    
    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Cloud Account Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("CloudAccountManager")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set application icon if exists
    icon_paths = [
        'logo.png',
        os.path.join(application_path, 'logo.png'),
        os.path.join(application_path, 'ui', 'logo.png')
    ]
    
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            try:
                app.setWindowIcon(QIcon(icon_path))
                print(f"✅ Application icon loaded from: {icon_path}")
                break
            except Exception as e:
                print(f"⚠️ Could not load icon from {icon_path}: {e}")
    
    # Create and show main window
    try:
        print("🪟 Creating main window...")
        window = MainWindow(db_manager, config)
        window.show()
        
        print("✅ Application started successfully!")
        print("\n" + "=" * 50)
        print("READY")
        print("=" * 50)
        
        # Show warning about missing dependencies
        if missing_deps:
            msg = "⚠️ Some dependencies are missing:\n\n"
            for dep in missing_deps:
                msg += f"• {dep}\n"
            msg += "\nSome features may not work properly.\n"
            msg += "Install with: pip install " + " ".join(missing_deps)
            
            QMessageBox.warning(window, "Missing Dependencies", msg)
        
        # Start application event loop
        exit_code = app.exec()
        
        print("\n" + "=" * 50)
        print("APPLICATION SHUTDOWN")
        print("=" * 50)
        
        # Cleanup
        if db_manager:
            db_manager.close()
            print("✅ Database connection closed")
        
        print(f"🔄 Exit code: {exit_code}")
        return exit_code
        
    except Exception as e:
        print(f"❌ Failed to create main window: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error dialog
        error_msg = f"Failed to start application:\n\n{str(e)}\n\n"
        error_msg += "Please check the console for details."
        QMessageBox.critical(None, "Application Error", error_msg)
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
