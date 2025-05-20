from flask import session
import sqlite3
import random

# Game Variables
game_state = {
    "distanceTraveled": 0,
    "daysPassed": 0,
    "survivingPeople": 5,
    "foodQuantity": 100,
    "money": 700,
    "oxen": 2,
    "bullets": 50,
}


# Connect to the database
def connect():
    db = sqlite3.connect("rest.db")
    c = db.cursor()
    return c, db


def save_game_state():
    c, db = connect()
    user_id = session.get("user_id", 1)  # Default to 1 if not logged in
    c.execute("""
        INSERT OR REPLACE INTO stats(
            distanceTraveled, daysPassed, survivingPeople, foodQuantity, 
            money, oxen, bullets, userID
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        game_state["distanceTraveled"], 
        game_state["daysPassed"], 
        game_state["survivingPeople"], 
        game_state["foodQuantity"], 
        game_state["money"], 
        game_state["oxen"], 
        game_state["bullets"], 
        user_id
    ))
    db.commit()
    db.close()


def load_game_state():
    c, db = connect()
    user_id = session.get("user_id", 1)  # Default to 1 if not logged in
    result = c.execute("""
        SELECT distanceTraveled, daysPassed, survivingPeople, 
               foodQuantity, money, oxen, bullets 
        FROM stats WHERE userID = ?
    """, (user_id,)).fetchone()
    db.close()
    if result:
        game_state["distanceTraveled"], game_state["daysPassed"], game_state["survivingPeople"], game_state["foodQuantity"], game_state["money"], game_state["oxen"], game_state["bullets"] = result


def random_event():
    event = random.choice(["bandits", "illness", "bad_weather", "good_hunting", "find_food", "no_event"])
    if event == "bandits":
        print("Bandits attack! You lose bullets and money.")
        game_state["bullets"] = max(0, game_state["bullets"] - random.randint(5, 20))
        game_state["money"] = max(0, game_state["money"] - random.randint(20, 100))
    elif event == "illness":
        print("A member falls ill. You lose a person.")
        game_state["survivingPeople"] = max(0, game_state["survivingPeople"] - 1)
    elif event == "bad_weather":
        print("Severe weather slows your progress.")
        game_state["distanceTraveled"] -= random.randint(10, 50)
    elif event == "good_hunting":
        print("You successfully hunt and gain food.")
        game_state["foodQuantity"] += random.randint(20, 50)
        game_state["bullets"] = max(0, game_state["bullets"] - random.randint(1, 5))
    elif event == "find_food":
        print("You find extra food along the trail.")
        game_state["foodQuantity"] += random.randint(10, 30)
    else:
        print("No significant event occurs.")


def game_turn():
    game_state["distanceTraveled"] += random.randint(10, 30)
    game_state["foodQuantity"] -= game_state["survivingPeople"] * 2
    game_state["daysPassed"] += 1

    if game_state["foodQuantity"] <= 0:
        return "Game Over! Your party has starved."
    if game_state["survivingPeople"] <= 0:
        return "Game Over! Everyone has perished."
    if game_state["distanceTraveled"] >= 2040:
        return "Congratulations! You reached Oregon."

    random_event()
    save_game_state()
    return None
