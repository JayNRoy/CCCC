import sqlite3
connection = sqlite3.connect('Experiment.db')

cursor = connection.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS MES
            (SENDER TEXT,
            RECEIVER TEXT,
            MESSAGE TEXT,
            NUMBER INTEGER PRIMARY KEY AUTOINCREMENT);
    """)

cursor.execute("""
    INSERT INTO MES (SENDER, RECEIVER, MESSAGE) VALUES(?, ?, ?)
    """, ["abc", "def", "message"])

cursor.execute("""
    SELECT * FROM MES
    """)    
for row in cursor:
    print(row)
