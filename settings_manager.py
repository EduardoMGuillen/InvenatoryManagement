import json
import os
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

class SettingsManager(QObject):
    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = QSettings("BizztrackPro", "InventoryManagement")
        self.set_default_settings()
        self.force_update_smtp_settings()  # Force update SMTP settings

    def force_update_smtp_settings(self):
        """Force update the SMTP settings."""
        self.settings.setValue("smtp_username", "bizztrackpro@gmail.com")
        self.settings.setValue("smtp_password", "zwxhhgnkoqdmrtww")
        self.settings.setValue("smtp_server", "smtp.gmail.com")
        self.settings.setValue("smtp_port", 587)
        self.settings.sync()
        
        # Verify settings
        print("Debug - Current SMTP Settings:")
        print(f"Username: {self.settings.value('smtp_username')}")
        print(f"Password length: {len(self.settings.value('smtp_password', ''))}")
        print(f"Server: {self.settings.value('smtp_server')}")
        print(f"Port: {self.settings.value('smtp_port')}")

    def set_default_settings(self):
        # Set default values if they don't exist
        defaults = {
            # Appearance
            "theme": "light",
            "font_size": 12,
            "accent_color": "#3498db",  # Default blue accent color
            
            # Company Info
            "company_name": "Mi Empresa",
            "company_address": "",
            "company_phone": "",
            
            # Invoice Settings
            "invoice_prefix": "FAC",
            "invoice_folder": "invoices",
            "tax_rate": 15.0,
            
            # Backup settings
            "backup_recipient_email": "",  # User will set this in settings
            "backup_frequency": "daily",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "bizztrackpro@gmail.com",  # Fixed sender
            "smtp_password": "zwxhhgnkoqdmrtww",  # App password
            "last_backup": None
        }
        
        # Set default values with proper types
        for key, value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)
        
        self.settings.sync()

    def get_setting(self, key, default=None):
        """Get a setting value with proper type conversion."""
        value = self.settings.value(key, default)
        
        # Handle type conversion based on the setting key
        if key in ["font_size", "smtp_port"]:
            try:
                return int(value)
            except (TypeError, ValueError):
                return default if default is not None else 0
        elif key in ["tax_rate"]:
            try:
                return float(value)
            except (TypeError, ValueError):
                return default if default is not None else 0.0
        else:
            return value

    def set_setting(self, key, value):
        """Set a setting value."""
        self.settings.setValue(key, value)
        self.settings.sync()
        self.settings_changed.emit()

    def reset_to_defaults(self):
        self.settings.clear()
        self.set_default_settings()
        self.settings_changed.emit()

    def get_all_settings(self):
        """Get all current settings."""
        return self.settings.allKeys() 