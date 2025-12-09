#!/usr/bin/env python3
"""
Main entry point for Cloud Account Manager
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Application entry point"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon
    
    app = QApplication(sys.argv)
    app.setApplicationName("Cloud Account Manager")
    app.setOrganizationName("CloudTools")
    
    # Try to set application icon if exists
    icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(icon_path):
        try:
            app.setWindowIcon(QIcon(icon_path))
            print(f"✅ Application icon loaded from: {icon_path}")
        except Exception as e:
            print(f"⚠️ Could not load application icon: {e}")
    
    from ui.main_window import MainWindow
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
