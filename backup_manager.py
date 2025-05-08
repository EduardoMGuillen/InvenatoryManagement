import os
import shutil
import datetime
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class BackupManager(QObject):
    backup_completed = pyqtSignal(str)  # Signal emitted when backup is completed
    backup_failed = pyqtSignal(str)     # Signal emitted when backup fails

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_backup_schedule)
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
        """Start the backup timer to check schedule every hour."""
        self.timer.start(3600000)  # Check every hour

    def check_backup_schedule(self):
        """Check if it's time to perform an automatic backup."""
        try:
            backup_frequency = self.settings_manager.get_setting("backup_frequency")
            last_backup = self.settings_manager.get_setting("last_backup")
            
            if not backup_frequency or not last_backup:
                return

            last_backup_date = datetime.datetime.strptime(last_backup, "%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.now()
            
            # Check if it's time for a new backup
            if backup_frequency == "daily" and (now - last_backup_date).days >= 1:
                self.create_backup()
            elif backup_frequency == "weekly" and (now - last_backup_date).days >= 7:
                self.create_backup()
            elif backup_frequency == "monthly" and (now - last_backup_date).days >= 30:
                self.create_backup()

        except Exception as e:
            self.backup_failed.emit(f"Error checking backup schedule: {str(e)}")

    def create_backup(self):
        """Create a backup of the database and send it via email."""
        try:
            # Get backup recipient email from settings
            recipient_email = self.settings_manager.get_setting("backup_recipient_email")
            if not recipient_email:
                self.backup_failed.emit("Por favor configure un email para recibir backups en Configuración")
                return

            # Create backup directory if it doesn't exist
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)

            # Create backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{backup_dir}/backup_{timestamp}.db"

            # Copy database file
            shutil.copy2("inventory.db", backup_file)

            # Send email with backup
            self.send_backup_email(backup_file, recipient_email)

            # Update last backup time
            self.settings_manager.set_setting("last_backup", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            self.backup_completed.emit(f"Backup creado y enviado a {recipient_email}")

        except Exception as e:
            self.backup_failed.emit(f"Error al crear backup: {str(e)}")

    def send_backup_email(self, backup_file, recipient_email):
        """Send backup file via email."""
        try:
            # Get email settings - using fixed sender email
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "bizztrackpro@gmail.com"
            
            # Use the exact App Password format
            smtp_password = "uwxt jvud ilfy llkf"

            print("Attempting to send backup email...")
            print(f"From: {sender_email}")
            print(f"To: {recipient_email}")
            print(f"SMTP Server: {smtp_server}:{smtp_port}")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Backup de Base de Datos - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Add body
            body = f"""Backup de la base de datos BizztrackPro

Fecha y hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Archivo adjunto: {os.path.basename(backup_file)}

Este es un backup automático de su base de datos. Por favor, guarde este archivo en un lugar seguro.

Enviado desde: {sender_email}
Enviado a: {recipient_email}
"""
            msg.attach(MIMEText(body, 'plain'))

            # Attach backup file
            with open(backup_file, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="db")
                attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(backup_file))
                msg.attach(attach)

            # Send email using Gmail's SMTP
            print("Connecting to SMTP server...")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            print("Attempting login...")
            print(f"Using password (length: {len(smtp_password.replace(' ', ''))})")
            server.login(sender_email, smtp_password.replace(' ', ''))
            
            print("Sending email...")
            server.send_message(msg)
            server.quit()
            print("Email sent successfully!")

            return True

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Error de autenticación SMTP: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error enviando email: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

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