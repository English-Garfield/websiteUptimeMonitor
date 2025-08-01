import logging as lg
import sqlite3

# Configure logging
lg.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=lg.INFO,
    handlers=[
        lg.FileHandler('uptimeMonitor.log'),
        lg.StreamHandler()
    ]
)

class UptimeMonitor:
    def __init__(self, dbName='uptimeMonitor.db'):
        self.db.name = dbName
        self.setup_db()
        self.config = self.load_config()

    def setup_db(self):

        connection = sqlite3.connect(self.db.name)
        cursor = connection.cursor()

        # Create  table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                check_interval INTEGER DEFAULT 300,
                timeout INTEGER DEFAULT 10,
                expected_status INTEGER DEFAULT 200,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create uptime_checks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uptime_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website_id INTEGER,
                status_code INTEGER,
                response_time REAL,
                is_up BOOLEAN,
                error_message TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (website_id) REFERENCES websites (id)
            )
        ''')

        # Create a downtime_alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downtime_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website_id INTEGER,
                alert_sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (website_id) REFERENCES websites (id)
            )
        ''')






def main():
    pass


if __name__ == "__main__":
    main()