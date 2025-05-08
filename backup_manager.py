import os
import shutil
import datetime
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import smtplib
import ssl
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
        self.start_backup_timer()

    def start_backup_timer(self):
        """Start the backup timer to check schedule every hour."""
        self.timer.start(3600000)  # Check every hour (3600000 ms = 1 hour)
        self.check_backup_schedule()  # Check immediately on start

    def check_backup_schedule(self):
        """Check if it's time to perform an automatic backup."""
        try:
            backup_frequency = self.settings_manager.get_setting("backup_frequency", "daily")
            last_backup = self.settings_manager.get_setting("last_backup")
            
            if not last_backup:
                # If no backup has been made, do one now
                self.create_backup()
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
            
            # Clean up old backups (keep last 5)
            self.cleanup_old_backups()

            self.backup_completed.emit(f"Backup creado y enviado a {recipient_email}")

        except Exception as e:
            self.backup_failed.emit(f"Error al crear backup: {str(e)}")

    def send_backup_email(self, backup_file, recipient_email):
        """Send backup file via email."""
        try:
            # Get email settings from settings manager
            smtp_server = self.settings_manager.get_setting("smtp_server")
            smtp_port = int(self.settings_manager.get_setting("smtp_port"))
            smtp_username = self.settings_manager.get_setting("smtp_username")
            smtp_password = self.settings_manager.get_setting("smtp_password")

            print(f"Debug - SMTP Settings:")
            print(f"Server: {smtp_server}")
            print(f"Port: {smtp_port}")
            print(f"Username: {smtp_username}")
            print(f"Password length: {len(smtp_password) if smtp_password else 0}")
            print(f"Recipient: {recipient_email}")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = recipient_email
            msg['Subject'] = f"Backup de Base de Datos - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Add body
            body = f"""Backup de la base de datos BizztrackPro

Fecha y hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Archivo adjunto: {os.path.basename(backup_file)}

Este es un backup automático de su base de datos. Por favor, guarde este archivo en un lugar seguro.
"""
            msg.attach(MIMEText(body, 'plain'))

            # Attach backup file
            with open(backup_file, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="db")
                attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(backup_file))
                msg.attach(attach)

            print("Debug - Connecting to SMTP server...")
            # Send email with enhanced security settings
            context = smtplib.ssl.create_default_context()
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()  # Identify ourselves to the server
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Re-identify ourselves over TLS
            print("Debug - Attempting login...")
            server.login(smtp_username, smtp_password)
            print("Debug - Sending message...")
            server.send_message(msg)
            server.quit()
            print("Debug - Email sent successfully")

        except Exception as e:
            print(f"Debug - Error: {str(e)}")
            raise Exception(f"Error enviando email: {str(e)}")

    def cleanup_old_backups(self):
        """Keep only the last 5 backups."""
        try:
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                return
                
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
            if not os.path.exists(backup_file):
                raise Exception("Archivo de backup no encontrado")

            # Create a backup of current database before restoring
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"backups/pre_restore_backup_{timestamp}.db"
            os.makedirs("backups", exist_ok=True)
            shutil.copy2("inventory.db", current_backup)

            # Restore the selected backup
            shutil.copy2(backup_file, "inventory.db")
            
            return True, "Backup restaurado exitosamente"
        except Exception as e:
            return False, f"Error al restaurar backup: {str(e)}" 