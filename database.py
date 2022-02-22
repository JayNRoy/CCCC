from ast import Pass
from collections import namedtuple
import sqlite3
from sys import prefix

db = sqlite3.connect("database.db")
cursor = db.cursor()

def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS US
            (NAME TEXT,
            PASSWORD TEXT,
            PREFERENCES TEXT,
            LANGUAGEID INTEGER,
            EMAIL TEXT);
    """)
    db.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS M
            (SENDER TEXT,
            RECEIVER TEXT,
            MESSAGE TEXT,
            NUMBER INTEGER PRIMARY KEY AUTOINCREMENT);
    """)
    db.commit()


class user:
    def __init__(self, name, password, pref, langid, email):
        self.name = name
        self.Pass = password
        self.Pref = pref
        self.langid = langid
        self.email = email
        self.all = [self.name, self.Pass, self.langid, self.email]

def add_user(Name, Pass, Pref, Langid, Email, cursor):
    exist_name = ""
    cursor.execute("""
        SELECT NAME FROM US where NAME = ?
    """, [Name])
    db.commit()
    # if there is an entry already we don't do anything
    for row in cursor:
        # if the name exists, check the password
        exist_name = (row)
    if exist_name == "":
        cursor.execute("""
        INSERT INTO US (NAME, PASSWORD, PREFERENCES, LANGUAGEID, EMAIL) VALUES(?, ?, ?, ?, ?)
        """, [Name, Pass, Pref, Langid, Email]) 
        db.commit() 
    else:
        return "user already exists"

#add_user(234, "Olivia", "olivia", "45456", "@olivia.com")   

def add_message(user1, user2, text, cursor):
    cursor.execute("""
    INSERT INTO M (SENDER, RECEIVER, MESSAGE) VALUES(?, ?, ?)
    """, [user1, user2, text])
    db.commit()

def get_user(name, cursor):
    cursor.execute("""
        SELECT * FROM US where NAME = ?
    """, [name])
    #result = ""
    for row in cursor:
        newusr = user(row[0], row[1], row[2], row[3], row[4])
        return newusr

def get_message(user1, user2, cursor):
    cursor.execute(""" 
    SELECT NUMBER FROM M where (SENDER,RECEIVER) = (?, ?) 
    """, [user1, user2])
    result = []
    

    for row in cursor:
        result.append(row)

    cursor.execute(""" 
    SELECT NUMBER FROM M where (RECEIVER, SENDER) = (?, ?) 
    """, [user1, user2])
    for row in cursor:
        result.append(row)
    res=[]
    for i in result:
        res.append(i[0])

    res.sort()
    print(res,"result")
    conversation = []

    for num in res:
        cursor.execute(""" 
        SELECT SENDER, RECEIVER, MESSAGE FROM M where (NUMBER) = (?) 
        """, [num])
        
        for row in cursor:
           conversation.append(row)

    print(conversation)



SUCCESS, ERR_NOUSR, ERR_WRONGPASS = 0, 1, 2
def errmsg_from_code(code):
    if code == SUCCESS:
        return "User found"
    elif code == ERR_NOUSR:
        return "Non-existent Username"
    elif code == ERR_WRONGPASS:
        return "Incorrect password"

def verify_user(name, password, cursor):
    print("verify")
    real_password = ""
    exist_name = ""
    cursor.execute("""
        SELECT * FROM US where NAME = (?)
    """, [name])
    #print(name)
    r=cursor.fetchall()
    print(r,"cur")
    for row in r:
        print(row)
        # if the name exists, check the password
        exist_name = row
        print("exist = ", exist_name)
    if exist_name == "":
        print("Not a username")
        return ERR_NOUSR
    else:
        cursor.execute("""
        SELECT PASSWORD FROM US where NAME = ?
        """, [name])
        for row in cursor:
            real_password = row[0]
            print(f"password was {real_password}")
        if password == real_password:
            print("found")
            return SUCCESS
        else:
            return ERR_WRONGPASS
    
        
        



