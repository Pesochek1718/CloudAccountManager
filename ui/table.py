"""
Table component for Cloud Account Manager
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, 
    QHeaderView, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt6.QtGui import QGuiApplication

def create_accounts_table_widget(window):
    """Create widget containing table and select all checkbox"""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(5)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Select all checkbox row
    select_row = QHBoxLayout()
    select_row.setContentsMargins(0, 0, 0, 5)
    
    window.select_all_checkbox = QCheckBox("Select All")
    window.select_all_checkbox.stateChanged.connect(window.toggle_select_all)
    select_row.addWidget(window.select_all_checkbox)
    select_row.addStretch()
    
    layout.addLayout(select_row)
    
    # Table
    window.accounts_table = create_accounts_table(window)
    layout.addWidget(window.accounts_table)
    
    return widget

def create_accounts_table(window):
    """Create table for displaying accounts"""
    table = QTableView()
    
    # Create proxy model for filtering
    window.proxy_model = QSortFilterProxyModel()
    window.proxy_model.setFilterKeyColumn(-1)
    window.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    
    # Data model
    window.model = QStandardItemModel()
    window.model.setHorizontalHeaderLabels([
        "",  # Checkbox
        "ID",
        "Provider",
        "Email",
        "Region",
        "Status",
        "Quota",
        "Last Check",
        "Actions"
    ])
    
    # Set proxy model source
    window.proxy_model.setSourceModel(window.model)
    table.setModel(window.proxy_model)
    
    # Table settings
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
    
    # Set column widths
    header = table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
    header.resizeSection(0, 30)  # Checkbox
    header.resizeSection(1, 50)  # ID
    header.resizeSection(2, 100)  # Provider
    header.resizeSection(3, 200)  # Email
    header.resizeSection(4, 120)  # Region
    header.resizeSection(5, 100)  # Status
    header.resizeSection(6, 80)   # Quota
    header.resizeSection(7, 120)  # Last Check
    header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)  # Actions
    
    # Sorting disabled as requested
    
    # Load sample data
    load_sample_data(window)
    
    # Connect signals - но  update_status_bar, он добавится позже
    # table.selectionModel().selectionChanged.connect(window.update_status_bar)
    
    return table

def load_sample_data(window):
    """Load sample data for testing"""
    # Clear existing data
    window.model.removeRows(0, window.model.rowCount())
    
    # Sample data with emails
    window.sample_data = [
        {
            "id": "1", 
            "provider": "AWS", 
            "email": "admin@company.com", 
            "region": "us-east-1", 
            "status": "✅ Active", 
            "quota": "80%",
            "last_check": "2024-01-20 14:30", "comment": "Production account"
        },
        {
            "id": "2", 
            "provider": "Linode", 
            "email": "dev@company.com", 
            "region": "eu-west", 
            "status": "✅ Active", 
            "quota": "3/10",
            "last_check": "2024-01-19 09:15", "comment": "Development"
        },
        {
            "id": "3", 
            "provider": "Digital Ocean", 
            "email": "test@company.com", 
            "region": "sgp1", 
            "status": "❌ Error", 
            "quota": "2/10",
            "last_check": "2024-01-18 16:45", "comment": "Testing"
        },
        {
            "id": "4", 
            "provider": "AWS", 
            "email": "support@company.com", 
            "region": "us-west-2", 
            "status": "✅ Active", 
            "quota": "45%",
            "last_check": "2024-01-21 11:20", "comment": "Support"
        },
        {
            "id": "5", 
            "provider": "Digital Ocean", 
            "email": "backup@company.com", 
            "region": "nyc3", 
            "status": "✅ Active", 
            "quota": "1/10",
            "last_check": "2024-01-22 09:45", "comment": "Backup"
        },
    ]
    
    for account in window.sample_data:
        items = []
        
        # Checkbox
        checkbox_item = QStandardItem()
        checkbox_item.setCheckable(True)
        checkbox_item.setCheckState(Qt.CheckState.Unchecked)
        checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        items.append(checkbox_item)
        
        # ID
        id_item = QStandardItem(account["id"])
        id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        items.append(id_item)
        
        # Provider with icon/color
        provider_item = QStandardItem(account["provider"])
        if account["provider"] == "AWS":
            provider_item.setForeground(QBrush(QColor("#FF9900")))
        elif account["provider"] == "Linode":
            provider_item.setForeground(QBrush(QColor("#02B159")))
        elif account["provider"] == "Digital Ocean":
            provider_item.setForeground(QBrush(QColor("#0080FF")))
        items.append(provider_item)
        
        # Email
        email_item = QStandardItem(account["email"])
        items.append(email_item)
        
        # Region
        region_item = QStandardItem(account["region"])
        items.append(region_item)
        
        # Status
        status_item = QStandardItem(account["status"])
        if "✅" in account["status"]:
            status_item.setForeground(QBrush(QColor("#28a745")))
        elif "❌" in account["status"]:
            status_item.setForeground(QBrush(QColor("#dc3545")))
        items.append(status_item)
        
        # Quota
        quota_item = QStandardItem(account["quota"])
        if account["provider"] == "AWS":
            quota_percent = int(account["quota"].replace("%", ""))
            if quota_percent > 80:
                quota_item.setForeground(QBrush(QColor("#dc3545")))
            elif quota_percent > 50:
                quota_item.setForeground(QBrush(QColor("#ffc107")))
            else:
                quota_item.setForeground(QBrush(QColor("#28a745")))
        else:
            if '/' in account["quota"]:
                current, total = map(int, account["quota"].split('/'))
                if current >= total:
                    quota_item.setForeground(QBrush(QColor("#dc3545")))
                elif current >= total * 0.7:
                    quota_item.setForeground(QBrush(QColor("#ffc107")))
                else:
                    quota_item.setForeground(QBrush(QColor("#28a745")))
        items.append(quota_item)
        
        # Last check
        items.append(QStandardItem(account["last_check"]))
        
        # Actions cell
        actions_item = QStandardItem("👁️ View | 🗑️ Delete | 🔍 Check")
        actions_item.setEditable(False)
        items.append(actions_item)
        
        # Make all items non-editable except checkbox
        for i, item in enumerate(items):
            if i != 0:
                item.setEditable(False)
        
        window.model.appendRow(items)
    
    # Update region filter from sample data
    regions = set()
    for account in window.sample_data:
        regions.add(account["region"])
    
    window.region_filter.clear()
    window.region_filter.addItem("All")
    for region in sorted(regions):
        window.region_filter.addItem(region)

def add_table_methods_to_window(window):
    """Add table-related methods to window class"""
    
    def toggle_select_all(state):
        """Toggle select all checkboxes"""
        for row in range(window.model.rowCount()):
            item = window.model.item(row, 0)
            item.setCheckState(Qt.CheckState(state))
        # бновляем статус бар если метод существует
        if hasattr(window, 'update_status_bar'):
            window.update_status_bar()
    
    def get_selected_rows():
        """Get list of selected row indices from proxy model"""
        selected_rows = []
        for row in range(window.proxy_model.rowCount()):
            source_index = window.proxy_model.mapToSource(window.proxy_model.index(row, 0))
            source_row = source_index.row()
            
            item = window.model.item(source_row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                selected_rows.append(row)
        return selected_rows
    
    def copy_selected():
        """Copy selected accounts data to clipboard"""
        selected_rows = get_selected_rows()
        
        if not selected_rows:
            QMessageBox.warning(window, "Warning", "Please select at least one account!")
            return
            
        copied_data = []
        for row in selected_rows:
            row_data = []
            source_row = window.proxy_model.mapToSource(window.proxy_model.index(row, 0)).row()
            
            for col in range(window.model.columnCount()):
                item = window.model.item(source_row, col)
                if item:
                    if col == 0:
                        row_data.append("✓" if item.checkState() == Qt.CheckState.Checked else "✗")
                    else:
                        row_data.append(item.text())
            
            copied_data.append("\t".join(row_data))
        
        clipboard_text = "\n".join(copied_data)
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(clipboard_text)
    
    # Attach methods to window
    window.toggle_select_all = toggle_select_all
    window.get_selected_rows = get_selected_rows
    window.copy_selected = copy_selected
    
    # Теперь можно подключить сигнал после того как методы добавлены
    if hasattr(window, 'accounts_table'):
        window.accounts_table.selectionModel().selectionChanged.connect(
            lambda: window.update_status_bar() if hasattr(window, 'update_status_bar') else None
        )





