from ast import Pass
from asyncio import create_subprocess_shell
from collections import namedtuple
from datetime import datetime
import sqlite3
from sys import prefix

from colorama import Cursor

datab = sqlite3.connect("database.db", check_same_thread=False)
def openData():
    # A repeatable command each function can use to open and close the database connection at will.
    cursor = datab.cursor()
    return cursor

def create_tables():
    cursor = openData()

    cursor.execute("""
    CREATE TABLE MESSAGES
            (MESSAGEID INTEGER PRIMARY KEY AUTOINCREMENT,
            MESSAGESTRING TEXT,
            SENDER TEXT,
            RECIPIENT TEXT,
            DATE TEXT,
            ROOMNAME TEXT);
        """)
    datab.commit()

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

#create_tables()

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

def add_message(message, sender, recipient, roomName):
    cursor = openData()
    cursor.execute("""
    INSERT INTO MESSAGES (MESSAGESTRING, SENDER, RECIPIENT, DATE, ROOMNAME) VALUES(?, ?, ?, ?, ?)
    """, [message, sender, recipient, datetime.utcnow(), roomName])
    datab.commit()
    cursor.close()

def get_messages(roomName):
    cursor = openData()
    cursor.execute("""
    SELECT MESSAGESTRING, SENDER, RECIPIENT, DATE FROM MESSAGES WHERE ROOMNAME = (?) ORDER BY DATE
    """, [roomName])
    datab.commit()

    messages = []

    for row in cursor:
        messages.append(row)

    return messages

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

def find_common_users(interests, currentUser):
    cursor = openData()
    cursor.execute("""
    SELECT NAME, PREFERENCES, LANGUAGEID FROM US WHERE NAME != ?
    """, [currentUser])
    datab.commit()

    userPrefs = set(interests.split(","))
    possibleFriendList = []

    for row in cursor:
        arrayPrefs = row[1].split(",")
        strangerPrefs = set(arrayPrefs)
        commonality = userPrefs.intersection(strangerPrefs)

        if commonality:
            if len(possibleFriendList) == 0:
                possibleFriendList.append([row[0], ", ".join(list(commonality)), find_lang(row[2])[0]])
            else:
                placed = False
                for i in range(0, len(possibleFriendList)):
                    if not placed:
                        if len(commonality) >= len(possibleFriendList[i][1]):
                            possibleFriendList.insert(i, [row[0], ", ".join(list(commonality)), find_lang(row[2])[0]])
                            placed = True
                
                if not placed:
                    possibleFriendList.append([row[0], ", ".join(list(commonality)), find_lang(row[2])[0]])

    return possibleFriendList




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

def safe_get_user(name): 
    #A version of get_user that doesn't return confidential information
    cursor = openData()
    cursor.execute("""
    SELECT NAME, PREFERENCES, LANGUAGEID FROM US WHERE NAME = ?
    """, [name])

    for row in cursor:
        details = {
            "username" : row[0],
            "preferences" : row[1],
            "language" : find_lang(row[2])[0]
        }

    return details
    
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

"""
def get_message(user1, user2):
    cursor = openData()
    cursor.execute(/"/"/" 
    SELECT NUMBER FROM M where (SENDER,RECEIVER) = (?, ?) 
    /"/"/", [user1, user2])
    result = []
    
    for row in cursor:
        result.append(row)

    cursor.execute(/"/"/" 
    SELECT NUMBER FROM M where (RECEIVER, SENDER) = (?, ?) 
    /"/"/", [user1, user2])
    for row in cursor:
        result.append(row)
    res=[]
    for i in result:
        res.append(i[0])

    res.sort()
    print(res,"result")
    conversation = []

    for num in res:
        cursor.execute(/"/"/" 
        SELECT SENDER, RECEIVER, MESSAGE FROM M where (NUMBER) = (?) 
        /"/"/", [num])
        
        for row in cursor:
           conversation.append(row)

    print(conversation)
    cursor.close()
"""


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
        
        
        



