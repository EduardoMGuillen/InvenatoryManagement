import json
import os
from PyQt6.QtCore import QObject, pyqtSignal

class SettingsManager(QObject):
    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings_file = "settings.json"
        self.default_settings = {
            # Appearance
            "theme": "light",
            "font_size": 14,
            "accent_color": "#3498db",
            
            # Company Information
            "company_name": "Mi Empresa",
            "company_address": "Dirección de la Empresa",
            "company_phone": "9999-9999",
            "company_email": "contacto@empresa.com",
            "company_rtn": "0000-000000-000-0",
            
            # Currency Settings
            "currency": "LPS",
            "currency_symbol": "L",
            "currency_position": "before",  # before or after
            "decimal_separator": ".",
            "thousands_separator": ",",
            
            # Invoice Settings
            "tax_rate": 15.0,
            "invoice_prefix": "FAC",
            "invoice_folder": "invoices",
            
            # Database
            "backup_enabled": True,
            "backup_interval_days": 7,
            "backup_folder": "backups",
            
            # Default Values
            "default_product_quantity": 1,
            "default_product_cost": 0.0,
            "default_product_price": 0.0,
            
            # Language
            "language": "es",
            
            # Recent Items
            "max_recent_items": 10,
            
            # Auto-save
            "auto_save_enabled": True,
            "auto_save_interval_minutes": 5
        }
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from file or create with defaults if not exists."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Ensure all default settings exist
                    for key, value in self.default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.default_settings.copy()
        else:
            return self.default_settings.copy()

    def save_settings(self):
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            self.settings_changed.emit()
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get_setting(self, key, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        """Set a setting value and save."""
        self.settings[key] = value
        return self.save_settings()

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings = self.default_settings.copy()
        return self.save_settings()

    def get_all_settings(self):
        """Get all current settings."""
        return self.settings.copy() 