"""
Server-side functionality
"""

# our code
import database as db
from database import verify_user, errmsg_from_code
import translation as tl

# third party
from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import mkdtemp
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from assistingFunctions import *
from flask_socketio import SocketIO, join_room, leave_room, emit
from numpy import isin
from datetime import datetime
from webbrowser import get

app = Flask(__name__)
sio = SocketIO(app)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = b'P\x87\xfc\xa9\xe6qQ~)8\x90D\x11\n\xb9\xa1'

@app.route("/", methods=["GET","POST"])
@login_required
def index():
    if session["username"] == "" or session["username"] == None:
        session.clear()
        return redirect("/login")

    pastConversations = db.find_past_conversations(session["username"])

    return render_template("home.html", pastConversations = pastConversations)

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        session.pop("username")
    except:
        pass
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash("Please enter a correct username")
            print("Incorrect username")
            return redirect("/login")
        password = request.form.get("password")
        if not password:
            flash("Please enter a password")
            print("blank password")
            return redirect("/login")
        user = db.get_user(username)
        if user != db.ERR_NOUSR and user != []:
            if check_password_hash(user[1], password) == True:
                flash("Welcome back " + username + "!")
                session["username"] = username
                lang = user[3]
                langCode = db.find_lang(lang)
                session["localLang"] = langCode[1]
                return redirect("/")
            else:
                flash("Password was incorrect")
                return redirect("/login")
        else:
            flash("Username " + username + " is invalid")
            print("Username " + username + " is invalid")
            return redirect("/login")
    else:
        return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    return render_template("chat.html", username = session.get("username", None), recipient = "testUser")

@app.route("/helpSettings", methods=["GET", "POST"])
@login_required
def helpSettings():
    langs = db.load_lang()
    user = db.get_user(session["username"])
    if request.method == "POST":
        data = ["", ""]
        tags = request.form.get("myTags")
        language = request.form.get("language")
        if language != "":
            for i in langs:
                if i[1] == language:
                    data[0] = i[0]
        if tags != "":
            data[1] = tags
        db.updateUser(data, user[0])
        langCode = db.find_lang(language)
        session["localLang"] = langCode[1]
        return redirect("/")
    else:
        langCode = user[3]
        default = ""
        tags = user[2]
        langus = []
        for i in langs:
            langus.append(i[1])
            if i[0] == langCode:
                default = i[1]
        return render_template("help.html", tags=tags, languages=langus, default=default)

@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():
    if request.method == "POST":
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        same = password == confirm
        password = generate_password_hash(password)
        if same == True:
            db.change_password(password, session["username"])
            flash("Changes saved!")
            return redirect("/")
        else:
            flash("Please ensure the password match.")
            return redirect("/changePassword")
    else:
        return render_template("changePassword.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        session.pop("username")
    except:
        pass
    langs = db.load_lang()
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash("Please enter a correct username")
            return redirect("/register")
        password = request.form.get("password")
        confirmPass = request.form.get("confirmation")
        if not password or not confirmPass:
            flash("Please enter password(s)")
            return redirect("/register")
        if password != confirmPass:
            flash("Please ensure your passwords match")
            return redirect("/register")
        passHash = generate_password_hash(password)
        email = request.form.get("email")
        prefs = request.form.get("myTags")
        lang = request.form.get("language")
        for i in langs:
            if  lang == i[1]:
                lang = i[0]
                break
        db.add_user(username, passHash, prefs, lang, email)
        # Add user to the db
        session["username"] = username
        langCode = db.find_lang(lang)
        session["localLang"] = langCode[1]
        return redirect("/")
    else:
        langus = []
        for i in langs:
            langus.append(i[1])
        return render_template("signup.html", languages=langus)

@app.route("/match", methods=["GET", "POST"])
@login_required
def match():
    if request.method == "POST":
        target = request.form.get("person")
        recipientDetails = db.safe_get_user(target)

        return render_template("chat.html", username = session.get("username", None), recipient = recipientDetails)
    else:
        # DB search for all online people with similar interests to user.
        userTags = db.get_user(session['username'])[2]
        possible = db.find_common_users(userTags, session["username"])

        return render_template("matches.html", people=possible )

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """ Log user out """
    flash("Logged out.")
    session.clear()
    return redirect("/login")

@sio.on('join_chat')
def on_client_connect(data):
    join_room(data["roomName"])
    session["roomName"] = data["roomName"]
    print("client connected")
    sio.emit("online_announcement", data, room=data["roomName"])

@sio.on('on_leave_room')
def on_leave_room(data):
    print("Someone is leaving a room!")
    oldRoom = data["roomName"]
    currentUsername = data["username"]
    leave_room(oldRoom)
    sio.emit("left_room", {"username" : currentUsername}, room = oldRoom)

@sio.on('msg_sent')
def on_msg_sent(data):
    data["message"] = data["message"].strip()
    data["time"] = str(datetime.utcnow())[:16]
    db.add_message(data["message"], data["sender"], data["recipient"], data["roomName"])
    sio.emit('msg_from_serv', data, room = session.get("roomName", None))

@sio.on('get_prev_messages')
def get_prev_messages():
    messages = db.get_messages(session["roomName"])
    print("SOMEONE IS GETTING PREVIOUS MESSAGES")
    sio.emit('got_messages', messages)

@sio.on('disconnect')
def disconnectUser():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    session.clear()
    sio.run(app)
