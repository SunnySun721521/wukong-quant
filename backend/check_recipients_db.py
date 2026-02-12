import sqlite3

conn = sqlite3.connect('data/email_config.db')
cursor = conn.cursor()
cursor.execute('SELECT config_key, config_value FROM email_config WHERE config_key="recipients"')
result = cursor.fetchone()
print(result)
conn.close()