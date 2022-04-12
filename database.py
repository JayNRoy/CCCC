from ast import Pass
from asyncio import create_subprocess_shell
from collections import namedtuple
import sqlite3
from sys import prefix

datab = sqlite3.connect("database.db", check_same_thread=False)
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
    for table in ["US", "M"]:
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
        cursor.close()
        return "user already exists"

def removeUser(name):
    cursor = openData()
    cursor.execute("""
        DELETE FROM US WHERE name = (?)
    """, [name])
    datab.commit()
    cursor.close()

def updateUser(data, name):
    """fields can be either LANGUAGEID or PREFERENCES"""
    cursor = openData()
    if data[0] != "":
        cursor.execute("""
            UPDATE US
            SET LANGUAGEID = (?)
            WHERE NAME = (?);
        """, [str(data[0]), name])
    if data[1] != "":
        cursor.execute("""
            UPDATE US
            SET PREFERENCES = (?)
            WHERE NAME = (?);
        """, [data[1], name])
    datab.commit()
    cursor.close()

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
    datab.commit()
    cursor.close()

def find_lang(langCode):
    # finds a language from its language code
    cursor = openData()
    res = ""
    # If langCode is a string, the language name has been given, otherwise its the code.
    if type(langCode) == str:
        cursor.execute("""
            SELECT LANGUAGEID, LANGCODE FROM LANG WHERE NAME = (?);
        """, [langCode])
    else:
        cursor.execute("""
            SELECT NAME, LANGCODE FROM LANG WHERE LANGUAGEID = (?);
        """, [str(langCode)])
    datab.commit()
    for row in cursor:
        res = [row[0], row[1]]
    cursor.close()
    return res

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

def findCommonUsers(interests):
    # interests is a string of words seperated by commas
    cursor = openData()
    users = []
    pref = interests.split(",")
    for i in pref:
        field = "%" + i + "%"
        cursor.execute("""
            SELECT NAME, LANGUAGEID FROM US WHERE PREFERENCES LIKE (?);
        """, [field])
        datab.commit()
        # print(cursor.fetchall())
        # Change to find 10 results vvvvv
        num = 0
        sql = []
        for row in cursor:
            temp = [row[0], row[1]]
            sql.append(temp)
        num = 10 if len(sql) > 10 else len(sql)
        for j in range(num):
            row = sql[j]
            found = False
            for record in users:
                if len(users) > 0:
                    if row[0] in record:
                        found = True
            if found == False:
                users.append([row[0], i, row[1]])
    cursor.close()
    # returns the users matched, how they were matched and their preferred language
    return users

def get_user(name):
    cursor = openData()
    cursor.execute("""
        SELECT * FROM US where NAME = ?
    """, [name])
    # All fields in the record can be returned as they are, with the exception of prefernces.
    # The data within this attribute should be treated like a mini csv.
    newusr = []
    for row in cursor:
        try:
            newusr = [row[0], row[1], row[2], row[3], row[4]]
        except:
            return ERR_NOUSR
    cursor.close()
    return newusr

def change_password(newPassword, username):
    username = get_user(username)[0]
    cursor = openData()
    cursor.execute("""
        UPDATE US
        SET PASSWORD = (?)
        WHERE NAME = (?);
    """, [newPassword, username])
    datab.commit()
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
    real_password = ""
    exist_name = ""
    cursor.execute("""
        SELECT * FROM US where NAME = (?)
    """, [name])
    #print(name)
    r=cursor.fetchall()
    for row in r:
        # if the name exists, check the password
        exist_name = row
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
        if password == real_password:
            print("found")
            cursor.close()
            return SUCCESS
        else:
            cursor.close()
            return ERR_WRONGPASS
        
        
        



