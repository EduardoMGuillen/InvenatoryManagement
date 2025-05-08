import os
import shutil
import datetime
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class BackupManager(QObject):
    backup_completed = pyqtSignal(str)  # Signal emitted when backup is completed
    backup_failed = pyqtSignal(str)     # Signal emitted when backup fails

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_backup)
        self.last_backup = None
        self.load_last_backup_time()

    def load_last_backup_time(self):
        """Load the last backup time from a file."""
        try:
            if os.path.exists("last_backup.txt"):
                with open("last_backup.txt", "r") as f:
                    self.last_backup = datetime.datetime.fromisoformat(f.read().strip())
        except Exception as e:
            print(f"Error loading last backup time: {e}")
            self.last_backup = None

    def save_last_backup_time(self):
        """Save the current time as the last backup time."""
        try:
            with open("last_backup.txt", "w") as f:
                f.write(datetime.datetime.now().isoformat())
        except Exception as e:
            print(f"Error saving last backup time: {e}")

    def start_backup_timer(self):
        """Start the backup timer if enabled in settings."""
        if self.settings_manager.get_setting("backup_enabled"):
            # Convert days to milliseconds
            interval = self.settings_manager.get_setting("backup_interval_days") * 24 * 60 * 60 * 1000
            self.timer.start(interval)
        else:
            self.timer.stop()

    def check_backup(self):
        """Check if it's time to perform a backup."""
        if not self.settings_manager.get_setting("backup_enabled"):
            return

        now = datetime.datetime.now()
        if self.last_backup is None or (now - self.last_backup).days >= self.settings_manager.get_setting("backup_interval_days"):
            self.perform_backup()

    def perform_backup(self):
        """Perform a backup of the database."""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = self.settings_manager.get_setting("backup_folder")
            os.makedirs(backup_dir, exist_ok=True)

            # Generate backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"backup_{timestamp}.db")

            # Copy the database file
            shutil.copy2("inventory.db", backup_file)

            # Update last backup time
            self.last_backup = datetime.datetime.now()
            self.save_last_backup_time()

            # Clean up old backups (keep last 5)
            self.cleanup_old_backups()

            self.backup_completed.emit(f"Backup completed successfully: {backup_file}")
        except Exception as e:
            self.backup_failed.emit(f"Backup failed: {str(e)}")

    def cleanup_old_backups(self):
        """Keep only the last 5 backups."""
        try:
            backup_dir = self.settings_manager.get_setting("backup_folder")
            backups = [f for f in os.listdir(backup_dir) if f.startswith("backup_") and f.endswith(".db")]
            backups.sort(reverse=True)  # Sort by name (which includes timestamp)

            # Remove old backups
            for old_backup in backups[5:]:
                os.remove(os.path.join(backup_dir, old_backup))
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")

    def restore_backup(self, backup_file):
        """Restore the database from a backup file."""
        try:
            # Stop any running timers
            self.timer.stop()

            # Copy the backup file to the database location
            shutil.copy2(backup_file, "inventory.db")

            # Update last backup time
            self.last_backup = datetime.datetime.now()
            self.save_last_backup_time()

            # Restart the backup timer
            self.start_backup_timer()

            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False 