'''
Salty Llamas - Ivan Gontchar, Jackie Zeng, Christopher Louie, Abidur Rahman
SoftDev
2025-05-08
p05 - Le fin
time spent: XYZ hrs
'''
from flask import Flask, render_template, request, session, redirect, url_for, flash
from database import *
from gameBuilder import *

import sqlite3
import os

app = Flask(__name__)    #create Flask object

# makin' a supa-secret key
app.secret_key = os.urandom(32)


#Global Vars
# currGame = []


build()

@app.route(("/"), methods=['GET', 'POST'])
def home():
    return render_template( 'home.html')

@app.route(("/login") , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if auth(username, password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password. Please try again.", "danger")
    return render_template('login.html')

@app.route(("/register") , methods=['GET', 'POST'])
def register():
    # print(session['user'])
    # if session['user'] != NULL:
    #     session.clear()
    # else:
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if createUser(username, password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash("User already exists. Try logging in.", "danger")

    return render_template('register.html')

@app.route("/builder", methods=['GET', 'POST'])
def builder():
    # print("start")
    currGame = getCurrGame()
    currPath = getCurrPath()
    # print("here's what I got " + str(currGame))
    reseter = request.form.get('reset')
    update = request.form.get('event')
    startPoint = request.form.get('start')
    endPoint = request.form.get('end')
    # print("." + reset + ".")
    if request.method == 'POST':
        # print("top of if")
        if reseter:
            # print("reset")
            reset()
        elif update:
            # print("update: " + update)
            update = request.form['event']
            addEvent(update)
            # currGame = addEvent(update)
        # print("end of if")
        # print(reset)
    # print("VERY end")
    return render_template('builder.html', events=currGame)


@app.route("/play", methods=['GET', 'POST'])
def play(title):
    return 0


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    return 0


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("Logged out successfully", 'info')
    return redirect("/")


if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
