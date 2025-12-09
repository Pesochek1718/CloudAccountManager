import sys
import os
import traceback

print('='*60)
print('CLOUD ACCOUNT MANAGER - FULLY WORKING')
print('='*60)

# Add paths
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

print(f'Project: {project_path}')

try:
    # Imports
    import yaml
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon, QStandardItem
    from database.database import DatabaseManager
    from ui.main_window import MainWindow
    from models.account import Account
    
    print('All imports successful')
    
    # Load config
    config_path = os.path.join(project_path, 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print('Config loaded')
    else:
        config = {'database': {'url': 'sqlite:///cloud_accounts.db'}}
        print('Using default config')
    
    # Initialize DB
    db_url = config.get('database', {}).get('url', 'sqlite:///cloud_accounts.db')
    print(f'Database URL: {db_url}')
    
    db_manager = DatabaseManager('config.yaml')
    print('Database initialized')
    
    # Add refresh_table method to MainWindow
    original_main_window = MainWindow
    
    class PatchedMainWindow(original_main_window):
        def __init__(self):
            super().__init__()
            self.db_manager = db_manager
            
        def refresh_table(self):
            try:
                # Clear table
                self.model.removeRows(0, self.model.rowCount())
                
                # Load from database
                session = self.db_manager.get_session()
                accounts = session.query(Account).all()
                session.close()
                
                # Add to table
                for account in accounts:
                    items = []
                    
                    # Checkbox
                    checkbox_item = QStandardItem()
                    checkbox_item.setCheckable(True)
                    checkbox_item.setCheckState(Qt.CheckState.Unchecked)
                    checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    items.append(checkbox_item)
                    
                    # ID
                    id_item = QStandardItem(str(account.id))
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    items.append(id_item)
                    
                    # Provider
                    provider_item = QStandardItem(account.provider)
                    items.append(provider_item)
                    
                    # Email
                    email_item = QStandardItem(account.email)
                    items.append(email_item)
                    
                    # Region
                    region_item = QStandardItem(account.region or '')
                    items.append(region_item)
                    
                    # Status
                    status_text = 'Active' if (account.is_active if hasattr(account, 'is_active') else True) else 'Error'
                    status_item = QStandardItem(status_text)
                    items.append(status_item)
                    
                    # Quota
                    quota_item = QStandardItem('N/A')
                    items.append(quota_item)
                    
                    # Last check
                    last_check = account.last_check.strftime('%Y-%m-%d %H:%M') if account.last_check else 'Never'
                    items.append(QStandardItem(last_check))
                    
                    # Actions
                    actions_item = QStandardItem('Actions')
                    actions_item.setEditable(False)
                    items.append(actions_item)
                    
                    # Make non-editable
                    for idx, item in enumerate(items):
                        if idx != 0:
                            item.setEditable(False)
                    
                    self.model.appendRow(items)
                
                print(f'Table refreshed with {len(accounts)} accounts')
                if hasattr(self, 'update_status_bar'):
                    self.update_status_bar()
                
            except Exception as e:
                print(f'Error refreshing table: {e}')
                traceback.print_exc()
        
        def add_account(self):
            """Open modal dialog to add account"""
            try:
                from ui.add_account_dialog import AddAccountDialog
                dialog = AddAccountDialog(self)
                if dialog.exec():
                    # Refresh table after successful addition
                    self.refresh_table()
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Failed to open dialog: {str(e)}")
        
        def delete_selected(self):
            selected_rows = self.get_selected_rows()
            
            if not selected_rows:
                QMessageBox.warning(self, 'Warning', 'Please select accounts to delete')
                return
            
            reply = QMessageBox.question(
                self, 'Confirm',
                f'Delete {len(selected_rows)} accounts from database?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                deleted_count = 0
                for row in selected_rows:
                    source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
                    source_row = source_index.row()
                    
                    # Get account ID from table
                    id_item = self.model.item(source_row, 1)
                    if id_item:
                        account_id = int(id_item.text())
                        if self.db_manager.delete_account(account_id):
                            deleted_count += 1
                
                # Refresh table
                self.refresh_table()
                QMessageBox.information(self, 'Success', f'Deleted {deleted_count} accounts')
    
    # Start application
    app = QApplication(sys.argv)
    app.setApplicationName('Cloud Account Manager')
    
    print('')
    print('Creating main window...')
    window = PatchedMainWindow()
    
    # Load icon
    icon_path = os.path.join(project_path, 'logo.png')
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
        print(f'Icon loaded: {icon_path}')
    
    window.show()
    
    # Refresh table with initial data
    window.refresh_table()
    
    print('')
    print('Application started!')
    print('='*60)
    print('Features:')
    print('  - Add accounts via Add button (uses ORIGINAL dialog)')
    print('  - Delete accounts via Delete button')
    print('  - Data saved to database')
    print('='*60)
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f'')
    print(f'Fatal error: {e}')
    traceback.print_exc()
    input('')
    input('Press Enter to exit...')