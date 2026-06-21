import sqlite3
import time
from datetime import date, timedelta
import logging
import socket
import sys

# Setup logger for background service
logging.basicConfig(
    level=logging.INFO,
    filename="reminder_service.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Single Instance Check using local Socket binding (Aynı anda sadece tek bir tane çalışması için)
try:
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to an arbitrary local port
    lock_socket.bind(('127.0.0.1', 45678))
except socket.error:
    # If port is already in use, another instance is already running
    logging.info("Reminder service is already running. Exiting.")
    sys.exit(0)

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

DB_PATH = "pda.db"
# Check interval: 3 hours (3 * 60 * 60 seconds)
CHECK_INTERVAL_SECONDS = 3 * 60 * 60

def get_urgent_tasks_count():
    """
    Queries the database directly to find pending tasks due today or tomorrow.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today_str = str(date.today())
        tomorrow_str = str(date.today() + timedelta(days=1))
        
        # Today's pending tasks count
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Bekliyor' AND due_date = ?", (today_str,))
        today_count = cursor.fetchone()[0]
        
        # Tomorrow's pending tasks count
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Bekliyor' AND due_date = ?", (tomorrow_str,))
        tomorrow_count = cursor.fetchone()[0]
        
        conn.close()
        return today_count, tomorrow_count
    except Exception as e:
        logging.error(f"Error querying SQLite database: {e}")
        return 0, 0

def send_notification(today_count, tomorrow_count):
    """
    Sends native desktop notification.
    """
    if not PLYER_AVAILABLE:
        logging.warning("Plyer library not found. Cannot trigger notification.")
        return
        
    title = "📅 Yaklaşan Görev Hatırlatıcısı!"
    message = ""
    if today_count > 0:
        message += f"Bugün teslim edilmesi gereken {today_count} acil göreviniz var! "
    if tomorrow_count > 0:
        message += f"Yarın teslim edilmesi gereken {tomorrow_count} göreviniz var!"
        
    if message:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Kişisel Dijital Asistan",
                timeout=10
            )
            logging.info("Desktop notification sent successfully.")
        except Exception as e:
            logging.error(f"Failed to show desktop notification: {e}")

def main():
    logging.info("Background reminder service started.")
    
    # Wait 5 seconds to ensure DB is initialized if started concurrently
    time.sleep(5)
    
    while True:
        today_cnt, tomorrow_cnt = get_urgent_tasks_count()
        if today_cnt > 0 or tomorrow_cnt > 0:
            send_notification(today_cnt, tomorrow_cnt)
            
        logging.info(f"Check completed. Sleeping for {CHECK_INTERVAL_SECONDS} seconds.")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()