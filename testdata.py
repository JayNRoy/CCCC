import database as db
import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()
db.create_tables(cursor)