from ast import Pass
from collections import namedtuple
import sqlite3
from sys import prefix

datab = sqlite3.connect("database.db")
def openData():
    # A repeatable command each function can use to open and close the database connection at will.
    cursor = datab.cursor()
    return cursor

def create_tables():
    cursor = openData()
    try:
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS US
            (USERID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT,
            PASSWORD TEXT,
            PREFERENCES TEXT,
            LANGUAGEID INTEGER,
            EMAIL TEXT);
    """)
        datab.commit()

        cursor.execute("""
    CREATE TABLE IF NOT EXISTS M
            (NUMBER INTEGER PRIMARY KEY AUTOINCREMENT,
            SENDER TEXT,
            RECEIVER TEXT,
            MESSAGE TEXT,
            LANGUAGEFROM INTEGER);
    """)
        datab.commit()

        cursor.execute("""
    CREATE TABLE IF NOT EXISTS LANG
            (LANGUAGEID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT,
            LANGCODE TEXT);
    """)
        datab.commit()
        cursor.close()
        return True
    except:
        return False

def recallDB():
    cursor = openData()
    query = """SELECT * FROM """
    result = []
    for table in ["US", "M", "LANG"]:
        cursor.execute(query + table)
        datab.commit()
        result.append([table, cursor.fetchall()])
    cursor.close()
    return result

class user:
    def __init__(self, name, password, pref, langid, email):
        self.name = name
        self.Pass = password
        self.Pref = pref
        self.langid = langid
        self.email = email
        self.all = [self.name, self.Pass, self.langid, self.email]

def add_user(Name, Pass, Pref, Langid, Email):
    cursor = openData()
    exist_name = ""
    cursor.execute("""
        SELECT NAME FROM US where NAME = ?
    """, [Name])
    datab.commit()
    # if there is an entry already we don't do anything
    for row in cursor:
        # if the name exists, check the password
        exist_name = (row)
    if exist_name == "":
        cursor.execute("""
        INSERT INTO US (NAME, PASSWORD, PREFERENCES, LANGUAGEID, EMAIL) VALUES(?, ?, ?, ?, ?)
        """, [Name, Pass, Pref, Langid, Email]) 
        datab.commit()
        cursor.close()
        return "user added"
    else:
        return "user already exists"

#add_user(234, "Olivia", "olivia", "45456", "@olivia.com")   

def add_message(user1, user2, text):
    cursor = openData()
    cursor.execute("""
    INSERT INTO M (SENDER, RECEIVER, MESSAGE) VALUES(?, ?, ?)
    """, [user1, user2, text])
    datab.commit()
    cursor.close()

def add_lang(name, code):
    cursor = openData()
    cursor.execute("""
    INSERT INTO LANG (NAME, LANGCODE) VALUES(?, ?)
    """, [name, code])
    datab.commit
    cursor.close()

def load_lang():
    """A function to load all supported languages to allow them to be chosen by preference by the user."""
    cursor = openData()
    res = []
    cursor.execute("""
        SELECT * FROM LANG
    """)
    datab.commit()
    for row in cursor:
        res.append(row)
    cursor.close()
    return res

def get_user(name):
    cursor = openData()
    cursor.execute("""
        SELECT * FROM US where NAME = ?
    """, [name])
    # All fields in the record can be returned as they are, with the exception of prefernces.
    # The data within this attribute should be treated like a mini csv.
    for row in cursor:
        newusr = user(row[0], row[1], row[2], row[3], row[4])
        return newusr
    cursor.close()

def get_message(user1, user2):
    cursor = openData()
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
    cursor.close()



SUCCESS, ERR_NOUSR, ERR_WRONGPASS = 0, 1, 2
def errmsg_from_code(code):
    if code == SUCCESS:
        return "User found"
    elif code == ERR_NOUSR:
        return "Non-existent Username"
    elif code == ERR_WRONGPASS:
        return "Incorrect password"

def verify_user(name, password):
    cursor = openData()
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
        cursor.close()
        return ERR_NOUSR
    else:
        cursor.execute("""
        SELECT PASSWORD FROM US where NAME = ?
        """, [name])
        for row in cursor:
            real_password = row[0]
            print("password was " + str(real_password))
        if password == real_password:
            print("found")
            cursor.close()
            return SUCCESS
        else:
            cursor.close()
            return ERR_WRONGPASS
    
        
        



