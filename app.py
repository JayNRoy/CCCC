"""
the server
"""

# our code
import database as db
from database import verify_user, errmsg_from_code
import translation as tl

# third party
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import mkdtemp
from flask_session import Session
from functools import wraps
from assistingFunctions import login_required
from flask_socketio import SocketIO


con = sqlite3.connect("database.db", check_same_thread=False)
cursor = con.cursor()
db.create_tables(cursor)

# add stock users
db.add_user("jack wright", "pass", "none", 0, "jackwright@gmail.com", cursor)
db.add_user("jack wrong", "pass", "none", 0, "jackwrong@gmail.com", cursor)

app = Flask(__name__)
sio = SocketIO(app)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = b'P\x87\xfc\xa9\xe6qQ~)8\x90D\x11\n\xb9\xa1'
Session(app)

@app.route("/", methods=["GET","POST"])
@login_required
def index():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash("Please enter a correct username")
            return redirect("/login")
        password = request.form.get("password")
        if not password:
            flash("Please enter a password")
            return redirect("/login")
        print(username, password)
        verification = verify_user(username, password, cursor)
        if verification == db.SUCCESS:
            flash("Welcome back " + username + "!")
            session["username"] = username
            return redirect("/")
        elif verification == db.ERR_NOUSR:
            flash("Username " + username + " is invalid")
            return redirect("/login")
        else:
            flash("Password was incorrect")
            return redirect("/login")
    else:
        return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    return render_template("chat.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
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
        lang = request.form.get
        
    else:
        return render_template("signup.html")

@app.route("/logout")
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