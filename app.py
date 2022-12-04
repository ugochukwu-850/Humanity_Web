import os, random, sys, time
from flask import Flask, render_template, redirect, request
 
from cs50 import SQL

from modules import filter


#configure application
app = Flask(__name__)

#ensure templates are auto reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True



# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///humanity.db")


#defaults requirements or stats
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
    