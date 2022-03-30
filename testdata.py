import database as db
import sqlite3

# Initialisation and table creation

""" connection = sqlite3.connect("database.db")
cursor = connection.cursor() """
db.create_tables()
# db.add_user("jeremyRoy", "jezza", "metal,guitar,music,gaming,destiny2", 0, "jezoffy@gmail.com")

print(db.recallDB())
