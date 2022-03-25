import database as db
import sqlite3

# Initialisation and table creation

connection = sqlite3.connect("database.db")
cursor = connection.cursor()
db.create_tables(cursor)
db.add_user("jeremyRoy", "jezza", "metal,guitar,music,gaming,destiny2", 0, "jezoffy@gmail.com", cursor)

print(db.recallDB(cursor))
