from flask import render_template
from . import web_bp

@web_bp.route("/")
def login():
    return render_template("login.html")


