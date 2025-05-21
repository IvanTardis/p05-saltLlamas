from flask import session
import sqlite3
import random
from database import connect, close

# Game State Initialization
game_state = {
    "distanceTraveled": 0,
    "daysPassed": 0,
    "survivingPeople": 5,
    "foodQuantity": 100,
    "money": 700,
    "oxen": 2,
    "bullets": 50,
    "mileage": 0,
    "event_counter": 0,
    "injury": False,
    "illness": False,
    "blizzard": False,
    "fort_flag": False,
    "south_pass_flag": False
}

def save_game_state():
    """Save the current game state to the database."""
    c, db = connect()
    user_id = session.get("user_id", 1)
    c.execute("""
        UPDATE stats
        SET distanceTraveled=?, daysPassed=?, survivingPeople=?, foodQuantity=?, money=?,
            oxen=?, bullets=?, mileage=?, event_counter=?, injury=?, illness=?, blizzard=?, fort_flag=?
        WHERE userID=?
    """, (
        game_state["distanceTraveled"],
        game_state["daysPassed"],
        game_state["survivingPeople"],
        game_state["foodQuantity"],
        game_state["money"],
        game_state["oxen"],
        game_state["bullets"],
        game_state["mileage"],
        game_state["event_counter"],
        int(game_state["injury"]),
        int(game_state["illness"]),
        int(game_state["blizzard"]),
        int(game_state["fort_flag"]),
        user_id
    ))
    db.commit()
    close(db)

def load_game_state():
    """Load game state from the database."""
    c, db = connect()
    user_id = session.get("user_id", 1)
    result = c.execute("""
        SELECT distanceTraveled, daysPassed, survivingPeople, foodQuantity, money,
        oxen, bullets, mileage, event_counter, injury, illness, blizzard, fort_flag
        FROM stats WHERE userID = ?
    """, (user_id,)).fetchone()
    close(db)
    if result:
        (game_state["distanceTraveled"], game_state["daysPassed"],
         game_state["survivingPeople"],game_state["foodQuantity"],
         game_state["money"], game_state["oxen"], game_state["bullets"],
         game_state["mileage"], game_state["event_counter"],
         game_state["injury"], game_state["illness"], game_state["blizzard"],
         game_state["fort_flag"]) = result


def game_turn(action):
    """
    Executes a game turn based on the specified action:
    - 'travel': Moves forward and consumes food.
    - 'hunt': Uses bullets to gain food.
    - 'rest': Spends a day resting, consuming food.
    """
    if action == "travel":
        game_state["distanceTraveled"] += random.randint(10, 30)
        game_state["foodQuantity"] -= game_state["survivingPeople"] * 2
        game_state["daysPassed"] += 1
    elif action == "hunt":
        if game_state["bullets"] > 0:
            game_state["bullets"] -= random.randint(5, 15)
            game_state["foodQuantity"] += random.randint(10, 50)
        else:
            return "Not enough bullets to hunt."
    elif action == "rest":
        game_state["daysPassed"] += 1
        game_state["foodQuantity"] -= game_state["survivingPeople"]

    # Check if food or people are 0
    if game_state["foodQuantity"] <= 0:
        return "You ran out of food and starved!"
    if game_state["survivingPeople"] <= 0:
        return "Everyone has perished."

    save_game_state()
    return game_state
