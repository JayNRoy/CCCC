from database import recallDB
import database as db
import sqlite3

# Initialisation and table creation

""" connection = sqlite3.connect("database.db")
cursor = connection.cursor() """
# db.create_tables()
# db.add_user("johnDoe", "johnnyd", "metal,gaming,destiny2", 0, "johnedwarddoe@gmail.com")
# db.add_user("jeremyRoy", "jezza123", "metal,music,guitar,destiny2", 0, "jezoffy@gmail.com")

langCSV = open('languages.txt', 'r')
langs = langCSV.readlines()
langCSV.close()
languages = []
for i in langs:
    end, codeS, codeE = 1, 1, 1
    name = ""
    code = ""
    for char in i:
        if char != ",":
            end += 1
        else:
            name = i[0:end - 1]
            codeS, codeE = end, end + 2
            code = i[codeS:codeE]
    languages.append([name, code])
""" for i in languages:
    db.add_lang(i[0], i[1]) """

langu = db.load_lang()
# print(db.recallDB())
