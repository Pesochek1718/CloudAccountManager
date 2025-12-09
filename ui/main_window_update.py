#  классе MainWindow, в методе init_ui, после создания таблицы:
self.accounts_table = AccountsTable(self.db, self)
# ... существующий код ...

#  методе init_ui, где создается кнопка Add Account, обновляем:
add_account_action.triggered.connect(self.show_add_account_dialog)

# обавляем новый метод:
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
        success = self.db.save_account(account_data)
        if success:
            # Refresh accounts table
            self.accounts_table.refresh_data()
            # Show success message
            QMessageBox.information(self, "Success", 
                                  f"{account_data['provider']} account added successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save account to database.")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to add account: {str(e)}")
