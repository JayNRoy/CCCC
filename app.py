"""
Server-side functionality
"""

# our code
from webbrowser import get
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
from flask_socketio import SocketIO, emit


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
        session.clear()
        return redirect("/login")
    return render_template("home.html")

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
            flash("Pleas ensure the password match.")
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
        # DB search to find the language of the person queried.
        target = db.get_user(target)
        session['endUser'] = target[0]
        session['endLang'] = db.find_lang(target[3])[1]
        return redirect("/chat")
    else:
        # DB search for all online people with similar interests to user.
        userTags = db.get_user(session['username'])[2]
        possible = db.findCommonUsers(userTags)
        self = -1
        for i in possible:
            if i[0] == session['username']:
                self = possible.index(i)
            if i[1][0] == " ":
                i[1] = i[1][1:]
            i[2] = db.find_lang(i[2])[0]
            i[1] = i[1].capitalize()
        if self >= 0:
            possible.remove(possible[self])
        people = possible
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
    txt = translateThis(txt, session['endLang'], session['localLang'])
    sio.emit('msg_from_serv', {'text': txt})

@sio.on('disconnect')
def disconnectUser():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    session.clear()
    app.run(port=5000)