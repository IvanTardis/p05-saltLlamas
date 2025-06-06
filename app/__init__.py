'''
Salty Llamas - Ivan Gontchar, Jackie Zeng, Christopher Louie, Abidur Rahman
SoftDev
2025-05-08
p05 - Le fin
time spent: XYZ hrs
'''
from flask import Flask, render_template, request, session, redirect, url_for, flash
from database import auth, createUser, getHighScore, build, updateImagePath
from gameBuilder import *
from gamePlayer import (
    game_state,
    load_game_state,
    save_game_state,
    reset_game_state,
    game_turn,
    TOTAL_TRAIL
)


import sqlite3
import os
app = Flask(__name__)
app.secret_key = os.urandom(32)

build()

@app.route("/", methods=['GET', 'POST'])
def home():
    logged_in = "NOT LOGGED IN"
    if "user_id" in session:
        logged_in = "LOGGED IN"
        user_id = session.get('user_id')
        background_path = getBackgroundImagePath(user_id)
        midground1_path = getMidgroundImageOnePath(user_id)
        midground2_path = getMidgroundImageTwoPath(user_id)
        wagon_path = getWagonImagePath(user_id)
        return render_template('builder.html',
            
            test = logged_in
        )
    return render_template('home.html', test=logged_in)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_info = auth(username, password)

        if user_info:
            session['user'] = username
            session['user_id'] = user_info[4]
            load_game_state()
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if createUser(username, password):
            session['user'] = username
            session['user_id'] = sqlite3.connect("rest.db").cursor().execute(
                "SELECT userID FROM users WHERE username = ?", (username,)
            ).fetchone()[0]
            load_game_state()
            flash("Registration successful! You are now logged in.", "success")
            return redirect(url_for('home'))
        else:
            flash("User already exists. Try logging in.", "danger")
    return render_template('register.html')


@app.route("/builder", methods=['GET', 'POST'])
def builder():
    if "user_id" not in session:
        flash("You must log in to build a game.", "warning")
        return redirect(url_for("login"))

    currTitle = getTitle()
    updatedTitle = request.form.get('title')

    currEvents = getCurrEvents()
    currPath = getCurrPath()
    currStartDate = getStartDate()
    reseter = request.form.get('reset')
    update = request.form.get('event')
    startPoint = request.form.get('start')
    endPoint = request.form.get('end')
    startDate = request.form.get('startDate')

    characterName = request.form.get('characterName')
    description = request.form.get('description')
    startingHealth = request.form.get('startingHealth')
    startingBalance = request.form.get('startingBalance')
    bonusStat = request.form.get('bonusStat')
    currCharacters = getCharacters()

    monumentName = request.form.get('monumentName')
    monumentType = request.form.get('monumentType')
    currMonuments = getMonuments()

    trailLength = request.form.get('trailLength')
    currDist = getDistance()

    backgroundImage = request.form.get('backgroundImage')
    midgroundImageOne = request.form.get('midgroundImageOne')
    midgroundImageTwo = request.form.get('midgroundImageTwo')
    foregroundImage = request.form.get('foregroundImage')

    fullGame = getGame()

    if request.method == 'POST':
        if reseter:
            reset()
        elif update:
            currEvents = addEvent(update)
        elif startPoint or endPoint:
            currPath = changePath(startPoint, endPoint)
        elif startDate:
            currStartDate = changeStartDate(startDate)
        elif characterName:
            addCharacter(characterName, description, startingHealth,
                         startingBalance, bonusStat)
        elif monumentName:
            addMonument(monumentName, monumentType)
        elif backgroundImage:
            addBack(backgroundImage)
        elif midgroundImageOne:
            addMidOne(midgroundImageOne)
        elif midgroundImageTwo:
            addMidTwo(midgroundImageTwo)
        elif foregroundImage:
            addFore(foregroundImage)
        elif trailLength:
            currDist = changeDistance(trailLength)
        elif changeTitle:
            currTitle = changeTitle(updatedTitle)

    return render_template('builder.html', events=currEvents, path=currPath,
        startPoint=currPath[0], endPoint=currPath[1], startDate=currStartDate,
        characters=currCharacters, monuments=currMonuments, game=fullGame,
        trailLength=updatedTitle, currTitle=currTitle)

    return render_template(
        'builder.html',
        events=currEvents,
        path=currPath,
        startPoint=currPath[0],
        endPoint=currPath[1],
        startDate=currStartDate,
        characters=currCharacters,
        monuments=currMonuments,
        game=fullGame
    )
