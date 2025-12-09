"""
Status Bar component for Cloud Account Manager
"""

from PyQt6.QtWidgets import QLabel

def create_status_bar(window):
    """Create status bar without credit"""
    status_bar = window.statusBar()
    status_bar.showMessage("✅ Ready | Total accounts: 5 | Selected: 0")
    
    # брали надпись про бота из статус бара

# Helper method to update status bar
def update_status_bar(window):
    """Update status bar with selection info"""
    selected_count = len(window.get_selected_rows())
    filtered_count = window.proxy_model.rowCount()
    total_count = window.model.rowCount()
    
    if filtered_count == total_count:
        window.statusBar().showMessage(f"✅ Ready | Total accounts: {total_count} | Selected: {selected_count}")
    else:
        window.statusBar().showMessage(f"✅ Filtered: {filtered_count} of {total_count} accounts | Selected: {selected_count}")
