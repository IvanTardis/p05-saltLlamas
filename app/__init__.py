'''
Salty Llamas - Ivan Gontchar, Jackie Zeng, Christopher Louie, Abidur Rahman
SoftDev
2025-05-08
p05 - Le fin
time spent: XYZ hrs
'''
from flask import Flask, render_template, request, session, redirect, url_for
from database import *

import sqlite3
import os

app = Flask(__name__)    #create Flask object

# makin' a supa-secret key
app.secret_key = os.urandom(32)

build()

@app.route(("/"), methods=['GET', 'POST'])
def home():
    return render_template( 'home.html')

@app.route(("/login") , methods=['GET', 'POST'])
def login():
    return 0

@app.route(("/register") , methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if createUser(email, password):
            session['user'] = email
            return redirect(url_for('home'))
        else:
            flash("User already exists. Try logging in.", "danger")

    return render_template('register.html')

@app.route("/builder", methods=['GET', 'POST'])
def blogCreate():
    return 0


@app.route("/play", methods=['GET', 'POST'])
def blogView(title):
    return 0


@app.route("/profile", methods=['GET', 'POST'])
def editing(title):
    return 0


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    return 0


if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
