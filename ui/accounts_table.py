"""
Accounts table widget with filtering capabilities
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMenu, QMessageBox, QComboBox, QLabel,
    QLineEdit, QDateEdit, QCheckBox, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QAction, QFont
from datetime import datetime, timedelta

class AccountsTable(QWidget):
    """Table widget for displaying cloud accounts"""
    
    account_selected = pyqtSignal(int)  # Emit account ID when selected
    refresh_requested = pyqtSignal()    # Request data refresh
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_provider = "AWS"
        self.current_filter = {'provider': 'AWS'}
        self.init_ui()
        self.load_accounts()
    
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        
        # Filter section
        filter_layout = QVBoxLayout()
        
        # Provider selector
        provider_layout = QHBoxLayout()
        provider_label = QLabel("Provider:")
        provider_label.setFixedWidth(80)
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["AWS", "DigitalOcean", "Linode", "Azure"])
        self.provider_combo.setCurrentText(self.current_provider)
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        
        filter_layout.addLayout(provider_layout)
        
        # Provider-specific filters
        self.filter_frame = QFrame()
        self.filter_layout = QHBoxLayout(self.filter_frame)
        self.filter_layout.setSpacing(10)
        
        filter_layout.addWidget(self.filter_frame)
        main_layout.addLayout(filter_layout)
        
        # Update filters based on current provider
        self.update_filters()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(0)  # Will be set in load_accounts
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        main_layout.addWidget(self.table)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.count_label = QLabel("0 accounts")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setFixedWidth(80)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.count_label)
        status_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(status_layout)
    
    def update_filters(self):
        """Update filters based on current provider - FIXED VERSION"""
        # Clear existing filters
        for i in reversed(range(self.filter_layout.count())):
            widget = self.filter_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Reset current filter but keep provider
        self.current_filter = {'provider': self.current_provider}
        
        if self.current_provider == "AWS":
            # AWS filters - регион, квота, страна регистрации, когда добавлен
            # Region filter - ТСЯ  
            region_label = QLabel("Region:")
            region_label.setFixedWidth(60)
            self.region_combo = QComboBox()
            self.region_combo.addItem("All regions", "")
            # Get regions from database
            regions = self.db.get_unique_regions("AWS")
            for region in regions:
                self.region_combo.addItem(region, region)
            self.region_combo.currentIndexChanged.connect(self.apply_filters)
            
            # Quota filter - вычисляется на основе данных
            quota_label = QLabel("Quota:")
            quota_label.setFixedWidth(60)
            self.quota_combo = QComboBox()
            self.quota_combo.addItem("All quotas", "")
            self.quota_combo.addItem("Low (<30%)", "low")
            self.quota_combo.addItem("Medium (30-70%)", "medium")
            self.quota_combo.addItem("High (>70%)", "high")
            self.quota_combo.addItem("No data", "no_data")
            self.quota_combo.currentIndexChanged.connect(self.apply_filters)
            
            # Country filter - ТСЯ  
            country_label = QLabel("Country:")
            country_label.setFixedWidth(60)
            self.country_combo = QComboBox()
            self.country_combo.addItem("All countries", "")
            countries = self.db.get_unique_countries("AWS")
            for country in countries:
                self.country_combo.addItem(country, country)
            self.country_combo.currentIndexChanged.connect(self.apply_filters)
            
            # Time filter - когда добавлен
            time_label = QLabel("Added:")
            time_label.setFixedWidth(60)
            self.time_combo = QComboBox()
            self.time_combo.addItem("All time", "")
            self.time_combo.addItem("Last 24 hours", "day")
            self.time_combo.addItem("Last 2 days", "days2")
            self.time_combo.addItem("Last week", "week")
            self.time_combo.addItem("Last month", "month")
            self.time_combo.currentIndexChanged.connect(self.apply_filters)
            
            self.filter_layout.addWidget(region_label)
            self.filter_layout.addWidget(self.region_combo)
            self.filter_layout.addWidget(quota_label)
            self.filter_layout.addWidget(self.quota_combo)
            self.filter_layout.addWidget(country_label)
            self.filter_layout.addWidget(self.country_combo)
            self.filter_layout.addWidget(time_label)
            self.filter_layout.addWidget(self.time_combo)
            
        elif self.current_provider == "DigitalOcean":
            # DigitalOcean filters - квота 3/10, когда добавлен, страна регистрации, способ оплаты
            # Quota filter - 3/10 (пример лимитов)
            quota_label = QLabel("Limits:")
            quota_label.setFixedWidth(60)
            self.do_quota_combo = QComboBox()
            self.do_quota_combo.addItem("All limits", "")
            self.do_quota_combo.addItem("With limits set", "with_limits")
            self.do_quota_combo.addItem("No limits set", "no_limits")
            self.do_quota_combo.currentIndexChanged.connect(self.apply_filters)
            
            # Time filter - когда добавлен
            time_label = QLabel("Added:")
            time_label.setFixedWidth(60)
            self.do_time_combo = QComboBox()
            self.do_time_combo.addItem("All time", "")
            self.do_time_combo.addItem("Last 24 hours", "day")
            self.do_time_combo.addItem("Last 2 days", "days2")
            self.do_time_combo.addItem("Last week", "week")
            self.do_time_combo.addItem("Last month", "month")
            self.do_time_combo.currentIndexChanged.connect(self.apply_filters)
            
            # Country filter - ТСЯ  
            country_label = QLabel("Country:")
            country_label.setFixedWidth(60)
            self.do_country_combo = QComboBox()
            self.do_country_combo.addItem("All countries", "")
            countries = self.db.get_unique_countries("DigitalOcean")
            for country in countries:
                self.do_country_combo.addItem(country, country)
            self.do_country_combo.currentIndexChanged.connect(self.apply_filters)
            
            # Payment method filter - ТСЯ  
            payment_label = QLabel("Payment:")
            payment_label.setFixedWidth(60)
            self.do_payment_combo = QComboBox()
            self.do_payment_combo.addItem("All methods", "")
            # Get payment methods from database
            methods = self.db.get_unique_payment_methods("DigitalOcean")
            for method in methods:
                self.do_payment_combo.addItem(method, method)
            # If no data in DB yet, add defaults
            if not methods:
                self.do_payment_combo.addItem("Card", "card")
                self.do_payment_combo.addItem("PayPal", "paypal")
            self.do_payment_combo.currentIndexChanged.connect(self.apply_filters)
            
            self.filter_layout.addWidget(quota_label)
            self.filter_layout.addWidget(self.do_quota_combo)
            self.filter_layout.addWidget(time_label)
            self.filter_layout.addWidget(self.do_time_combo)
            self.filter_layout.addWidget(country_label)
            self.filter_layout.addWidget(self.do_country_combo)
            self.filter_layout.addWidget(payment_label)
            self.filter_layout.addWidget(self.do_payment_combo)
            
        elif self.current_provider == "Linode":
            # Linode filters - страна регистрации, способ оплаты
            # Country filter - ТСЯ  
            country_label = QLabel("Country:")
            country_label.setFixedWidth(60)
            self.linode_country_combo = QComboBox()
            self.linode_country_combo.addItem("All countries", "")
            countries = self.db.get_unique_countries("Linode")
            for country in countries:
                self.linode_country_combo.addItem(country, country)
            self.linode_country_combo.currentIndexChanged.connect(self.apply_filters)
            
            # Payment method filter - ТСЯ  
            payment_label = QLabel("Payment:")
            payment_label.setFixedWidth(60)
            self.linode_payment_combo = QComboBox()
            self.linode_payment_combo.addItem("All methods", "")
            methods = self.db.get_unique_payment_methods("Linode")
            for method in methods:
                self.linode_payment_combo.addItem(method, method)
            # If no data in DB yet, add defaults
            if not methods:
                self.linode_payment_combo.addItem("Card", "card")
                self.linode_payment_combo.addItem("PayPal", "paypal")
            self.linode_payment_combo.currentIndexChanged.connect(self.apply_filters)
            
            self.filter_layout.addWidget(country_label)
            self.filter_layout.addWidget(self.linode_country_combo)
            self.filter_layout.addWidget(payment_label)
            self.filter_layout.addWidget(self.linode_payment_combo)
            
        elif self.current_provider == "Azure":
            # Azure filters - страна регистрации, вид аккаунта
            # Country filter - ТСЯ  
            country_label = QLabel("Country:")
            country_label.setFixedWidth(60)
            self.azure_country_combo = QComboBox()
            self.azure_country_combo.addItem("All countries", "")
            countries = self.db.get_unique_countries("Azure")
            for country in countries:
                self.azure_country_combo.addItem(country, country)
            self.azure_country_combo.currentIndexChanged.connect(self.apply_filters)
            
            # Subscription filter - ТСЯ  
            sub_label = QLabel("Subscription:")
            sub_label.setFixedWidth(80)
            self.azure_sub_combo = QComboBox()
            self.azure_sub_combo.addItem("All types", "")
            subscriptions = self.db.get_unique_subscriptions()
            for subscription in subscriptions:
                self.azure_sub_combo.addItem(subscription, subscription)
            # If no data in DB yet, add defaults
            if not subscriptions:
                self.azure_sub_combo.addItem("Pay as You Go", "Pay as You Go")
                self.azure_sub_combo.addItem("Free Trial 200$", "Free Trial 200$")
            self.azure_sub_combo.currentIndexChanged.connect(self.apply_filters)
            
            self.filter_layout.addWidget(country_label)
            self.filter_layout.addWidget(self.azure_country_combo)
            self.filter_layout.addWidget(sub_label)
            self.filter_layout.addWidget(self.azure_sub_combo)
        
        self.filter_layout.addStretch()
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        clear_btn.setFixedWidth(100)
        self.filter_layout.addWidget(clear_btn)
    
    def on_provider_changed(self, provider):
        """Handle provider change"""
        self.current_provider = provider
        self.current_filter = {'provider': provider}
        self.update_filters()
        self.load_accounts()
    
    def apply_filters(self):
        """Apply current filters"""
        self.current_filter = {'provider': self.current_provider}
        
        if self.current_provider == "AWS":
            region = self.region_combo.currentData()
            if region:
                self.current_filter['region'] = region
            
            quota = self.quota_combo.currentData()
            if quota:
                self.current_filter['quota'] = quota
            
            country = self.country_combo.currentData()
            if country:
                self.current_filter['country'] = country
            
            time_filter = self.time_combo.currentData()
            if time_filter:
                self.current_filter['time_filter'] = time_filter
        
        elif self.current_provider == "DigitalOcean":
            quota = self.do_quota_combo.currentData()
            if quota:
                self.current_filter['quota'] = quota
            
            time_filter = self.do_time_combo.currentData()
            if time_filter:
                self.current_filter['time_filter'] = time_filter
            
            country = self.do_country_combo.currentData()
            if country:
                self.current_filter['country'] = country
            
            payment = self.do_payment_combo.currentData()
            if payment:
                self.current_filter['payment_method'] = payment
        
        elif self.current_provider == "Linode":
            country = self.linode_country_combo.currentData()
            if country:
                self.current_filter['country'] = country
            
            payment = self.linode_payment_combo.currentData()
            if payment:
                self.current_filter['payment_method'] = payment
        
        elif self.current_provider == "Azure":
            country = self.azure_country_combo.currentData()
            if country:
                self.current_filter['country'] = country
            
            subscription = self.azure_sub_combo.currentData()
            if subscription:
                self.current_filter['subscription'] = subscription
        
        self.load_accounts()
    
    def clear_filters(self):
        """Clear all filters"""
        if self.current_provider == "AWS":
            self.region_combo.setCurrentIndex(0)
            self.quota_combo.setCurrentIndex(0)
            self.country_combo.setCurrentIndex(0)
            self.time_combo.setCurrentIndex(0)
        elif self.current_provider == "DigitalOcean":
            self.do_quota_combo.setCurrentIndex(0)
            self.do_time_combo.setCurrentIndex(0)
            self.do_country_combo.setCurrentIndex(0)
            self.do_payment_combo.setCurrentIndex(0)
        elif self.current_provider == "Linode":
            self.linode_country_combo.setCurrentIndex(0)
            self.linode_payment_combo.setCurrentIndex(0)
        elif self.current_provider == "Azure":
            self.azure_country_combo.setCurrentIndex(0)
            self.azure_sub_combo.setCurrentIndex(0)
        
        self.current_filter = {'provider': self.current_provider}
        self.load_accounts()
    
    def load_accounts(self):
        """Load accounts from database with current filters"""
        try:
            # Get accounts from database
            if self.current_filter and len(self.current_filter) > 1:  # Has filters beyond provider
                accounts = self.db.get_accounts_by_filter(self.current_filter)
            else:
                accounts = self.db.get_all_accounts(self.current_provider)
            
            # Update table
            self.update_table(accounts)
            
            # Update status
            self.count_label.setText(f"{len(accounts)} accounts")
            self.status_label.setText(f"Loaded {self.current_provider} accounts")
        except Exception as e:
            print(f"Error loading accounts: {e}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def update_table(self, accounts):
        """Update table with accounts data"""
        # Set columns based on provider
        if self.current_provider == "AWS":
            headers = ["ID", "Email", "Region", "Country", "Quota", "Added", "Status", "Last Check"]
            col_count = 8
        elif self.current_provider == "DigitalOcean":
            headers = ["ID", "Email", "Limits", "Country", "Payment", "Added", "Status"]
            col_count = 7
        elif self.current_provider == "Linode":
            headers = ["ID", "Email", "Login", "Country", "Payment", "Added", "Status"]
            col_count = 7
        elif self.current_provider == "Azure":
            headers = ["ID", "Email", "Subscription", "Country", "Added", "Status"]
            col_count = 6
        else:
            headers = ["ID", "Email", "Added", "Status"]
            col_count = 4
        
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(accounts))
        
        # Fill table with data
        for row, account in enumerate(accounts):
            # Common fields
            id_item = QTableWidgetItem(str(account.id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, id_item)
            
            email_item = QTableWidgetItem(account.email or "")
            email_item.setFlags(email_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, email_item)
            
            # Provider-specific fields
            if self.current_provider == "AWS":
                region_item = QTableWidgetItem(account.region or "")
                self.table.setItem(row, 2, region_item)
                
                country_item = QTableWidgetItem(account.country or "")
                self.table.setItem(row, 3, country_item)
                
                # Quota calculation
                if account.quota_limit and account.quota_used:
                    percentage = (account.quota_used / account.quota_limit) * 100
                    quota_text = f"{account.quota_used}/{account.quota_limit} ({percentage:.1f}%)"
                else:
                    quota_text = "N/A"
                quota_item = QTableWidgetItem(quota_text)
                self.table.setItem(row, 4, quota_item)
                
                # Added date
                added_text = self.format_time_ago(account.created_at)
                added_item = QTableWidgetItem(added_text)
                self.table.setItem(row, 5, added_item)
                
                # Status
                status_item = QTableWidgetItem(account.check_result or "Not checked")
                if account.check_result == "Success":
                    status_item.setForeground(Qt.GlobalColor.green)
                elif account.check_result == "Failed":
                    status_item.setForeground(Qt.GlobalColor.red)
                elif account.check_result == "Warning":
                    status_item.setForeground(Qt.GlobalColor.yellow)
                self.table.setItem(row, 6, status_item)
                
                # Last check
                if account.last_check:
                    last_check = account.last_check.strftime("%Y-%m-%d %H:%M")
                else:
                    last_check = "Never"
                last_item = QTableWidgetItem(last_check)
                self.table.setItem(row, 7, last_item)
            
            elif self.current_provider == "DigitalOcean":
                limits_item = QTableWidgetItem(account.limits or "N/A")
                self.table.setItem(row, 2, limits_item)
                
                country_item = QTableWidgetItem(account.country or "")
                self.table.setItem(row, 3, country_item)
                
                payment_item = QTableWidgetItem(account.payment_method or "N/A")
                self.table.setItem(row, 4, payment_item)
                
                # Added date
                added_text = self.format_time_ago(account.created_at)
                added_item = QTableWidgetItem(added_text)
                self.table.setItem(row, 5, added_item)
                
                # Status
                status_item = QTableWidgetItem(account.check_result or "Not checked")
                self.table.setItem(row, 6, status_item)
            
            elif self.current_provider == "Linode":
                login_item = QTableWidgetItem(account.linode_login or "")
                self.table.setItem(row, 2, login_item)
                
                country_item = QTableWidgetItem(account.linode_country or "")
                self.table.setItem(row, 3, country_item)
                
                payment_item = QTableWidgetItem(account.payment_method or "")
                self.table.setItem(row, 4, payment_item)
                
                # Added date
                added_text = self.format_time_ago(account.created_at)
                added_item = QTableWidgetItem(added_text)
                self.table.setItem(row, 5, added_item)
                
                # Status
                status_item = QTableWidgetItem(account.check_result or "Not checked")
                self.table.setItem(row, 6, status_item)
            
            elif self.current_provider == "Azure":
                subscription_item = QTableWidgetItem(account.subscription or "")
                self.table.setItem(row, 2, subscription_item)
                
                country_item = QTableWidgetItem(account.azure_country or "")
                self.table.setItem(row, 3, country_item)
                
                # Added date
                added_text = self.format_time_ago(account.created_at)
                added_item = QTableWidgetItem(added_text)
                self.table.setItem(row, 4, added_item)
                
                # Status
                status_item = QTableWidgetItem(account.check_result or "Not checked")
                self.table.setItem(row, 5, status_item)
            
            else:
                # Generic view for unknown providers
                added_text = self.format_time_ago(account.created_at)
                added_item = QTableWidgetItem(added_text)
                self.table.setItem(row, 2, added_item)
                
                status_item = QTableWidgetItem(account.check_result or "Active")
                self.table.setItem(row, 3, status_item)
        
        # Resize columns to content
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
    
    def format_time_ago(self, created_at):
        """Format created_at to human readable string"""
        if not created_at:
            return "N/A"
        
        now = datetime.utcnow()
        if created_at.tzinfo:
            created_at = created_at.replace(tzinfo=None)
        
        delta = now - created_at
        days = delta.days
        
        if days == 0:
            hours = delta.seconds // 3600
            if hours == 0:
                minutes = (delta.seconds // 60) % 60
                if minutes == 0:
                    return "Just now"
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif days == 1:
            return "Yesterday"
        elif days < 7:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
    
    def show_context_menu(self, position):
        """Show context menu for table"""
        menu = QMenu()
        
        edit_action = QAction("Edit Account", self)
        delete_action = QAction("Delete Account", self)
        check_action = QAction("Check Now", self)
        view_details = QAction("View Details", self)
        
        edit_action.triggered.connect(self.edit_account)
        delete_action.triggered.connect(self.delete_account)
        check_action.triggered.connect(self.check_account)
        view_details.triggered.connect(self.view_account_details)
        
        menu.addAction(view_details)
        menu.addAction(edit_action)
        menu.addAction(check_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def edit_account(self):
        """Edit selected account"""
        selected = self.table.currentRow()
        if selected >= 0:
            account_id = int(self.table.item(selected, 0).text())
            self.account_selected.emit(account_id)
    
    def delete_account(self):
        """Delete selected account"""
        selected = self.table.currentRow()
        if selected >= 0:
            account_id = int(self.table.item(selected, 0).text())
            
            reply = QMessageBox.question(
                self, 'Confirm Delete',
                'Are you sure you want to delete this account?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.db.delete_account(account_id):
                    self.load_accounts()  # Refresh table
                    QMessageBox.information(self, 'Success', 'Account deleted successfully!')
                else:
                    QMessageBox.warning(self, 'Error', 'Failed to delete account.')
    
    def check_account(self):
        """Check selected account"""
        selected = self.table.currentRow()
        if selected >= 0:
            account_id = int(self.table.item(selected, 0).text())
            # TODO: Implement account checking logic
            QMessageBox.information(self, 'Info', f'Checking account {account_id}...')
    
    def view_account_details(self):
        """View detailed account information"""
        selected = self.table.currentRow()
        if selected >= 0:
            account_id = int(self.table.item(selected, 0).text())
            account = self.db.get_account_by_id(account_id)
            
            if account:
                details = f"""
                <h3>Account Details</h3>
                <b>Provider:</b> {account.provider}<br>
                <b>Email:</b> {account.email}<br>
                <b>Created:</b> {account.created_at.strftime('%Y-%m-%d %H:%M') if account.created_at else 'N/A'}<br>
                <b>Comment:</b> {account.comment or 'None'}<br>
                <b>Status:</b> {account.check_result or 'Not checked'}<br>
                <b>Last Check:</b> {account.last_check.strftime('%Y-%m-%d %H:%M') if account.last_check else 'Never'}<br>
                """
                
                # Add provider-specific details
                if account.provider == 'AWS':
                    details += f"""
                    <hr>
                    <b>Region:</b> {account.region or 'N/A'}<br>
                    <b>Country:</b> {account.country or 'N/A'}<br>
                    <b>Quota:</b> {account.quota_used or 0}/{account.quota_limit or 0}<br>
                    """
                elif account.provider == 'DigitalOcean':
                    details += f"""
                    <hr>
                    <b>Limits:</b> {account.limits or 'N/A'}<br>
                    <b>Country:</b> {account.country or 'N/A'}<br>
                    <b>Payment Method:</b> {account.payment_method or 'N/A'}<br>
                    """
                elif account.provider == 'Linode':
                    details += f"""
                    <hr>
                    <b>Login:</b> {account.linode_login or 'N/A'}<br>
                    <b>Country:</b> {account.linode_country or 'N/A'}<br>
                    <b>Payment Method:</b> {account.payment_method or 'N/A'}<br>
                    """
                elif account.provider == 'Azure':
                    details += f"""
                    <hr>
                    <b>Subscription:</b> {account.subscription or 'N/A'}<br>
                    <b>Country:</b> {account.azure_country or 'N/A'}<br>
                    """
                
                QMessageBox.information(self, 'Account Details', details)
    
    def on_item_double_clicked(self, item):
        """Handle double click on table item"""
        self.view_account_details()
    
    def refresh_data(self):
        """Refresh table data and filters"""
        # Refresh filter dropdowns from database
        self.update_filters()
        # Reload accounts
        self.load_accounts()
        self.refresh_requested.emit()
    
    def add_account(self, account_data):
        """Add new account to database and refresh table - FIXED VERSION"""
        try:
            account_id = self.db.save_account(account_data)
            if account_id:
                # Refresh table to show new account
                self.load_accounts()
                # Refresh filters to include new data
                self.update_filters()
                return True
            else:
                QMessageBox.warning(self, 'Error', 'Failed to save account to database.')
                return False
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Database error: {str(e)}')
            return False
