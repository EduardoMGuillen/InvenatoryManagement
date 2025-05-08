from PyQt6.QtCore import QObject

class CurrencyFormatter(QObject):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager

    def format_amount(self, amount):
        """Format an amount according to currency settings."""
        try:
            return f"LPS {float(amount):,.2f}"
        except:
            return "LPS 0.00"

    def parse_amount(self, formatted_amount):
        """Parse a formatted amount string back to float."""
        try:
            # Remove 'LPS' and spaces, then convert to float
            amount_str = formatted_amount.replace("LPS", "").strip()
            amount_str = amount_str.replace(",", "")
            return float(amount_str)
        except:
            return 0.0 