@app.route("/setup", methods=["GET", "POST"])
def setup():
    """
    Initial in‐game setup. User provides:
      - Party name
      - Up to 5 companion names (optional)
      - Quantity‐based purchases: oxen, food (lbs), ammo belts, clothing sets, misc kits
    Once POSTed, we write all fields into game_state and save_game_state().
    """
    if "user_id" not in session:
        flash("You must log in first.", "warning")
        return redirect(url_for("login"))

    reset_game_state()
    load_game_state()

    if game_state["shot_skill"] != 0:
        return redirect(url_for("play"))

    if request.method == "POST":

        party_name = request.form["party_name"].strip()


        companion1 = request.form.get("companion1", "").strip()
        companion2 = request.form.get("companion2", "").strip()
        companion3 = request.form.get("companion3", "").strip()
        companion4 = request.form.get("companion4", "").strip()
        companion5 = request.form.get("companion5", "").strip()
        companions = [c for c in (companion1, companion2, companion3, companion4, companion5) if c]

        game_state["companions"] = companions
        game_state["party_name"] = party_name or "Unnamed Party"


        occupation = request.form.get("occupation", "")
        if occupation not in ("banker", "carpenter", "blacksmith", "farmer", "miner"):
            flash("Please select a valid occupation.", "danger")
            return render_template("setup.html")


        if occupation == "banker":
            starting_bonus = 500
            starting_shot = 1
        elif occupation == "carpenter":
            starting_bonus = 300
            starting_shot = 2
        elif occupation == "blacksmith":
            starting_bonus = 200
            starting_shot = 3
        elif occupation == "farmer":
            starting_bonus = 100
            starting_shot = 4
        else:  # "miner"
            starting_bonus = 0
            starting_shot = 5


        try:
            oxen_qty = int(request.form["oxen_qty"])
            food_lbs = int(request.form["food_lbs"])
            ammo_qty = int(request.form["ammo_qty"])
            clothing_sets = int(request.form["clothing_sets"])
            misc_kits = int(request.form["misc_kits"])
        except (ValueError, KeyError):
            flash("All supply quantities must be integers ≥ 0.", "danger")
            return render_template("setup.html")


        if any(x < 0 for x in (oxen_qty, food_lbs, ammo_qty, clothing_sets, misc_kits)):
            flash("Quantities cannot be negative.", "danger")
            return render_template("setup.html")


        cost_oxen = oxen_qty * 40
        cost_food = food_lbs * 0.5
        cost_ammo = ammo_qty * 1
        cost_clothing = clothing_sets * 10
        cost_misc = misc_kits * 5

        starting_money = 700 + starting_bonus
        total_cost = cost_oxen + cost_food + cost_ammo + cost_clothing + cost_misc

        if total_cost > starting_money:
            flash(f"You only have ${starting_money:.0f} total. You spent ${total_cost:.0f}.", "danger")
            return render_template("setup.html")


        game_state["money"] = int(starting_money - total_cost)
        game_state["shot_skill"] = starting_shot

        game_state["oxen_spent"] = cost_oxen
        game_state["food"] = food_lbs
        game_state["bullets"] = ammo_qty * 50
        game_state["clothing"] = clothing_sets
        game_state["misc"] = misc_kits

        save_game_state()
        flash("Setup complete! Your journey begins now.", "success")
        return redirect(url_for("play"))


    return render_template("setup.html")


@app.route("/play", methods=["GET", "POST"])
def play():
    if "user_id" not in session:
        flash("You must log in to play.", "warning")
        return redirect(url_for("login"))

    load_game_state()

    if game_state["shot_skill"] == 0:
        return redirect(url_for("setup"))

    if request.method == "POST":

        if request.form.get("reset"):
            reset_game_state()
            flash("Game has been reset. Please set up again.", "info")
            return redirect(url_for("setup"))


        action = request.form.get("action")
        if action:
            msgs = game_turn(action)
            for m in msgs:
                flash(m, "info")
            return redirect(url_for("play"))

    return render_template(
        "play.html",
        game_state=game_state,
        total_trail=2040
    )

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash("You need to be logged in to view your profile.", "warning")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    user_stats = getHighScore(user_id)
    return render_template('profile.html', stats=user_stats)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("Logged out successfully", 'info')
    return redirect(url_for("home"))

@app.route("/upload-image", methods=['POST'])
def upload_image():
    if "user_id" not in session:
        flash("Upload not saved: You're not logged in", "danger")
    image_file = request.files.get('image')
    image_type = request.form.get('type')
    user_id = session['user_id']
    if not image_file or not image_type:
        flash("Image Failed to Upload Properly", "danger")
    os.makedirs("uploads", exist_ok=True)
    filename = f"user{user_id}_{image_type}_{image_file.filename}"
    image_path = os.path.join("uploads", filename)
    image_file.save(image_path)
    column_map = {
        "background": "backgroundImagePath",
        "midground1": "midgroundImageOnePath",
        "midground2": "midgroundImageTwoPath",
        "wagon": "wagonImagePath"
    }
    if image_type not in column_map:
        flash("Invalid Image Format", "danger")
    updateImagePath(user_id, image_path, column_map[image_type])
    flash("Image uploaded.","success")

if __name__ == "__main__":
    app.debug = True
    app.run()
