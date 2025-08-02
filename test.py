try:
    cursor.execute('''
                   INSERT INTO websites (url, name, check_interval, timeout, expected_status)
                   VALUES (?, ?, ?, ?, ?)
                   ''', (url, name, check_interval, timeout, expected_status))

    conn.commit()
    website_id = cursor.lastrowid
    logging.info(f"Added website: {name} ({url})")
    return website_id

except sqlite3.IntegrityError:
    logging.error(f"Website {url} already exists")
    return None