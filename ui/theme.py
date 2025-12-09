"""
Theme component for Cloud Account Manager
"""

def apply_theme(window, dark_mode):
    """Apply dark or light theme with improved colors"""
    if dark_mode:
        # Improved dark theme
        window.setStyleSheet(f"""
            QMainWindow {{
                background-color: #1a1a1a;
            }}
            QMenuBar {{
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 11px;
                border-bottom: 1px solid #404040;
            }}
            QMenuBar::item {{
                padding: 5px 10px;
                background-color: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: #404040;
                border-radius: 3px;
            }}
            QWidget {{
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }}
            QTableView {{
                background-color: #252525;
                alternate-background-color: #2d2d2d;
                gridline-color: #404040;
                selection-background-color: #404040;
                selection-color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
            }}
            QTableView::item {{
                padding: 4px;
                border-bottom: 1px solid #353535;
            }}
            QTableView::item:selected {{
                background-color: #404040;
            }}
            QHeaderView::section {{
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 6px;
                border: none;
                border-right: 1px solid #404040;
                border-bottom: 1px solid #404040;
                font-weight: bold;
                font-size: 11px;
            }}
            QComboBox, QLineEdit {{
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #404040;
                padding: 4px;
                border-radius: 3px;
                min-height: 24px;
                font-size: 11px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QLabel {{
                color: #b0b0b0;
                font-weight: bold;
                font-size: 11px;
            }}
            QCheckBox {{
                color: #b0b0b0;
                font-size: 11px;
            }}
            QStatusBar {{
                background-color: #252525;
                color: #b0b0b0;
                border-top: 1px solid #404040;
                font-size: 11px;
            }}
            QMenu {{
                background-color: #252525;
                color: #e0e0e0;
                border: 1px solid #404040;
                font-size: 11px;
            }}
            QMenu::item:selected {{
                background-color: #404040;
            }}
        """)
    else:
        # Improved light theme with light gray background
        window.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f0f0f0;
            }}
            QMenuBar {{
                background-color: #e8e8e8;
                color: #333333;
                font-size: 11px;
                border-bottom: 1px solid #d0d0d0;
            }}
            QMenuBar::item {{
                padding: 5px 10px;
                background-color: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: #d0d0d0;
                border-radius: 3px;
            }}
            QWidget {{
                background-color: #f5f5f5;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }}
            QTableView {{
                background-color: #ffffff;
                alternate-background-color: #f8f8f8;
                gridline-color: #e0e0e0;
                selection-background-color: #e8e8e8;
                selection-color: #333333;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }}
            QTableView::item {{
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
            }}
            QTableView::item:selected {{
                background-color: #e8e8e8;
            }}
            QHeaderView::section {{
                background-color: #f0f0f0;
                color: #555555;
                padding: 6px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 11px;
            }}
            QComboBox, QLineEdit {{
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                padding: 4px;
                border-radius: 3px;
                min-height: 24px;
                font-size: 11px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QLabel {{
                color: #555555;
                font-weight: bold;
                font-size: 11px;
            }}
            QCheckBox {{
                color: #555555;
                font-size: 11px;
            }}
            QStatusBar {{
                background-color: #f0f0f0;
                color: #666666;
                border-top: 1px solid #d0d0d0;
                font-size: 11px;
            }}
            QMenu {{
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #d0d0d0;
                font-size: 11px;
            }}
            QMenu::item:selected {{
                background-color: #e8e8e8;
            }}
        """)
