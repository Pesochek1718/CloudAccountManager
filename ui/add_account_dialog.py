"""
Add Account Dialog for AWS
Modal window for adding new AWS accounts
"""

import os
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QGroupBox, QMessageBox, QTextEdit,
    QApplication, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QGuiApplication, QClipboard
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
    """Dialog for adding new AWS accounts"""
    
    account_added = pyqtSignal(dict)  # Signal emitted when account is added
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add AWS Account")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(450)
        
        # Get theme from parent
        self.dark_mode = getattr(parent, 'dark_mode', True) if parent else True
        
        self.totp_timer = None
        self.current_totp = None
        self.prev_totp = None
        
        self.init_ui()
        self.setup_connections()
        self.apply_theme()
        
        # Center dialog relative to parent
        if self.parent():
            self.move(self.parent().frameGeometry().center() - self.rect().center())
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        
        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFixedWidth(150)
        email_label.setStyleSheet("font-weight: bold;")
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        main_layout.addLayout(email_layout)
        
        # Password with generate button
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFixedWidth(150)
        password_label.setStyleSheet("font-weight: bold;")
        
        self.pass_aws_input = QLineEdit()
        self.pass_aws_input.setText(PasswordGenerator.generate_password())
        self.pass_aws_input.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                border: 2px solid #c3e6cb;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        generate_btn = QPushButton("Generate")
        generate_btn.setFixedWidth(80)
        generate_btn.setToolTip("Generate new password")
        generate_btn.clicked.connect(self.generate_new_password)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.pass_aws_input)
        password_layout.addWidget(generate_btn)
        main_layout.addLayout(password_layout)
        
        # MFA
        mfa_layout = QHBoxLayout()
        mfa_label = QLabel("MFA:")
        mfa_label.setFixedWidth(150)
        mfa_label.setStyleSheet("font-weight: bold;")
        self.mfa_input = QLineEdit()
        self.mfa_input.setPlaceholderText("Enter MFA secret key")
        mfa_layout.addWidget(mfa_label)
        mfa_layout.addWidget(self.mfa_input)
        main_layout.addLayout(mfa_layout)
        
        # TOTP Codes Display (2 codes - current and next)
        self.totp_frame = QFrame()
        self.totp_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.totp_frame.setVisible(False)
        
        totp_layout = QVBoxLayout(self.totp_frame)
        
        # Current TOTP
        self.current_totp_label = QLabel("Current TOTP: ---")
        self.current_totp_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #28a745;
                padding: 5px;
            }
        """)
        self.current_totp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Next TOTP
        self.next_totp_label = QLabel("Next TOTP: ---")
        self.next_totp_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #6c757d;
                padding: 5px;
            }
        """)
        self.next_totp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Timer label
        self.timer_label = QLabel("Time left: 30s")
        self.timer_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                padding: 3px;
                font-style: italic;
            }
        """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        totp_layout.addWidget(self.current_totp_label)
        totp_layout.addWidget(self.next_totp_label)
        totp_layout.addWidget(self.timer_label)
        
        main_layout.addWidget(self.totp_frame)
        
        # Access Key
        access_key_layout = QHBoxLayout()
        access_key_label = QLabel("Access Key:")
        access_key_label.setFixedWidth(150)
        access_key_label.setStyleSheet("font-weight: bold;")
        self.access_key_input = QLineEdit()
        self.access_key_input.setPlaceholderText("AKIA...")
        access_key_layout.addWidget(access_key_label)
        access_key_layout.addWidget(self.access_key_input)
        main_layout.addLayout(access_key_layout)
        
        # Secret Key
        secret_key_layout = QHBoxLayout()
        secret_key_label = QLabel("Secret Key:")
        secret_key_label.setFixedWidth(150)
        secret_key_label.setStyleSheet("font-weight: bold;")
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        secret_key_layout.addWidget(secret_key_label)
        secret_key_layout.addWidget(self.secret_key_input)
        main_layout.addLayout(secret_key_layout)
        
        # Region
        region_layout = QHBoxLayout()
        region_label = QLabel("Region:")
        region_label.setFixedWidth(150)
        region_label.setStyleSheet("font-weight: bold;")
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
        main_layout.addLayout(region_layout)
        
        # Registration Country (без выпадающего)
        country_layout = QHBoxLayout()
        country_label = QLabel("Registration Country:")
        country_label.setFixedWidth(150)
        country_label.setStyleSheet("font-weight: bold;")
        self.country_input = QLineEdit()
        self.country_input.setText("United States")
        country_layout.addWidget(country_label)
        country_layout.addWidget(self.country_input)
        main_layout.addLayout(country_layout)
        
        # Comment
        comment_layout = QHBoxLayout()
        comment_label = QLabel("Comment:")
        comment_label.setFixedWidth(150)
        comment_label.setStyleSheet("font-weight: bold;")
        self.comment_input = QTextEdit()
        self.comment_input.setMaximumHeight(60)
        self.comment_input.setPlaceholderText("Optional comment...")
        comment_layout.addWidget(comment_label)
        comment_layout.addWidget(self.comment_input)
        main_layout.addLayout(comment_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Account")
        save_btn.clicked.connect(self.save_account)
        save_btn.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                padding: 10px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton { 
                background-color: #f44336; 
                color: white; 
                padding: 10px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def setup_connections(self):
        """Setup signal-slot connections"""
        self.mfa_input.textChanged.connect(self.on_mfa_changed)
        
        # Make TOTP labels clickable to copy
        self.current_totp_label.mousePressEvent = lambda e: self.copy_to_clipboard(self.current_totp_label.text().replace("Current TOTP: ", ""))
        self.next_totp_label.mousePressEvent = lambda e: self.copy_to_clipboard(self.next_totp_label.text().replace("Next TOTP: ", ""))
        
    def apply_theme(self):
        """Apply theme colors"""
        if self.dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel[style*="font-weight: bold"] {
                    color: #cccccc;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 8px;
                    border-radius: 4px;
                }
                QTextEdit {
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                    color: #212529;
                }
                QLabel[style*="font-weight: bold"] {
                    color: #495057;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #ffffff;
                    color: #212529;
                    border: 1px solid #ced4da;
                    padding: 8px;
                    border-radius: 4px;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #212529;
                }
            """)
        
    def generate_new_password(self):
        new_password = PasswordGenerator.generate_password()
        self.pass_aws_input.setText(new_password)
        
        self.pass_aws_input.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                border: 2px solid #28a745;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        QTimer.singleShot(1000, lambda: self.pass_aws_input.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                border: 2px solid #c3e6cb;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                color: #000000;
            }
        """))
    
    def on_mfa_changed(self):
        """Handle MFA secret input changes"""
        mfa_secret = self.mfa_input.text().strip()
        
        if mfa_secret and PYOTP_AVAILABLE:
            self.totp_frame.setVisible(True)
            self.start_totp_timer(mfa_secret)
        else:
            self.totp_frame.setVisible(False)
            if self.totp_timer:
                self.totp_timer.stop()
                self.totp_timer = None
    
    def start_totp_timer(self, mfa_secret):
        """Start TOTP timer to update codes"""
        if self.totp_timer:
            self.totp_timer.stop()
        
        self.totp_timer = QTimer()
        self.totp_timer.timeout.connect(lambda: self.update_totp_codes(mfa_secret))
        self.totp_timer.start(100)  # Update every 100ms for smooth timer
        self.update_totp_codes(mfa_secret)  # Initial update
    
    def update_totp_codes(self, mfa_secret):
        """Update both current and next TOTP codes"""
        if not PYOTP_AVAILABLE:
            return
            
        try:
            # Clean the secret
            clean_secret = mfa_secret.replace(" ", "").upper()
            totp = pyotp.TOTP(clean_secret)
            
            current_time = time.time()
            current_interval = int(current_time / 30)
            
            # Get current and next codes
            current_code = totp.at(current_interval * 30)
            next_code = totp.at((current_interval + 1) * 30)
            
            # Calculate time remaining
            time_remaining = 30 - (current_time % 30)
            
            # Update labels
            self.current_totp_label.setText(f"Current TOTP: {current_code}")
            self.next_totp_label.setText(f"Next TOTP: {next_code}")
            self.timer_label.setText(f"Time left: {int(time_remaining)}s")
            
            # Color coding based on time remaining
            if time_remaining > 10:
                color = "#28a745"  # Green
            elif time_remaining > 5:
                color = "#ffc107"  # Yellow
            else:
                color = "#dc3545"  # Red
            
            self.current_totp_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 16px;
                    font-weight: bold;
                    color: {color};
                    padding: 5px;
                }}
            """)
            
            # Change cursor to indicate clickability
            self.current_totp_label.setCursor(Qt.CursorShape.PointingHandCursor)
            self.next_totp_label.setCursor(Qt.CursorShape.PointingHandCursor)
            
        except Exception as e:
            self.current_totp_label.setText(f"Current TOTP: Invalid MFA")
            self.next_totp_label.setText(f"Next TOTP: ---")
            self.timer_label.setText(f"Check MFA secret format")
            
    def copy_to_clipboard(self, text):
        """Copy text to clipboard with visual feedback"""
        if text and text != "---" and "Invalid" not in text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            
            # Visual feedback
            original_style = self.current_totp_label.styleSheet()
            self.current_totp_label.setStyleSheet(original_style + """
                background-color: #007bff;
                border-radius: 4px;
            """)
            
            QTimer.singleShot(300, lambda: self.current_totp_label.setStyleSheet(original_style))
    
    def get_account_data(self):
        """Get account data from form"""
        return {
            "provider": "AWS",
            "email": self.email_input.text().strip(),
            "password": self.pass_aws_input.text().strip(),
            "mfa_secret": self.mfa_input.text().strip(),
            "access_key": self.access_key_input.text().strip(),
            "secret_key": self.secret_key_input.text().strip(),
            "region": self.region_combo.currentText(),
            "country": self.country_input.text().strip(),
            "comment": self.comment_input.toPlainText().strip()
        }
    
    def validate_data(self, data):
        """Validate form data"""
        required_fields = ["email", "password", "access_key", "secret_key"]
        for field in required_fields:
            if not data[field]:
                return False, f"Field {field} is required"
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
        QMessageBox.information(self, "Success", "Account saved successfully!")
        
        self.accept()
    
    def closeEvent(self, event):
        """Clean up timers on close"""
        if self.totp_timer:
            self.totp_timer.stop()
        event.accept()
