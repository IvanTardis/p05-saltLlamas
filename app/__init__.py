'''
Salty Llamas - Ivan Gontchar, Jackie Zeng, Christopher Louie, Abidur Rahman
SoftDev
2025-05-08
p05 - Le fin
time spent: XYZ hrs
'''
from flask import Flask, render_template, request, session, redirect, url_for, flash
from database import auth, createUser, getHighScore, build
import gameBuilder 
from gamePlayer import game_turn, load_game_state, save_game_state, game_state


import sqlite3
import os

app = Flask(__name__)    #create Flask object

# Secret key for sessions
app.secret_key = os.urandom(32)

# Initialize database and game setup
build()

# Routes
@app.route(("/"), methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route(("/login"), methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_info = auth(username, password)

        if user_info:
            session['user'] = username
            session['user_id'] = user_info[4]
            load_game_state()  # Load their game state
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template('login.html')


@app.route(("/register"), methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if createUser(username, password):
            session['user'] = username
            flash("Registration successful! You are now logged in.", "success")
            return redirect(url_for('home'))
        else:
            flash("User already exists. Try logging in.", "danger")
    return render_template('register.html')


@app.route("/builder", methods=['GET', 'POST'])
def builder():
    currEvents = getCurrEvents()
    currPath = getCurrPath()
    reseter = request.form.get('reset')
    update = request.form.get('event')
    startPoint = request.form.get('start')
    endPoint = request.form.get('end')

    if request.method == 'POST':
        if reseter:
            reset()
        elif update:
            addEvent(update)
        elif startPoint or endPoint:
            changePath(startPoint, endPoint)

    return render_template('builder.html', events=currEvents, path=currPath)


@app.route("/play", methods=['GET', 'POST'])
def play():
    if 'user' not in session:
        flash("You need to be logged in to play.", "warning")
        return redirect(url_for('login'))

    load_game_state()  # Load the game state from DB
    if request.method == 'POST':
        action = request.form.get("action")
        if action == "travel":
            game_turn()
        elif action == "hunt":
            if game_state["bullets"] > 0:
                game_state["bullets"] -= random.randint(5, 15)
                game_state["foodQuantity"] += random.randint(10, 50)
            else:
                flash("You don't have enough bullets to hunt.", "warning")
        elif action == "rest":
            game_state["daysPassed"] += 1
            game_state["foodQuantity"] -= game_state["survivingPeople"]
        save_game_state()

    return render_template("play.html", game_state=game_state)


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        flash("You need to be logged in to view your profile.", "warning")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    user_stats = getHighScore(user_id)
    return render_template('profile.html', stats=user_stats)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("Logged out successfully", 'info')
    return redirect("/")


@app.route("/reset_game")
def reset_game():
    if 'user' not in session:
        flash("You need to be logged in to reset your game.", "warning")
        return redirect(url_for('login'))

    global game_state
    game_state = {
        "distanceTraveled": 0,
        "daysPassed": 0,
        "survivingPeople": 5,
        "foodQuantity": 100,
        "money": 700,
        "oxen": 2,
        "bullets": 50,
    }
    save_game_state()
    flash("Game reset successfully.", "success")
    return redirect(url_for("play"))

@app.route("/travel", methods=['POST'])
def travel_route():
    load_game_state()
    response = game_turn("travel")
    if isinstance(response, str):
        flash(response, "danger")
    else:
        flash("You traveled further along the trail.", "success")
    return redirect(url_for('play'))


@app.route("/hunt", methods=['POST'])
def hunt_route():
    load_game_state()
    response = game_turn("hunt")
    if isinstance(response, str):
        flash(response, "danger")
    else:
        flash("You successfully hunted for food.", "success")
    return redirect(url_for('play'))


@app.route("/rest", methods=['POST'])
def rest_route():
    load_game_state()
    response = game_turn("rest")
    if isinstance(response, str):
        flash(response, "danger")
    else:
        flash("You took a day to rest.", "info")
    return redirect(url_for('play'))

@app.route("/fort", methods=['POST'])
def fort_route():
    load_game_state()
    
    # Logic for buying supplies at the fort
    if game_state["money"] >= 50:
        game_state["foodQuantity"] += 20
        game_state["money"] -= 50
        flash("You bought supplies at the fort!", "success")
    else:
        flash("Not enough money to buy supplies at the fort.", "danger")

    save_game_state()
    return redirect(url_for('play'))

@app.route("/blizzard", methods=['POST'])
def blizzard_route():
    """ Logic for blizzard events. """
    load_game_state()
    game_state["foodQuantity"] -= 30
    game_state["daysPassed"] += 2
    flash("A harsh blizzard slowed you down. Lost 30 food and 2 days.", "danger")
    save_game_state()
    return redirect(url_for('play'))

@app.route("/mountain", methods=['POST'])
def mountain_route():
    """ Logic for mountain events. """
    load_game_state()
    game_state["distanceTraveled"] -= 10
    game_state["oxen"] -= 1
    flash("You encountered rough terrain in the mountains. Lost 10 miles and 1 ox.", "danger")
    save_game_state()
    return redirect(url_for('play'))

@app.route("/riders", methods=['POST'])
def riders_route():
    """ Logic for hostile or friendly riders. """
    load_game_state()
    if random.random() < 0.5:
        game_state["foodQuantity"] -= 20
        flash("Hostile riders stole 20 food.", "danger")
    else:
        game_state["foodQuantity"] += 10
        flash("Friendly riders gave you 10 food.", "success")
    save_game_state()
    return redirect(url_for('play'))
if __name__ == "__main__":
    app.debug = True
    app.run()
