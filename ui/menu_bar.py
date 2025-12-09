"""
Menu Bar component for Cloud Account Manager
"""

from PyQt6.QtGui import QAction

def create_menu_bar(window):
    """Create menu bar"""
    menubar = window.menuBar()
    
    # File menu
    file_menu = menubar.addMenu("&File")
    
    add_action = QAction("&Add Account", window)
    add_action.setShortcut("Ctrl+N")
    add_action.triggered.connect(window.add_account)
    file_menu.addAction(add_action)
    
    copy_action = QAction("&Copy Selected", window)
    copy_action.setShortcut("Ctrl+C")
    copy_action.triggered.connect(window.copy_selected)
    file_menu.addAction(copy_action)
    
    file_menu.addSeparator()
    
    exit_action = QAction("&Exit", window)
    exit_action.setShortcut("Ctrl+Q")
    exit_action.triggered.connect(window.close)
    file_menu.addAction(exit_action)
    
    # Tools menu
    tools_menu = menubar.addMenu("&Tools")
    
    # Theme switching in Tools menu
    dark_action = QAction("&Dark Theme", window)
    dark_action.setCheckable(True)
    dark_action.setChecked(window.dark_mode)
    dark_action.triggered.connect(lambda: window.toggle_theme(True))
    tools_menu.addAction(dark_action)
    
    light_action = QAction("&Light Theme", window)
    light_action.setCheckable(True)
    light_action.setChecked(not window.dark_mode)
    light_action.triggered.connect(lambda: window.toggle_theme(False))
    tools_menu.addAction(light_action)
    
    tools_menu.addSeparator()
    
    # Proxy settings in Tools menu
    proxy_action = QAction("&Proxy Settings", window)
    proxy_action.setShortcut("Ctrl+P")
    proxy_action.triggered.connect(window.open_proxy_settings)
    tools_menu.addAction(proxy_action)
    
    # Help menu
    help_menu = menubar.addMenu("&Help")
    
    about_action = QAction("&About", window)
    about_action.triggered.connect(window.show_about)
    help_menu.addAction(about_action)
