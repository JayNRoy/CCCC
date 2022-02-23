from flask import redirect, render_template, request, session
from functools import wraps
from googletrans import Translator

translator = Translator()

# no enum type ):
LANGID_ENG, LANGID_FR, LANGID_GER = 0, 1, 2

def translate_txt(txt, srclang, destlang):
    return translator.translate(txt, src=srclang, dest=destlang)

# Assisting Functions - decorated functions
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function