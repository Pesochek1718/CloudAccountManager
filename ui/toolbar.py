"""
Toolbar component for Cloud Account Manager
"""

import os
import sys
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QDesktopServices

def create_toolbar(window):
    """Create toolbar with buttons on left, logo and link on right"""
    toolbar_layout = QHBoxLayout()
    toolbar_layout.setSpacing(10)
    
    # нопки слева
    buttons = [
        ("➕ Add Account", window.add_account, "#28a745"),
        ("🔍 Check Selected", window.check_selected, "#17a2b8"),
        ("📋 Copy Selected", window.copy_selected, "#6f42c1"),
        ("🗑️ Delete Selected", window.delete_selected, "#dc3545"),
    ]
    
    for text, slot, color in buttons:
        btn = QPushButton(text)
        btn.clicked.connect(slot)
        btn.setFixedHeight(32)
        btn.setMinimumWidth(120)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {_darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {_darken_color(color, 40)};
            }}
        """)
        toolbar_layout.addWidget(btn)
    
    # астягиваем пространство между кнопками и логотипом
    toolbar_layout.addStretch()
    
    # оготип и ссылка справа
    right_container = QHBoxLayout()
    right_container.setSpacing(10)
    
    # ытаемся найти логотип в разных местах
    logo_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png"),
        os.path.join(os.getcwd(), "logo.png"),
        "logo.png"
    ]
    
    logo_loaded = False
    
    for path in logo_paths:
        if os.path.exists(path):
            try:
                # робуем загрузить логотип
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    print(f"✅ оготип загружен из: {path}")
                    print(f"✅ азмер логотипа: {pixmap.width()}x{pixmap.height()}")
                    
                    # Создаем QLabel для логотипа
                    logo_label = QLabel()
                    #  размер логотипа (высота 50px)
                    scaled_pixmap = pixmap.scaledToHeight(50, Qt.TransformationMode.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                    logo_label.setToolTip("Cloud Account Manager")
                    right_container.addWidget(logo_label)
                    logo_loaded = True
                    break
                else:
                    print(f"⚠️ е удалось загрузить логотип из: {path}")
            except Exception as e:
                print(f"⚠️ шибка при загрузке логотипа из {path}: {e}")
    
    # сли логотип не загрузился, показываем текст
    if not logo_loaded:
        print("⚠️ оготип не найден или не загрузился")
        text_label = QLabel("☁️")
        text_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #007bff;
                font-weight: bold;
                padding: 5px;
            }
        """)
        right_container.addWidget(text_label)
    
    # Ссылка на бота - ЬШ 
    bot_label = QLabel()
    bot_label.setText('<a href="https://t.me/CloudStorm_bot" style="color: #007bff; text-decoration: none;">@CloudStorm_bot</a>')
    bot_label.setTextFormat(Qt.TextFormat.RichText)
    bot_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    bot_label.setOpenExternalLinks(True)
    
    # станавливаем ЬШ шрифт для ссылки
    bot_label.setStyleSheet("""
        QLabel {
            color: #007bff;
            font-size: 16px;  /*  с 12px до 16px */
            font-weight: bold;
            padding: 5px;
        }
        QLabel:hover {
            text-decoration: underline;
            color: #0056b3;
        }
    """)
    
    bot_label.setCursor(Qt.CursorShape.PointingHandCursor)
    right_container.addWidget(bot_label)
    
    # обавляем правый контейнер в основной layout
    toolbar_layout.addLayout(right_container)
        
    return toolbar_layout

def _darken_color(hex_color, amount=20):
    """Darken a hex color"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    r = max(0, r - amount)
    g = max(0, g - amount)
    b = max(0, b - amount)
    
    return f'#{r:02x}{g:02x}{b:02x}'
