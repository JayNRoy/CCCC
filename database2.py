def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS USER
            (USERID INTEGER,
            NAME TEXT,
            PASSWORD TEXT,
            LANGUAGEID INTEGER,
            EMAIL TEXT);
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MESSAGES
            (MESSAGEID INTEGER,
            PASSWORD TEXT,
            LANGUAGEID INTEGER,
            EMAIL TEXT);
    """)