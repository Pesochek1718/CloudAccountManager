"""
Filters component for Cloud Account Manager
"""

from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QComboBox, QPushButton

def create_filter_panel(window):
    """Create compact filter panel"""
    group = QGroupBox("🔍 Filters")
    group.setMaximumHeight(80)
    group.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            font-size: 12px;
            border: 1px solid #6c757d;
            border-radius: 6px;
            margin-top: 6px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 6px 0 6px;
        }
    """)
    
    layout = QHBoxLayout()
    layout.setSpacing(8)
    layout.setContentsMargins(8, 15, 8, 8)
    
    # Provider filter
    provider_label = QLabel("Provider:")
    window.provider_filter = QComboBox()
    window.provider_filter.addItems(["All", "AWS", "Linode", "Digital Ocean"])
    window.provider_filter.setMinimumWidth(120)
    window.provider_filter.setMaximumWidth(150)
    
    # Region filter
    region_label = QLabel("Region:")
    window.region_filter = QComboBox()
    window.region_filter.addItems(["All"])
    window.region_filter.setMinimumWidth(120)
    window.region_filter.setMaximumWidth(150)
    
    # Status filter
    status_label = QLabel("Status:")
    window.status_filter = QComboBox()
    window.status_filter.addItems(["All", "✅ Active", "❌ Error"])
    window.status_filter.setMinimumWidth(120)
    window.status_filter.setMaximumWidth(150)
    
    # Quota filter
    quota_label = QLabel("Quota:")
    window.quota_filter = QComboBox()
    window.quota_filter.addItems(["All", "Low (<20%)", "Medium (20-80%)", "High (>80%)", "3/10", "10/10"])
    window.quota_filter.setMinimumWidth(120)
    window.quota_filter.setMaximumWidth(150)
    
    # Reset button
    reset_btn = QPushButton("Reset Filters")
    reset_btn.setFixedHeight(28)
    reset_btn.setMinimumWidth(100)
    reset_btn.clicked.connect(window.reset_filters)
    reset_btn.setStyleSheet("""
        QPushButton {
            background-color: #6c757d;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #5a6268;
        }
    """)
    
    # Add widgets to layout
    layout.addWidget(provider_label)
    layout.addWidget(window.provider_filter)
    layout.addSpacing(10)
    
    layout.addWidget(region_label)
    layout.addWidget(window.region_filter)
    layout.addSpacing(10)
    
    layout.addWidget(status_label)
    layout.addWidget(window.status_filter)
    layout.addSpacing(10)
    
    layout.addWidget(quota_label)
    layout.addWidget(window.quota_filter)
    layout.addSpacing(20)
    
    layout.addWidget(reset_btn)
    layout.addStretch()
    
    group.setLayout(layout)
    return group
