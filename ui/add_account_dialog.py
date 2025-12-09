"""
Add Account Dialog for Cloud Providers
Modal window for adding new cloud accounts (AWS, DigitalOcean, Linode, Azure)
"""

import os
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QMessageBox, QTextEdit, QStackedWidget, QWidget,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QGuiApplication
import random
import string

# Try to import pyotp
try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    print("⚠️ pyotp not installed. Install with: python -m pip install pyotp")
    print("   MFA TOTP codes will not be generated")

class PasswordGenerator:
    """Utility class for generating passwords"""
    
    @staticmethod
    def generate_password(length=16):
        """Generate random password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(characters) for _ in range(length))

class AddAccountDialog(QDialog):
    """Dialog for adding new cloud accounts"""
    
    account_added = pyqtSignal(dict)  # Signal emitted when account is added
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Cloud Account")
        self.setModal(True)
        
        # Get theme from parent
        self.dark_mode = getattr(parent, 'dark_mode', True) if parent else True
        
        # TOTP variables
        self.totp_timer = None
        self.current_interval = -1
        self.prev_code = "---"
        self.curr_code = "---"
        self.next_code = "---"
        
        # Current 2FA secret for timer
        self.current_2fa_secret = ""
        
        # Store current position to prevent jumping
        self.current_position = None
        
        # Initialize UI components
        self.init_ui()
        self.setup_connections()
        self.apply_theme()
        
        # Set initial size
        self.resize(500, 500)
        
        # Center dialog relative to parent
        if self.parent():
            self.current_position = self.parent().frameGeometry().center() - self.rect().center()
            self.move(self.current_position)
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        
        # Provider Selection - обычное выравнивание как было
        provider_layout = QHBoxLayout()
        provider_layout.setSpacing(10)
        
        provider_label = QLabel("Cloud Provider:")
        provider_label.setFixedWidth(120)
        provider_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["AWS", "DigitalOcean", "Linode", "Azure"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        
        main_layout.addLayout(provider_layout)
        
        # Stacked Widget for different provider forms
        self.stacked_widget = QStackedWidget()
        
        # AWS Form
        self.aws_widget = self.create_aws_form()
        self.stacked_widget.addWidget(self.aws_widget)
        
        # DigitalOcean Form
        self.do_widget = self.create_digitalocean_form()
        self.stacked_widget.addWidget(self.do_widget)
        
        # Linode Form
        self.linode_widget = self.create_linode_form()
        self.stacked_widget.addWidget(self.linode_widget)
        
        # Azure Form
        self.azure_widget = self.create_azure_form()
        self.stacked_widget.addWidget(self.azure_widget)
        
        main_layout.addWidget(self.stacked_widget)
        
        # TOTP Codes Frame - С , порядок: коды → таймер
        self.totp_frame = QFrame()
        self.totp_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.totp_frame.setVisible(True)
        self.totp_frame.setMaximumHeight(80)
        
        totp_layout = QHBoxLayout(self.totp_frame)
        totp_layout.setSpacing(10)
        totp_layout.setContentsMargins(5, 5, 5, 5)
        
        # ервое окно - редыдущий код
        self.first_totp_btn = QPushButton("---")
        self.first_totp_btn.setFixedSize(100, 35)
        self.first_totp_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: #28a745;
                padding: 5px;
                border: 1px solid #28a745;
                border-radius: 4px;
                background-color: rgba(40, 167, 69, 0.1);
            }
            QPushButton:hover {
                background-color: rgba(40, 167, 69, 0.2);
            }
        """)
        
        # торое окно - Текущий код
        self.second_totp_btn = QPushButton("---")
        self.second_totp_btn.setFixedSize(100, 35)
        self.second_totp_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: #6c757d;
                padding: 5px;
                border: 1px solid #6c757d;
                border-radius: 4px;
                background-color: rgba(108, 117, 125, 0.1);
            }
            QPushButton:hover {
                background-color: rgba(108, 117, 125, 0.2);
            }
        """)
        
        # Timer label (после кодов)
        self.timer_label = QLabel("--:--")
        self.timer_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #17a2b8;
                padding: 2px;
                min-width: 40px;
            }
        """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        totp_layout.addWidget(self.first_totp_btn)
        totp_layout.addWidget(self.second_totp_btn)
        totp_layout.addWidget(self.timer_label)
        totp_layout.addStretch()
        
        main_layout.addWidget(self.totp_frame)
        
        # Comment Field - обычное выравнивание как было
        comment_layout = QHBoxLayout()
        comment_layout.setSpacing(10)
        
        comment_label = QLabel("Comment:")
        comment_label.setFixedWidth(120)
        comment_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        
        self.comment_input = QTextEdit()
        self.comment_input.setMaximumHeight(60)
        self.comment_input.setPlaceholderText("Optional comment...")
        
        comment_layout.addWidget(comment_label)
        comment_layout.addWidget(self.comment_input)
        comment_layout.addStretch()
        
        main_layout.addLayout(comment_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        save_btn = QPushButton("Save Account")
        save_btn.clicked.connect(self.save_account)
        save_btn.setFixedSize(120, 35)
        save_btn.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setFixedSize(120, 35)
        cancel_btn.setStyleSheet("""
            QPushButton { 
                background-color: #f44336; 
                color: white; 
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
    def create_aws_form(self):
        """Create AWS account form"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)
        
        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFixedWidth(120)
        email_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # Password with generate and copy buttons
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFixedWidth(120)
        password_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        
        self.pass_aws_input = QLineEdit()
        self.pass_aws_input.setText(PasswordGenerator.generate_password())
        self.pass_aws_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.pass_aws_input.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        generate_btn = QPushButton("Generate")
        generate_btn.setFixedSize(80, 30)
        generate_btn.setToolTip("Generate new password")
        generate_btn.clicked.connect(lambda: self.generate_new_password("aws"))
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        copy_btn = QPushButton("Copy")
        copy_btn.setFixedSize(60, 30)
        copy_btn.setToolTip("Copy password to clipboard")
        copy_btn.clicked.connect(lambda: self.copy_password("aws"))
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.pass_aws_input)
        password_layout.addWidget(generate_btn)
        password_layout.addWidget(copy_btn)
        layout.addLayout(password_layout)
        
        # MFA
        mfa_layout = QHBoxLayout()
        mfa_label = QLabel("MFA Secret Key:")
        mfa_label.setFixedWidth(120)
        mfa_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.mfa_input = QLineEdit()
        self.mfa_input.setPlaceholderText("Enter MFA secret key (optional)")
        self.mfa_input.setEchoMode(QLineEdit.EchoMode.Normal)
        mfa_layout.addWidget(mfa_label)
        mfa_layout.addWidget(self.mfa_input)
        layout.addLayout(mfa_layout)
        
        # Access Key
        access_key_layout = QHBoxLayout()
        access_key_label = QLabel("Access Key:")
        access_key_label.setFixedWidth(120)
        access_key_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.access_key_input = QLineEdit()
        self.access_key_input.setPlaceholderText("AKIA...")
        self.access_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        access_key_layout.addWidget(access_key_label)
        access_key_layout.addWidget(self.access_key_input)
        layout.addLayout(access_key_layout)
        
        # Secret Key
        secret_key_layout = QHBoxLayout()
        secret_key_label = QLabel("Secret Key:")
        secret_key_label.setFixedWidth(120)
        secret_key_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        secret_key_layout.addWidget(secret_key_label)
        secret_key_layout.addWidget(self.secret_key_input)
        layout.addLayout(secret_key_layout)
        
        # Region
        region_layout = QHBoxLayout()
        region_label = QLabel("Region:")
        region_label.setFixedWidth(120)
        region_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "US East (Ohio)",
            "US East (N. Virginia)",
            "US West (N. California)",
            "US West (Oregon)",
            "Asia Pacific (Mumbai)",
            "Asia Pacific (Osaka)",
            "Asia Pacific (Seoul)",
            "Asia Pacific (Singapore)",
            "Asia Pacific (Sydney)",
            "Asia Pacific (Tokyo)",
            "Canada (Central)",
            "Europe (Frankfurt)",
            "Europe (Ireland)",
            "Europe (London)",
            "Europe (Paris)",
            "Europe (Stockholm)",
            "South America (São Paulo)"
        ])
        self.region_combo.setCurrentText("US East (Ohio)")
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_combo)
        layout.addLayout(region_layout)
        
        # Registration Country
        country_layout = QHBoxLayout()
        country_label = QLabel("Registration Country:")
        country_label.setFixedWidth(120)
        country_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Enter registration country")
        country_layout.addWidget(country_label)
        country_layout.addWidget(self.country_input)
        layout.addLayout(country_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_digitalocean_form(self):
        """Create DigitalOcean account form"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)
        
        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFixedWidth(120)
        email_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.do_email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.do_email_input)
        layout.addLayout(email_layout)
        
        # Email Password with generate and copy
        email_pass_layout = QHBoxLayout()
        email_pass_label = QLabel("Pass Email (optional):")
        email_pass_label.setFixedWidth(120)
        email_pass_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        
        self.do_email_pass_input = QLineEdit()
        self.do_email_pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        
        generate_email_btn = QPushButton("Generate")
        generate_email_btn.setFixedSize(80, 30)
        generate_email_btn.setToolTip("Generate email password")
        generate_email_btn.clicked.connect(lambda: self.generate_new_password("do_email"))
        
        copy_email_btn = QPushButton("Copy")
        copy_email_btn.setFixedSize(60, 30)
        copy_email_btn.setToolTip("Copy email password")
        copy_email_btn.clicked.connect(lambda: self.copy_password("do_email"))
        
        email_pass_layout.addWidget(email_pass_label)
        email_pass_layout.addWidget(self.do_email_pass_input)
        email_pass_layout.addWidget(generate_email_btn)
        email_pass_layout.addWidget(copy_email_btn)
        layout.addLayout(email_pass_layout)
        
        # DO Password with generate and copy
        do_pass_layout = QHBoxLayout()
        do_pass_label = QLabel("Pass DO:")
        do_pass_label.setFixedWidth(120)
        do_pass_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        
        self.do_pass_input = QLineEdit()
        self.do_pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.do_pass_input.setText(PasswordGenerator.generate_password())
        self.do_pass_input.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        generate_do_btn = QPushButton("Generate")
        generate_do_btn.setFixedSize(80, 30)
        generate_do_btn.setToolTip("Generate DO password")
        generate_do_btn.clicked.connect(lambda: self.generate_new_password("do"))
        
        copy_do_btn = QPushButton("Copy")
        copy_do_btn.setFixedSize(60, 30)
        copy_do_btn.setToolTip("Copy DO password")
        copy_do_btn.clicked.connect(lambda: self.copy_password("do"))
        
        do_pass_layout.addWidget(do_pass_label)
        do_pass_layout.addWidget(self.do_pass_input)
        do_pass_layout.addWidget(generate_do_btn)
        do_pass_layout.addWidget(copy_do_btn)
        layout.addLayout(do_pass_layout)
        
        # 2FA
        do_2fa_layout = QHBoxLayout()
        do_2fa_label = QLabel("2FA Secret Key:")
        do_2fa_label.setFixedWidth(120)
        do_2fa_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.do_2fa_input = QLineEdit()
        self.do_2fa_input.setPlaceholderText("Enter 2FA secret key (optional)")
        self.do_2fa_input.setEchoMode(QLineEdit.EchoMode.Normal)
        do_2fa_layout.addWidget(do_2fa_label)
        do_2fa_layout.addWidget(self.do_2fa_input)
        layout.addLayout(do_2fa_layout)
        
        # Limits
        limits_layout = QHBoxLayout()
        limits_label = QLabel("Limits:")
        limits_label.setFixedWidth(120)
        limits_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.limits_input = QLineEdit()
        self.limits_input.setPlaceholderText("e.g., 10 droplets, $100/month")
        limits_layout.addWidget(limits_label)
        limits_layout.addWidget(self.limits_input)
        layout.addLayout(limits_layout)
        
        # Registration Country
        do_country_layout = QHBoxLayout()
        do_country_label = QLabel("Registration Country:")
        do_country_label.setFixedWidth(120)
        do_country_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.do_country_input = QLineEdit()
        self.do_country_input.setPlaceholderText("Enter registration country")
        do_country_layout.addWidget(do_country_label)
        do_country_layout.addWidget(self.do_country_input)
        layout.addLayout(do_country_layout)
        
        # Apply button styles
        for btn in [generate_email_btn, generate_do_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
        
        for btn in [copy_email_btn, copy_do_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
        
        widget.setLayout(layout)
        return widget
    
    def create_linode_form(self):
        """Create Linode account form"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)
        
        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFixedWidth(120)
        email_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.linode_email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.linode_email_input)
        layout.addLayout(email_layout)
        
        # Email Password with generate and copy
        email_pass_layout = QHBoxLayout()
        email_pass_label = QLabel("Pass Email (optional):")
        email_pass_label.setFixedWidth(120)
        email_pass_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        
        self.linode_email_pass_input = QLineEdit()
        self.linode_email_pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        
        generate_email_btn = QPushButton("Generate")
        generate_email_btn.setFixedSize(80, 30)
        generate_email_btn.setToolTip("Generate email password")
        generate_email_btn.clicked.connect(lambda: self.generate_new_password("linode_email"))
        
        copy_email_btn = QPushButton("Copy")
        copy_email_btn.setFixedSize(60, 30)
        copy_email_btn.setToolTip("Copy email password")
        copy_email_btn.clicked.connect(lambda: self.copy_password("linode_email"))
        
        email_pass_layout.addWidget(email_pass_label)
        email_pass_layout.addWidget(self.linode_email_pass_input)
        email_pass_layout.addWidget(generate_email_btn)
        email_pass_layout.addWidget(copy_email_btn)
        layout.addLayout(email_pass_layout)
        
        # Linode Login
        login_layout = QHBoxLayout()
        login_label = QLabel("Login Linode:")
        login_label.setFixedWidth(120)
        login_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.linode_login_input = QLineEdit()
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.linode_login_input)
        layout.addLayout(login_layout)
        
        # Linode Password with generate and copy
        linode_pass_layout = QHBoxLayout()
        linode_pass_label = QLabel("Pass Linode:")
        linode_pass_label.setFixedWidth(120)
        linode_pass_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        
        self.linode_pass_input = QLineEdit()
        self.linode_pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.linode_pass_input.setText(PasswordGenerator.generate_password())
        self.linode_pass_input.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        generate_linode_btn = QPushButton("Generate")
        generate_linode_btn.setFixedSize(80, 30)
        generate_linode_btn.setToolTip("Generate Linode password")
        generate_linode_btn.clicked.connect(lambda: self.generate_new_password("linode"))
        
        copy_linode_btn = QPushButton("Copy")
        copy_linode_btn.setFixedSize(60, 30)
        copy_linode_btn.setToolTip("Copy Linode password")
        copy_linode_btn.clicked.connect(lambda: self.copy_password("linode"))
        
        linode_pass_layout.addWidget(linode_pass_label)
        linode_pass_layout.addWidget(self.linode_pass_input)
        linode_pass_layout.addWidget(generate_linode_btn)
        linode_pass_layout.addWidget(copy_linode_btn)
        layout.addLayout(linode_pass_layout)
        
        # 2FA
        linode_2fa_layout = QHBoxLayout()
        linode_2fa_label = QLabel("2FA Secret Key:")
        linode_2fa_label.setFixedWidth(120)
        linode_2fa_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.linode_2fa_input = QLineEdit()
        self.linode_2fa_input.setPlaceholderText("Enter 2FA secret key (optional)")
        self.linode_2fa_input.setEchoMode(QLineEdit.EchoMode.Normal)
        linode_2fa_layout.addWidget(linode_2fa_label)
        linode_2fa_layout.addWidget(self.linode_2fa_input)
        layout.addLayout(linode_2fa_layout)
        
        # API KEY
        api_layout = QHBoxLayout()
        api_label = QLabel("API KEY (optional):")
        api_label.setFixedWidth(120)
        api_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.linode_api_input = QLineEdit()
        self.linode_api_input.setEchoMode(QLineEdit.EchoMode.Normal)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.linode_api_input)
        layout.addLayout(api_layout)
        
        # Payment method
        payment_layout = QHBoxLayout()
        payment_label = QLabel("Payment method:")
        payment_label.setFixedWidth(120)
        payment_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.linode_payment_combo = QComboBox()
        self.linode_payment_combo.addItems(["Card", "PayPal"])
        self.linode_payment_combo.setCurrentText("Card")
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.linode_payment_combo)
        layout.addLayout(payment_layout)
        
        # Registration Country
        linode_country_layout = QHBoxLayout()
        linode_country_label = QLabel("Registration Country:")
        linode_country_label.setFixedWidth(120)
        linode_country_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.linode_country_input = QLineEdit()
        self.linode_country_input.setPlaceholderText("Enter registration country")
        linode_country_layout.addWidget(linode_country_label)
        linode_country_layout.addWidget(self.linode_country_input)
        layout.addLayout(linode_country_layout)
        
        # Apply button styles
        for btn in [generate_email_btn, generate_linode_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
        
        for btn in [copy_email_btn, copy_linode_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
        
        widget.setLayout(layout)
        return widget
    
    def create_azure_form(self):
        """Create Azure account form"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)
        
        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFixedWidth(120)
        email_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.azure_email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.azure_email_input)
        layout.addLayout(email_layout)
        
        # Pass Azure with generate and copy
        azure_pass_layout = QHBoxLayout()
        azure_pass_label = QLabel("Pass Azure:")
        azure_pass_label.setFixedWidth(120)
        azure_pass_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        
        self.azure_pass_input = QLineEdit()
        self.azure_pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.azure_pass_input.setText(PasswordGenerator.generate_password())
        self.azure_pass_input.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        generate_azure_btn = QPushButton("Generate")
        generate_azure_btn.setFixedSize(80, 30)
        generate_azure_btn.setToolTip("Generate Azure password")
        generate_azure_btn.clicked.connect(lambda: self.generate_new_password("azure"))
        
        copy_azure_btn = QPushButton("Copy")
        copy_azure_btn.setFixedSize(60, 30)
        copy_azure_btn.setToolTip("Copy Azure password")
        copy_azure_btn.clicked.connect(lambda: self.copy_password("azure"))
        
        azure_pass_layout.addWidget(azure_pass_label)
        azure_pass_layout.addWidget(self.azure_pass_input)
        azure_pass_layout.addWidget(generate_azure_btn)
        azure_pass_layout.addWidget(copy_azure_btn)
        layout.addLayout(azure_pass_layout)
        
        # 2FA
        azure_2fa_layout = QHBoxLayout()
        azure_2fa_label = QLabel("2FA Secret Key:")
        azure_2fa_label.setFixedWidth(120)
        azure_2fa_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.azure_2fa_input = QLineEdit()
        self.azure_2fa_input.setPlaceholderText("2FA secret key (optional)")
        self.azure_2fa_input.setEchoMode(QLineEdit.EchoMode.Normal)
        azure_2fa_layout.addWidget(azure_2fa_label)
        azure_2fa_layout.addWidget(self.azure_2fa_input)
        layout.addLayout(azure_2fa_layout)
        
        # Subscription
        subscription_layout = QHBoxLayout()
        subscription_label = QLabel("Subscription:")
        subscription_label.setFixedWidth(120)
        subscription_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.azure_subscription_combo = QComboBox()
        self.azure_subscription_combo.addItems(["Pay as You Go", "Free Trial 200$"])
        self.azure_subscription_combo.setCurrentText("Pay as You Go")
        subscription_layout.addWidget(subscription_label)
        subscription_layout.addWidget(self.azure_subscription_combo)
        layout.addLayout(subscription_layout)
        
        # Registration Country
        azure_country_layout = QHBoxLayout()
        azure_country_label = QLabel("Registration Country:")
        azure_country_label.setFixedWidth(120)
        azure_country_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        self.azure_country_input = QLineEdit()
        self.azure_country_input.setPlaceholderText("Enter registration country")
        azure_country_layout.addWidget(azure_country_label)
        azure_country_layout.addWidget(self.azure_country_input)
        layout.addLayout(azure_country_layout)
        
        # Apply button styles
        generate_azure_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        copy_azure_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        widget.setLayout(layout)
        return widget
    
    def on_provider_changed(self, provider):
        """Handle provider selection change"""
        # Stop any existing timer
        if self.totp_timer:
            self.totp_timer.stop()
            self.totp_timer = None
        
        # Reset TOTP display
        self.first_totp_btn.setText("---")
        self.second_totp_btn.setText("---")
        self.timer_label.setText("--:--")
        
        # Reset current secret
        self.current_2fa_secret = ""
        self.prev_code = "---"
        self.curr_code = "---"
        self.next_code = "---"
        self.current_interval = -1
        
        # Switch widget
        if provider == "AWS":
            self.stacked_widget.setCurrentWidget(self.aws_widget)
        elif provider == "DigitalOcean":
            self.stacked_widget.setCurrentWidget(self.do_widget)
        elif provider == "Linode":
            self.stacked_widget.setCurrentWidget(self.linode_widget)
        elif provider == "Azure":
            self.stacked_widget.setCurrentWidget(self.azure_widget)
        
        #  меняем позицию окна! стаемся на том же месте
        if self.current_position:
            self.move(self.current_position)
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Connect all 2FA fields
        self.mfa_input.textChanged.connect(self.on_2fa_changed)
        self.do_2fa_input.textChanged.connect(self.on_2fa_changed)
        self.linode_2fa_input.textChanged.connect(self.on_2fa_changed)
        self.azure_2fa_input.textChanged.connect(self.on_2fa_changed)
        
        # Connect copy buttons for TOTP codes
        self.first_totp_btn.clicked.connect(lambda: self.copy_totp_code("first"))
        self.second_totp_btn.clicked.connect(lambda: self.copy_totp_code("second"))
    
    def on_2fa_changed(self):
        """Handle 2FA secret input changes for any provider"""
        # Get current provider's 2FA secret
        provider = self.provider_combo.currentText()
        
        if provider == "AWS":
            secret = self.mfa_input.text().strip()
        elif provider == "DigitalOcean":
            secret = self.do_2fa_input.text().strip()
        elif provider == "Linode":
            secret = self.linode_2fa_input.text().strip()
        elif provider == "Azure":
            secret = self.azure_2fa_input.text().strip()
        else:
            secret = ""
        
        self.handle_2fa_secret(secret)
    
    def handle_2fa_secret(self, secret):
        """Handle 2FA secret with correct sliding logic"""
        # Stop existing timer
        if self.totp_timer:
            self.totp_timer.stop()
            self.totp_timer = None
        
        # Reset codes
        self.prev_code = "---"
        self.curr_code = "---"
        self.next_code = "---"
        self.current_interval = -1
        
        # Update display
        self.first_totp_btn.setText("---")
        self.second_totp_btn.setText("---")
        self.timer_label.setText("--:--")
        
        # Start new timer if secret is valid
        if secret and PYOTP_AVAILABLE:
            self.current_2fa_secret = secret
            self.start_totp_timer(secret)
        else:
            self.current_2fa_secret = ""
    
    def apply_theme(self):
        """Apply dark theme by default with proper arrow"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #cccccc;
            }
            QLabel[style*="font-weight: bold"] {
                color: #cccccc;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 6px;
                border-radius: 4px;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 6px;
                border-radius: 4px;
                padding-right: 20px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                border: none;
                image: url(data:image/svg+xml;utf8,<svg fill="white" height="12" viewBox="0 0 12 12" width="12" xmlns="http://www.w3.org/2000/svg"><path d="M0 4l6 6 6-6z"/></svg>);
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                selection-background-color: #0078d4;
                border: 1px solid #555555;
            }
        """)
        
    def generate_new_password(self, field_type):
        """Generate new password for specific field"""
        new_password = PasswordGenerator.generate_password()
        
        if field_type == "aws":
            self.pass_aws_input.setText(new_password)
            field = self.pass_aws_input
        elif field_type == "do_email":
            self.do_email_pass_input.setText(new_password)
            field = self.do_email_pass_input
        elif field_type == "do":
            self.do_pass_input.setText(new_password)
            field = self.do_pass_input
        elif field_type == "linode_email":
            self.linode_email_pass_input.setText(new_password)
            field = self.linode_email_pass_input
        elif field_type == "linode":
            self.linode_pass_input.setText(new_password)
            field = self.linode_pass_input
        elif field_type == "azure":
            self.azure_pass_input.setText(new_password)
            field = self.azure_pass_input
        else:
            return
        
        # Visual feedback
        original_style = field.styleSheet()
        field.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                border: 1px solid #28a745;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        QTimer.singleShot(1000, lambda: field.setStyleSheet(original_style))
    
    def copy_password(self, field_type):
        """Copy password to clipboard"""
        if field_type == "aws":
            text = self.pass_aws_input.text()
        elif field_type == "do_email":
            text = self.do_email_pass_input.text()
        elif field_type == "do":
            text = self.do_pass_input.text()
        elif field_type == "linode_email":
            text = self.linode_email_pass_input.text()
        elif field_type == "linode":
            text = self.linode_pass_input.text()
        elif field_type == "azure":
            text = self.azure_pass_input.text()
        else:
            return
        
        if text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            
            # Visual feedback
            if field_type == "aws":
                field = self.pass_aws_input
            elif field_type == "do_email":
                field = self.do_email_pass_input
            elif field_type == "do":
                field = self.do_pass_input
            elif field_type == "linode_email":
                field = self.linode_email_pass_input
            elif field_type == "linode":
                field = self.linode_pass_input
            elif field_type == "azure":
                field = self.azure_pass_input
            
            original_style = field.styleSheet()
            field.setStyleSheet("""
                QLineEdit {
                    background-color: #007bff;
                    border: 1px solid #0056b3;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                    color: #ffffff;
                }
            """)
            
            QTimer.singleShot(300, lambda: field.setStyleSheet(original_style))
    
    def start_totp_timer(self, secret):
        """Start TOTP timer to update codes"""
        if self.totp_timer:
            self.totp_timer.stop()
        
        self.totp_timer = QTimer()
        self.totp_timer.timeout.connect(lambda: self.update_totp_codes())
        self.totp_timer.start(100)  # Update every 100ms
        self.current_2fa_secret = secret
        
        # Initial update
        self.update_totp_codes()
    
    def update_totp_codes(self):
        """Update TOTP codes with correct sliding logic"""
        if not PYOTP_AVAILABLE or not self.current_2fa_secret:
            return
            
        try:
            # Clean the secret
            clean_secret = self.current_2fa_secret.replace(" ", "").upper()
            totp = pyotp.TOTP(clean_secret)
            
            current_time = time.time()
            current_interval = int(current_time / 30)
            time_remaining = 30 - (current_time % 30)
            
            # Format timer as seconds
            timer_text = f"{int(time_remaining):02d}"
            self.timer_label.setText(timer_text)
            
            # сли это первый запуск или интервал изменился
            if self.current_interval != current_interval:
                # олучаем новый код
                new_code = totp.at(current_interval * 30)
                
                #  Т:
                # 1. ри первом вводе ключа: первый код в первое поле, второе пустое
                # 2. ри появлении второго кода: второй код во второе поле
                # 3. ри появлении третьего кода: второй код в первое поле, третий во второе
                
                if self.curr_code == "---" and self.next_code == "---":
                    # ервый код после ввода ключа
                    self.curr_code = new_code
                    self.first_totp_btn.setText(self.curr_code)
                    self.second_totp_btn.setText("---")
                elif self.next_code == "---":
                    # торой код появился
                    self.next_code = new_code
                    self.second_totp_btn.setText(self.next_code)
                else:
                    # Третий и последующие коды - прокрутка
                    self.prev_code = self.curr_code
                    self.curr_code = self.next_code
                    self.next_code = new_code
                    
                    # бновляем отображение
                    self.first_totp_btn.setText(self.curr_code)  # редыдущий становится текущим
                    self.second_totp_btn.setText(self.next_code)  # Текущий становится следующим
                
                # бновляем текущий интервал
                self.current_interval = current_interval
            
            # ветовая индикация времени
            if time_remaining > 10:
                color = "#28a745"  # Green
            elif time_remaining > 5:
                color = "#ffc107"  # Yellow
            else:
                color = "#dc3545"  # Red
            
            self.first_totp_btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 12px;
                    font-weight: bold;
                    color: {color};
                    padding: 5px;
                    border: 1px solid {color};
                    border-radius: 4px;
                    background-color: rgba({color[1:]}, 0.1);
                }}
                QPushButton:hover {{
                    background-color: rgba({color[1:]}, 0.2);
                }}
            """)
            
        except Exception as e:
            self.first_totp_btn.setText("Invalid")
            self.second_totp_btn.setText("Format")
            self.timer_label.setText("Error")
            
    def copy_totp_code(self, code_type):
        """Copy TOTP code to clipboard"""
        if code_type == "first":
            text = self.first_totp_btn.text()
        else:
            text = self.second_totp_btn.text()
        
        if text and text != "---" and text != "Invalid" and text != "Format":
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            
            # изуальная обратная связь
            original_style = self.first_totp_btn.styleSheet()
            self.first_totp_btn.setStyleSheet(original_style + """
                background-color: #007bff !important;
                border: 1px solid #0056b3 !important;
            """)
            
            QTimer.singleShot(300, lambda: self.update_totp_codes())
    
    def get_account_data(self):
        """Get account data from form"""
        provider = self.provider_combo.currentText()
        
        data = {
            "provider": provider,
            "comment": self.comment_input.toPlainText().strip()
        }
        
        if provider == "AWS":
            data.update({
                "email": self.email_input.text().strip(),
                "password": self.pass_aws_input.text().strip(),
                "mfa_secret": self.mfa_input.text().strip(),
                "access_key": self.access_key_input.text().strip(),
                "secret_key": self.secret_key_input.text().strip(),
                "region": self.region_combo.currentText(),
                "country": self.country_input.text().strip()
            })
        elif provider == "DigitalOcean":
            data.update({
                "email": self.do_email_input.text().strip(),
                "email_password": self.do_email_pass_input.text().strip(),
                "do_password": self.do_pass_input.text().strip(),
                "2fa_secret": self.do_2fa_input.text().strip(),
                "limits": self.limits_input.text().strip(),
                "country": self.do_country_input.text().strip()
            })
        elif provider == "Linode":
            data.update({
                "email": self.linode_email_input.text().strip(),
                "email_password": self.linode_email_pass_input.text().strip(),
                "linode_login": self.linode_login_input.text().strip(),
                "linode_password": self.linode_pass_input.text().strip(),
                "2fa_secret": self.linode_2fa_input.text().strip(),
                "api_key": self.linode_api_input.text().strip(),
                "payment_method": self.linode_payment_combo.currentText(),
                "country": self.linode_country_input.text().strip()
            })
        elif provider == "Azure":
            data.update({
                "email": self.azure_email_input.text().strip(),
                "azure_password": self.azure_pass_input.text().strip(),
                "2fa_secret": self.azure_2fa_input.text().strip(),
                "subscription": self.azure_subscription_combo.currentText(),
                "country": self.azure_country_input.text().strip()
            })
        
        return data
    
    def validate_data(self, data):
        """Validate form data"""
        provider = data["provider"]
        
        if provider == "AWS":
            required_fields = ["email", "password", "access_key", "secret_key"]
        elif provider == "DigitalOcean":
            required_fields = ["email", "do_password"]
        elif provider == "Linode":
            required_fields = ["email", "linode_login", "linode_password"]
        elif provider == "Azure":
            required_fields = ["email", "azure_password"]
        else:
            return False, "Unknown provider"
        
        for field in required_fields:
            if not data.get(field):
                return False, f"Field '{field}' is required"
        
        return True, ""
    
    def save_account(self):
        account_data = self.get_account_data()
        is_valid, error_msg = self.validate_data(account_data)
        
        if not is_valid:
            QMessageBox.warning(self, "Error", error_msg)
            return
        
        # Emit signal with account data
        self.account_added.emit(account_data)
        
        # Show success message
        QMessageBox.information(self, "Success", f"{account_data['provider']} account saved successfully!")
        
        self.accept()
    
    def closeEvent(self, event):
        """Clean up timers on close"""
        if self.totp_timer:
            self.totp_timer.stop()
        event.accept()
