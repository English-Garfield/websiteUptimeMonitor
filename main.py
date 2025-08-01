import logging as lg
import sqlite3
import json
import time
import requests

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

        connection.commit()
        connection.close()
        lg.info("Database initialized successfully")

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_config = {
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "your_email@gmail.com",
                    "password": "your_app_password",
                    "from_email": "your_email@gmail.com",
                    "to_emails": ["admin@example.com"]
                },
                "general": {
                    "user_agent": "UptimeMonitor/1.0",
                    "max_retries": 3,
                    "retry_delay": 30
                }
            }

            with open('config.json', 'w') as f:
                json.dump(default_config, f, indent=4)

            lg.info("Created default config.json - please update with your settings")
            return default_config

    def add_website(self, url, name, check_interval=300, timeout=10, expected_status=200):
            connection = sqlite3.connect(self.db.name)
            cursor = connection.cursor()

            try:
                cursor.execute('''
                               INSERT INTO websites (url, name, check_interval, timeout, expected_status)
                               VALUES (?, ?, ?, ?, ?)
                               ''', (url, name, check_interval, timeout, expected_status))

                connection.commit()
                website_id = cursor.lastrowid
                lg.info(f"Added website: {name} ({url})")
                return website_id

            except sqlite3.IntegrityError:
                lg.error(f"Website {url} already exists")
                return None
            finally:
                connection.close()

    def check_website(self, website_id, url, timeout, expected_status):
        start_time = time.time()

        try:
            headers = {'User-Agent': self.config['general']['user_agent']}
            response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            response_time = time.time() - start_time

            is_up = response.status_code == expected_status
            error_message = None if is_up else f"Unexpected status code: {response.status_code}"

            self.log_check_result(website_id, response.status_code, response_time, is_up, error_message)

            return {
                'is_up': is_up,
                'status_code': response.status_code,
                'response_time': response_time,
                'error': error_message
            }

        except requests.RequestException as e:
            response_time = time.time() - start_time
            error_message = str(e)

            self.log_check_result(website_id, None, response_time, False, error_message)

            return {
                'is_up': False,
                'status_code': None,
                'response_time': response_time,
                'error': error_message
            }

    def log_check_result(self, website_id, status_code, response_time, is_up, error_message):



def main():
    pass


if __name__ == "__main__":
    main()