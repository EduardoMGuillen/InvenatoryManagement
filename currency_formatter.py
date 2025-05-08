from PyQt6.QtCore import QObject

class CurrencyFormatter(QObject):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager

    def format_amount(self, amount):
        """Format an amount according to currency settings."""
        currency = self.settings_manager.get_setting("currency")
        symbol = self.settings_manager.get_setting("currency_symbol")
        position = self.settings_manager.get_setting("currency_position")
        decimal_sep = self.settings_manager.get_setting("decimal_separator")
        thousands_sep = self.settings_manager.get_setting("thousands_separator")

        # Format the number with separators
        formatted = f"{amount:,.2f}".replace(",", thousands_sep).replace(".", decimal_sep)

        # Add currency symbol
        if position == "before":
            return f"{symbol} {formatted}"
        else:
            return f"{formatted} {symbol}"

    def parse_amount(self, formatted_amount):
        """Parse a formatted amount string back to float."""
        try:
            # Remove currency symbol and spaces
            amount_str = formatted_amount.replace(self.settings_manager.get_setting("currency_symbol"), "").strip()
            
            # Replace separators
            decimal_sep = self.settings_manager.get_setting("decimal_separator")
            thousands_sep = self.settings_manager.get_setting("thousands_separator")
            
            amount_str = amount_str.replace(thousands_sep, "").replace(decimal_sep, ".")
            
            return float(amount_str)
        except:
            return 0.0 