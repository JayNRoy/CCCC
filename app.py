"""
Server-side functionality
"""

# our code
import database as db
from database import verify_user, errmsg_from_code
import translation as tl

# third party
import time
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import mkdtemp
from flask_session import Session
from functools import wraps
from assistingFunctions import *
from flask_socketio import SocketIO

# db.create_tables()

# add stock users
# db.add_user("jack wright", "pass", "none", 0, "jackwright@gmail.com", cursor)
# db.add_user("jack wrong", "pass", "none", 0, "jackwrong@gmail.com", cursor)

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
        return redirect("/login")
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
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
        verification = verify_user(username, password)
        if verification == db.SUCCESS:
            flash("Welcome back " + username + "!")
            session["username"] = username
            return redirect("/")
        elif verification == db.ERR_NOUSR:
            flash("Username " + username + " is invalid")
            print("Username " + username + " is invalid")
            return redirect("/login")
        else:
            flash("Password was incorrect")
            return redirect("/login")
    else:
        return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    return render_template("chat.html")

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
        print(same)
        if same == True:
            db.change_password(password, session["username"])
            flash("Changes saved!")
            return redirect("/")
        else:
            flash("Pleas ensure the password match.")
            return redirect("/changePassword")
    else:
        return render_template("changePassword.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
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
        email = request.form.get("email")
        prefs = request.form.get("myTags")
        lang = request.form.get("language")
        for i in langs:
            if  lang == i[1]:
                lang = i[0]
                break
        db.add_user(username, password, prefs, lang, email)
        # Add user to the db
        session["username"] = username
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
        # DB search to find the language of the person queried.
        language = ""
        return redirect("/chat")
    else:
        # DB search for all online people with similar interests to user.
        people = [["danishboi", "metal,games"]]
        return render_template("matches.html", people=people )

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """ Log user out """
    flash("Logged out.")
    session.clear()
    return redirect("/login")

@sio.on('connect')
def on_client_connect():
    print("client connected")
    
@sio.on('msg_sent')
def on_msg_sent(json):
    txt = json['msg_txt']
    sio.emit('msg_from_serv', {'text': txt})

if __name__ == "__main__":
    app.run(port=5000)