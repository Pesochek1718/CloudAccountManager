#  классе MainWindow добавляем/обновляем методы:

def show_add_account_dialog(self):
    """Show dialog for adding new account"""
    from ui.add_account_dialog import AddAccountDialog
    dialog = AddAccountDialog(self)
    dialog.account_added.connect(self.on_account_added)
    dialog.exec()

def on_account_added(self, account_data):
    """Handle new account added from dialog"""
    try:
        # Save to database
        success = self.accounts_table.add_account(account_data)
        if success:
            # Show success message
            QMessageBox.information(self, "Success", 
                                  f"{account_data['provider']} account added successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save account to database.")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to add account: {str(e)}")

#  методе init_ui, где создается меню:
add_account_action = QAction("Add Account", self)
add_account_action.setShortcut("Ctrl+N")
add_account_action.triggered.connect(self.show_add_account_dialog)
file_menu.addAction(add_account_action)
