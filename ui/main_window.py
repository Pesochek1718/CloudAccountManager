"""
Main Window module for Cloud Account Manager
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import QSettings, QRegularExpression

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("CloudTools", "CloudAccountManager")
        self.dark_mode = self.settings.value("dark_mode", True, type=bool)
        
        # Сначала добавляем методы таблицы
        from ui.table import add_table_methods_to_window
        add_table_methods_to_window(self)
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize UI"""
        # Window settings
        self.setWindowTitle("Cloud Account Manager v1.0")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Import and create components
        from ui.menu_bar import create_menu_bar
        from ui.toolbar import create_toolbar
        from ui.filters import create_filter_panel
        from ui.table import create_accounts_table_widget
        from ui.status_bar import create_status_bar, update_status_bar
        from ui.theme import apply_theme
        
        create_menu_bar(self)
        toolbar = create_toolbar(self)
        main_layout.addLayout(toolbar)
        
        filter_panel = create_filter_panel(self)
        main_layout.addWidget(filter_panel)
        
        table_widget = create_accounts_table_widget(self)
        main_layout.addWidget(table_widget, 1)
        
        create_status_bar(self)
        
        # Store update_status_bar method
        self.update_status_bar = lambda: update_status_bar(self)
        
        # Apply theme
        apply_theme(self, self.dark_mode)
        
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Connect filters to auto-apply
        self.provider_filter.currentTextChanged.connect(self.apply_filters)
        self.region_filter.currentTextChanged.connect(self.apply_filters)
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        self.quota_filter.currentTextChanged.connect(self.apply_filters)
        
    def toggle_theme(self, dark):
        """Toggle between dark and light theme"""
        self.dark_mode = dark
        self.settings.setValue("dark_mode", self.dark_mode)
        from ui.theme import apply_theme
        apply_theme(self, self.dark_mode)
        
    def apply_filters(self):
        """Apply filters automatically when selection changes"""
        provider_filter = self.provider_filter.currentText()
        region_filter = self.region_filter.currentText()
        status_filter = self.status_filter.currentText()
        quota_filter = self.quota_filter.currentText()
        
        # Build filter regex pattern
        filter_patterns = []
        
        if provider_filter != "All":
            filter_patterns.append(f"Provider:.*{provider_filter}.*")
        
        if region_filter != "All":
            filter_patterns.append(f"Region:.*{region_filter}.*")
            
        if status_filter != "All":
            status_text = status_filter.replace("✅ ", "").replace("❌ ", "")
            filter_patterns.append(f"Status:.*{status_text}.*")
        
        if quota_filter != "All":
            if quota_filter == "Low (<20%)":
                filter_patterns.append(r"Quota:(0?[0-9]|1[0-9])%")
            elif quota_filter == "Medium (20-80%)":
                filter_patterns.append(r"Quota:([2-7][0-9]|80)%")
            elif quota_filter == "High (>80%)":
                filter_patterns.append(r"Quota:(8[1-9]|9[0-9]|100)%")
            elif quota_filter == "3/10":
                filter_patterns.append(r"Quota:[0-3]/10")
            elif quota_filter == "10/10":
                filter_patterns.append(r"Quota:10/10")
        
        # Combine patterns
        if filter_patterns:
            combined_pattern = ".*" + ".*".join(filter_patterns) + ".*"
            regex = QRegularExpression(combined_pattern, QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.proxy_model.setFilterRegularExpression(regex)
        else:
            self.proxy_model.setFilterRegularExpression("")
        
        # Update status bar
        self.update_status_bar()
        
    def reset_filters(self):
        """Reset all filters"""
        self.provider_filter.setCurrentIndex(0)
        self.region_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.quota_filter.setCurrentIndex(0)
        self.proxy_model.setFilterRegularExpression("")
        self.statusBar().showMessage("✅ Ready | Total accounts: 5 | Selected: 0")
        
    def add_account(self):
        """Open modal dialog to add account"""
        from ui.add_account_dialog import AddAccountDialog
        dialog = AddAccountDialog(self)
        if dialog.exec():
            # Here we would add to database
            pass
            
    def check_selected(self):
        """Check selected accounts"""
        selected_rows = self.get_selected_rows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select at least one account!")
            return
            
        # Silent checking
        
    def delete_selected(self):
        """Delete selected accounts from table"""
        selected_rows = self.get_selected_rows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select at least one account!")
            return
            
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Are you sure you want to delete {len(selected_rows)} selected accounts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # даляем выбранные строки из модели
            # ужно удалять в обратном порядке, чтобы индексы не смещались
            for row in sorted(selected_rows, reverse=True):
                # олучаем исходную строку в модели
                source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
                source_row = source_index.row()
                self.model.removeRow(source_row)
            
            # бновляем фильтр регионов
            self.refresh_region_filter()
            # бновляем статус бар
            self.update_status_bar()
            
    def refresh_region_filter(self):
        """Refresh region filter from current table data"""
        regions = set()
        for row in range(self.model.rowCount()):
            region_item = self.model.item(row, 4)  # Region column
            if region_item:
                regions.add(region_item.text())
        
        self.region_filter.clear()
        self.region_filter.addItem("All")
        for region in sorted(regions):
            self.region_filter.addItem(region)
            
    def open_proxy_settings(self):
        """Open proxy settings dialog"""
        # Will be implemented later
        pass
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Cloud Account Manager",
            "<h3>Cloud Account Manager v1.0</h3>"
            "<p>A professional tool to manage and monitor cloud service accounts.</p>"
            "<p><b>Supported Providers:</b><br>"
            "• AWS (Amazon Web Services)<br>"
            "• Linode<br>"
            "• Digital Ocean</p>"
            "<p><b>Features:</b><br>"
            "• Account management with email identification<br>"
            "• SOCKS5 proxy support for all connections<br>"
            "• Dark/Light theme switching<br>"
            "• Copy selected accounts to clipboard<br>"
            "• Real-time quota monitoring</p>"
            "<p>Made with support from @CloudStorm_bot</p>"
            "<p>Created with PyQt6</p>"
        )
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save settings
        self.settings.sync()
        event.accept()
