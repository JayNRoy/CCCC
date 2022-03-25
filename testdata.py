import database as db
import sqlite3

# Initialisation and table creation

connection = sqlite3.connect("database.db")
cursor = connection.cursor()
db.create_tables(cursor)


print(db.recallDB(cursor))
