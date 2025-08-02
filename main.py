import requests
import sqlite3
import smtplib
import time
import json

from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import logging as lg

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
        connection = sqlite3.connect(self.db.name)
        cursor = connection.cursor()

        cursor.execute('''
                       INSERT INTO uptime_checks (website_id, status_code, response_time, is_up, error_message)
                       VALUES (?, ?, ?, ?, ?)
                       ''', (website_id, status_code, response_time, is_up, error_message))

        connection.commit()
        connection.close()

    def send_alert_email(self, website_name, website_url, error_message):
        """Send email alert for website downtime"""
        try:
            email_config = self.config['email']

            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = ', '.join(email_config['to_emails'])
            msg['Subject'] = f"🚨 DOWNTIME ALERT: {website_name}"

            body = f"""
            Website Downtime Alert

            Website: {website_name}
            URL: {website_url}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Error: {error_message}

            Please check the website immediately.

            ---
            Sent by Uptime Monitor
            """

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])

            text = msg.as_string()
            server.sendmail(email_config['from_email'], email_config['to_emails'], text)
            server.quit()

            lg.info(f"Alert email sent for {website_name}")
            return True

        except Exception as e:
            lg.error(f"Failed to send email alert: {e}")
            return False

    def check_and_alert(self, website_id, url, name, timeout, expected_status):
        result = self.check_website(website_id, url, timeout, expected_status)

        if result['is_up']:
            lg.info(f"{name} is UP (Status: {result['status_code']}, Time: {result['response_time']:.2f}s)")
            self.resolve_downtime_alert(website_id)
        else:
            lg.warning(f"{name} is DOWN - {result['error']}")

            # Check if we already sent an alert recently (avoid spam)
            if not self.recent_alert_sent(website_id):
                self.send_alert_email(name, url, result['error'])
                self.record_downtime_alert(website_id)

    def recent_alert_sent(self, website_id, hours=1):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours)

        cursor.execute('''
                       SELECT COUNT(*)
                       FROM downtime_alerts
                       WHERE website_id = ?
                         AND alert_sent_at > ?
                         AND resolved_at IS NULL
                       ''', (website_id, cutoff_time))

        count = cursor.fetchone()[0]
        connection.close()

        return count > 0

    def record_downtime_alert(self, website_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('''
                       INSERT INTO downtime_alerts (website_id)
                       VALUES (?)
                       ''', (website_id,))

        connection.commit()
        connection.close()

    def resolve_downtime_alert(self, website_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('''
                       UPDATE downtime_alerts
                       SET resolved_at = CURRENT_TIMESTAMP
                       WHERE website_id = ?
                         AND resolved_at IS NULL
                       ''', (website_id,))

        connection.commit()
        connection.close()

    def get_websites(self):
        connections = sqlite3.connect(self.db_name)
        cursor = connections.cursor()

        cursor.execute('''
                       SELECT id, url, name, check_interval, timeout, expected_status
                       FROM websites
                       WHERE active = 1
                       ''')

        websites = cursor.fetchall()
        connections.close()

        return websites

    def get_uptime_status(self, website_id, days=7):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cutoff_date = datetime.now() - timedelta(days=days)

        # Get total checks and successful checks
        cursor.execute('''
                       SELECT COUNT(*)                                   as total_checks,
                              SUM(CASE WHEN is_up = 1 THEN 1 ELSE 0 END) as successful_checks,
                              AVG(response_time)                         as avg_response_time,
                              MIN(checked_at)                            as first_check,
                              MAX(checked_at)                            as last_check
                       FROM uptime_checks
                       WHERE website_id = ?
                         AND checked_at > ?
                       ''', (website_id, cutoff_date))

        stats = cursor.fetchone()
        connection.close()

        if stats[0] == 0:  # No checks found
            return None

        uptime_percentage = (stats[1] / stats[0]) * 100 if stats[0] > 0 else 0

        return {
            'total_checks': stats[0],
            'successful_checks': stats[1],
            'uptime_percentage': round(uptime_percentage, 2),
            'avg_response_time': round(stats[2], 2) if stats[2] else 0,
            'first_check': stats[3],
            'last_check': stats[4]
        }

    def start_monitoring(self):
        """Start monitoring all websites"""
        websites = self.get_websites()

        if not websites:
            lg.warning("No websites to monitor. Add some websites first.")
            return

        lg.info(f"Starting monitoring for {len(websites)} websites...")

        threads = []
        for website in websites:
            thread = threading.Thread(target=self.monitor_website, args=(website,))
            thread.daemon = True
            thread.start()
            threads.append(thread)

        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            lg.info("Shutting down monitor...")

    def print_dashboard(self):
        websites = self.get_websites()

        print("\n" + "=" * 60)
        print("WEBSITE UPTIME DASHBOARD")
        print("=" * 60)

        for website in websites:
            website_id, url, name, check_interval, timeout, expected_status = website
            stats = self.get_uptime_stats(website_id)

            if stats:
                print(f"\n {name}")
                print(f"   URL: {url}")
                print(f"   Uptime: {stats['uptime_percentage']}% (last 7 days)")
                print(f"   Avg Response: {stats['avg_response_time']}s")
                print(f"   Total Checks: {stats['total_checks']}")
            else:
                print(f"\n {name}")
                print(f"   URL: {url}")
                print(f"   Status: No data yet")

        print("\n" + "=" * 60)

def main():
    pass


if __name__ == "__main__":
    main()
