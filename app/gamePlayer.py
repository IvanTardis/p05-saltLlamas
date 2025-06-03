# gamePlayer.py

import random
import time
from flask import session
from database import connect, close

# -----------------------------------------------------------------------------
# In‐memory game_state dictionary. We will only persist the columns that exist
# in your current stats table. Any missing columns (clothing, misc, shot_skill,
# blue_mountains_flag) will remain zero/default in memory.
# -----------------------------------------------------------------------------
game_state = {
    "distance": 0,             # ← maps to stats.distanceTraveled
    "prev_distance": 0,        # purely in‐memory, not in DB
    "days_on_trail": 0,        # ← maps to stats.daysPassed
    "year": 1847,              # fixed
    "food": 0,                 # ← maps to stats.foodQuantity
    "bullets": 0,              # ← maps to stats.bullets
    "clothing": 0,             # NOT in DB—defaults to 0
    "misc": 0,                 # NOT in DB—defaults to 0
    "money": 0,                # ← maps to stats.money
    "oxen_spent": 0,           # ← maps to stats.oxen (we store $ spent here)
    "shot_skill": 0,           # NOT in DB—defaults to 0
    "illness_flag": False,     # ← maps to stats.illness
    "injury_flag": False,      # ← maps to stats.injury
    "blizzard_flag": False,    # ← maps to stats.blizzard
    "south_pass_flag": False,  # ← maps to stats.south_pass_flag
    "blue_mountains_flag": False,  # NOT in DB—defaults to False
    "fort_option_flag": False, # ← maps to stats.fort_flag
    "event_counter": 0,        # ← maps to stats.event_counter
    "final_fraction": 0,       # purely in‐memory, not in DB
    "survivors": 5             # ← maps to stats.survivingPeople
}

TOTAL_TRAIL = 2040

DATE_SCHEDULE = [
    ("March", 29),    # D3 = 1
    ("April", 12),    # 2
    ("April", 26),    # 3
    ("May", 10),      # 4
    ("May", 24),      # 5
    ("June", 7),      # 6
    ("June", 21),     # 7
    ("July", 5),      # 8
    ("July", 19),     # 9
    ("August", 2),    # 10
    ("August", 16),   # 11
    ("August", 31),   # 12
    ("September", 13),# 13
    ("September", 27),# 14
    ("October", 11),  # 15
    ("October", 25),  # 16
    ("November", 8),  # 17
    ("November", 22), # 18
    ("December", 6),  # 19
    ("December", 20)  # 20
]


# -----------------------------------------------------------------------------
# LOAD / SAVE: match your existing stats table exactly
# -----------------------------------------------------------------------------
def load_game_state():
    """
    Load the current user's game state from your existing 'stats' table.
    Any fields that do not exist in the table are left at their in‐memory default (0/False).
    """
    c, db = connect()
    user_id = session.get("user_id")
    if not user_id:
        close(db)
        return

    row = c.execute("""
        SELECT
            distanceTraveled,   -- maps to game_state['distance']
            daysPassed,         -- maps to game_state['days_on_trail']
            survivingPeople,    -- maps to game_state['survivors']
            foodQuantity,       -- maps to game_state['food']
            money,              -- maps to game_state['money']
            oxen,               -- maps to game_state['oxen_spent']
            bullets,            -- maps to game_state['bullets']
            event_counter,      -- maps to game_state['event_counter']
            injury,             -- maps to game_state['injury_flag']
            illness,            -- maps to game_state['illness_flag']
            blizzard,           -- maps to game_state['blizzard_flag']
            fort_flag,          -- maps to game_state['fort_option_flag']
            south_pass_flag     -- maps to game_state['south_pass_flag']
        FROM stats
        WHERE userID = ?
    """, (user_id,)).fetchone()

    close(db)
    if row:
        (
            game_state["distance"],
            game_state["days_on_trail"],
            game_state["survivors"],
            game_state["food"],
            game_state["money"],
            ox_val,
            game_state["bullets"],
            game_state["event_counter"],
            inj_f,
            ill_f,
            bliz_f,
            fort_f,
            south_f
        ) = row

        # store oxen dollars in 'oxen_spent'
        game_state["oxen_spent"] = ox_val

        game_state["injury_flag"] = bool(inj_f)
        game_state["illness_flag"] = bool(ill_f)
        game_state["blizzard_flag"] = bool(bliz_f)
        game_state["fort_option_flag"] = bool(fort_f)
        game_state["south_pass_flag"] = bool(south_f)

        # The missing columns (clothing, misc, shot_skill, blue_mountains_flag)
        # remain at their default of 0/False.


def save_game_state():
    """
    Write back only those fields that exist in 'stats'. Any in‐memory‐only fields
    (clothing, misc, shot_skill, blue_mountains_flag) are not saved until you add them
    to the table schema.
    """
    c, db = connect()
    user_id = session.get("user_id")
    if not user_id:
        close(db)
        return

    # Use oxen_spent to write into stats.oxen
    ox_val = game_state["oxen_spent"]

    c.execute("""
        UPDATE stats
           SET distanceTraveled    = ?,
               daysPassed          = ?,
               survivingPeople     = ?,
               foodQuantity        = ?,
               money               = ?,
               oxen                = ?,
               bullets             = ?,
               event_counter       = ?,
               injury              = ?,
               illness             = ?,
               blizzard            = ?,
               fort_flag           = ?,
               south_pass_flag     = ?
         WHERE userID = ?
    """, (
        game_state["distance"],
        game_state["days_on_trail"],
        game_state["survivors"],
        game_state["food"],
        game_state["money"],
        ox_val,
        game_state["bullets"],
        game_state["event_counter"],
        int(game_state["injury_flag"]),
        int(game_state["illness_flag"]),
        int(game_state["blizzard_flag"]),
        int(game_state["fort_option_flag"]),
        int(game_state["south_pass_flag"]),
        user_id
    ))
    db.commit()
    close(db)


# -----------------------------------------------------------------------------
# All other helper / game logic functions remain exactly as before.
# (They reference the in‐memory `game_state` fields.)
# -----------------------------------------------------------------------------

def get_current_date_message():
    d3 = game_state["days_on_trail"]
    if d3 == 0:
        return "MONDAY March 29, 1847"
    if 1 <= d3 <= 20:
        month, day = DATE_SCHEDULE[d3 - 1]
        return f"MONDAY {month} {day}, 1847"
    return None


def random_event():
    thresholds = [6, 11, 13, 15, 17, 22, 32, 35, 37, 42, 44, 54, 64, 69, 95]
    r = random.randint(1, 100)
    idx = 0
    while idx < len(thresholds) and r > thresholds[idx]:
        idx += 1

    event_funcs = [
        wagon_breakdown,
        ox_injures_leg,
        daughter_breaks_arm,
        ox_wanders_off,
        son_gets_lost,
        unsafe_water,
        heavy_rains,
        bandits_attack,
        wagon_fire,
        lose_way_in_fog,
        snake_bite,
        ford_river_swamped,
        wild_animals_attack,
        cold_weather,
        hail_storm,
        friendly_indians
    ]

    if 0 <= idx < len(event_funcs):
        return event_funcs[idx]()
    return []


def wagon_breakdown():
    msgs = ["WAGON BREAKS DOWN — LOSE TIME AND SUPPLIES FIXING IT."]
    game_state["distance"] = max(0, game_state["distance"] - (15 + random.randint(0, 5)))
    game_state["misc"] = max(0, game_state["misc"] - 8)
    return msgs


def ox_injures_leg():
    msgs = ["OX INJURES LEG — SLOWS YOU DOWN REST OF TRIP"]
    game_state["distance"] = max(0, game_state["distance"] - 25)
    game_state["oxen_spent"] = max(0, game_state["oxen_spent"] - 20)
    return msgs


def daughter_breaks_arm():
    msgs = [
        "BACK LUCK — YOUR DAUGHTER BROKE HER ARM",
        "YOU HAD TO STOP AND USE SUPPLIES TO MAKE A SLING"
    ]
    game_state["distance"] = max(0, game_state["distance"] - (5 + random.randint(0, 4)))
    game_state["misc"] = max(0, game_state["misc"] - (2 + random.randint(0, 3)))
    return msgs


def ox_wanders_off():
    msgs = ["OX WANDERS OFF — SPEND TIME LOOKING FOR IT"]
    game_state["distance"] = max(0, game_state["distance"] - 17)
    return msgs


def son_gets_lost():
    msgs = ["YOUR SON GETS LOST — SPEND HALF THE DAY LOOKING FOR HIM"]
    game_state["distance"] = max(0, game_state["distance"] - 10)
    return msgs


def unsafe_water():
    msgs = ["UNSAFE WATER — LOSE TIME LOOKING FOR CLEAN SPRING"]
    game_state["distance"] = max(0, game_state["distance"] - (2 + random.randint(0, 10)))
    return msgs


def heavy_rains():
    msgs = []
    if game_state["distance"] <= 950:
        msgs.append("HEAVY RAINS — TIME AND SUPPLIES LOST")
        game_state["food"] = max(0, game_state["food"] - 10)
        game_state["bullets"] = max(0, game_state["bullets"] - 500)
        game_state["misc"] = max(0, game_state["misc"] - 15)
        game_state["distance"] = max(0, game_state["distance"] - (5 + random.randint(0, 10)))
    return msgs


def bandits_attack():
    msgs = ["BANDITS ATTACK!"]
    msgs.extend(shoot_out())
    return msgs


def wagon_fire():
    msgs = ["THERE WAS A FIRE IN YOUR WAGON — FOOD AND SUPPLIES DAMAGED!"]
    game_state["food"] = max(0, game_state["food"] - 40)
    game_state["bullets"] = max(0, game_state["bullets"] - 400)
    game_state["misc"] = max(0, game_state["misc"] - random.randint(3, 10))
    game_state["distance"] = max(0, game_state["distance"] - 15)
    return msgs


def lose_way_in_fog():
    msgs = ["LOSE YOUR WAY IN HEAVY FOG — TIME IS LOST"]
    game_state["distance"] = max(0, game_state["distance"] - (10 + random.randint(0, 5)))
    return msgs


def snake_bite():
    msgs = ["YOU KILLED A POISONOUS SNAKE AFTER IT BIT YOU"]
    game_state["bullets"] = max(0, game_state["bullets"] - 10)
    game_state["misc"] = max(0, game_state["misc"] - 5)
    if game_state["misc"] < 0:
        msgs.append("YOU DIED OF SNAKEBITE SINCE YOU HAVE NO MEDICINE")
        game_state["survivors"] = 0
    return msgs


def ford_river_swamped():
    msgs = ["WAGON GETS SWAMPED FORDING RIVER — LOSE FOOD AND CLOTHES"]
    game_state["food"] = max(0, game_state["food"] - 30)
    game_state["clothing"] = max(0, game_state["clothing"] - 20)
    game_state["distance"] = max(0, game_state["distance"] - (20 + random.randint(0, 20)))
    return msgs


def wild_animals_attack():
    msgs = ["WILD ANIMALS ATTACK!"]
    if game_state["bullets"] > 39:
        b1 = random.randint(1, 4)
        if b1 <= 2:
            msgs.append("NICE SHOOTIN' PARTNER — THEY DIDN'T GET MUCH")
            game_state["bullets"] = max(0, game_state["bullets"] - 20 * b1)
            game_state["clothing"] = max(0, game_state["clothing"] - 4 * b1)
            game_state["food"] = max(0, game_state["food"] - 8 * b1)
        else:
            msgs.append("SLOW ON THE DRAW — THEY GOT AT YOUR FOOD AND CLOTHES")
            game_state["bullets"] = max(0, game_state["bullets"] - 20 * b1)
            game_state["clothing"] = max(0, game_state["clothing"] - 4 * b1)
            game_state["food"] = max(0, game_state["food"] - 8 * b1)
    else:
        msgs.append("YOU WERE TOO LOW ON BULLETS — THE WOLVES OVERPOWERED YOU")
        game_state["injury_flag"] = True
    return msgs


def cold_weather():
    msgs = ["COLD WEATHER — BRRRRRRR! YOU "]
    threshold = 22 + 4 * random.random()
    if game_state["clothing"] > threshold:
        msgs[-1] += "have enough clothing to keep you warm."
    else:
        msgs[-1] += "don't have enough clothing to keep you warm."
        game_state["injury_flag"] = True
    return msgs


def hail_storm():
    msgs = ["HAIL STORM — SUPPLIES DAMAGED"]
    game_state["misc"] = max(0, game_state["misc"] - (random.randint(0, 10) + 4))
    game_state["bullets"] = max(0, game_state["bullets"] - 200)
    game_state["food"] = max(0, game_state["food"] - 5)
    return msgs


def friendly_indians():
    msgs = ["HELPFUL INDIANS SHOW YOU WHERE TO FIND MORE FOOD"]
    game_state["food"] += 14
    return msgs


def shoot_out():
    msgs = []
    skill = game_state["shot_skill"]
    success_chance = 60 + 10 * (5 - skill)
    if random.randint(1, 100) <= success_chance:
        lost_bullets = random.randint(1, 3) * 20 + 80
        game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
        game_state["food"] += 15
        game_state["money"] = max(0, game_state["money"] - 10)
        msgs.append("QUICKEST DRAW OUTSIDE OF DODGE CITY!!! YOU GOT 'EM!")
    else:
        msgs.append("LOUSY SHOT — YOU GOT KNIFED!")
        game_state["injury_flag"] = True
        game_state["money"] = max(0, game_state["money"] - 20)
        game_state["misc"] = max(0, game_state["misc"] - 5)
    return msgs


def check_mountains():
    msgs = []
    st = game_state
    if st["distance"] <= 950:
        return []
    difficulty = ((st["distance"] / 100 - 15) ** 2 + 72)
    threshold = 9 - difficulty / (difficulty + 12)
    if random.random() * 10 > threshold:
        msgs.append("RUGGED MOUNTAINS")
        r = random.random()
        if r < 0.1:
            msgs.append("YOU GOT LOST — LOSE VALUABLE TIME TRYING TO FIND TRAIL!")
            st["distance"] = max(0, st["distance"] - 60)
        elif 0.1 <= r < 0.21:
            msgs.append("WAGON DAMAGED! — LOSE TIME AND SUPPLIES")
            st["misc"] = max(0, st["misc"] - 5)
            st["bullets"] = max(0, st["bullets"] - 200)
            st["distance"] = max(0, st["distance"] - (20 + 30 * random.random()))
        else:
            msgs.append("THE GOING GETS SLOW")
            st["distance"] = max(0, st["distance"] - (45 + random.random() / 0.02))

        if not st["south_pass_flag"] and st["distance"] >= 1700:
            if random.random() < 0.8:
                msgs.append("YOU MADE IT SAFELY THROUGH SOUTH PASS — NO SNOW")
            else:
                msgs.append("BLIZZARD IN SOUTH PASS — TIME AND SUPPLIES LOST")
                st["blizzard_flag"] = True
                st["food"] = max(0, st["food"] - 25)
                st["misc"] = max(0, st["misc"] - 10)
                st["bullets"] = max(0, st["bullets"] - 300)
                st["distance"] = max(0, st["distance"] - (30 + 40 * random.random()))
                if st["clothing"] < 18 + 2 * random.random():
                    msgs.append("YOU DIED IN BLIZZARD — NOT ENOUGH CLOTHING")
                    st["survivors"] = 0
            st["south_pass_flag"] = True

    return msgs


def check_illness():
    msgs = []
    st = game_state
    if st["blizzard_flag"] or st["injury_flag"]:
        return []
    e_level = 2  # moderate by default
    chance_wild = 10 + 35 * (e_level - 1)
    if random.randint(1, 100) < chance_wild:
        msgs.append("WILD ILLNESS — MEDICINE USED")
        st["distance"] = max(0, st["distance"] - 5)
        st["misc"] = max(0, st["misc"] - 2)
    else:
        chance_bad = 100 - (40 / (4 ** (e_level - 1)))
        if random.randint(1, 100) < chance_bad:
            msgs.append("BAD ILLNESS — MEDICINE USED")
            st["distance"] = max(0, st["distance"] - 5)
            st["misc"] = max(0, st["misc"] - 5)
        else:
            return []

    if st["misc"] < 0:
        msgs.append("YOU RAN OUT OF MEDICAL SUPPLIES — YOU DIED OF ILLNESS")
        st["survivors"] = 0
    return msgs


def check_end_conditions():
    msgs = []
    st = game_state
    if st["food"] <= 0 and st["survivors"] > 0:
        msgs.append("YOU RAN OUT OF FOOD AND STARVED TO DEATH.")
        st["survivors"] = 0

    if st["distance"] >= TOTAL_TRAIL and st["survivors"] > 0:
        fraction = (TOTAL_TRAIL - st["prev_distance"]) / max(1, (st["distance"] - st["prev_distance"]))
        st["final_fraction"] = fraction
        msgs.append("YOU FINALLY ARRIVED AT OREGON CITY — AFTER 2040 LONG MILES! HOORAY!")
        msgs.append("PRESIDENT JAMES K. POLK SENDS YOU HIS HEARTIEST CONGRATULATIONS")
        msgs.append("AND WISHES YOU A PROSPEROUS LIFE AHEAD AT YOUR NEW HOME")
        st["survivors"] = 0

    return msgs


def travel_turn():
    msgs = []
    st = game_state

    miles = random.randint(10, 30)
    st["prev_distance"] = st["distance"]
    st["distance"] += miles
    msgs.append(f"You traveled {miles} miles down the trail.")

    cost = st["survivors"] * 2
    st["food"] = max(0, st["food"] - cost)
    msgs.append(f"You consumed {cost} pounds of food.")

    st["days_on_trail"] += 1
    st["fort_option_flag"] = True

    if st["food"] >= 13:
        st["food"] -= 18
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        st["distance"] += max(0, bonus)
        msgs.append(f"You ate a moderate meal (−18 food) and gained a {bonus}‐mile bonus from healthy oxen.")

    st["event_counter"] += 1
    if st["event_counter"] >= 1:
        msgs.extend(random_event())
        st["event_counter"] = 0

    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())

    return msgs


def hunt_turn():
    msgs = []
    st = game_state

    if st["bullets"] <= 0:
        msgs.append("TOUGH — YOU NEED MORE BULLETS TO GO HUNTING.")
        return msgs

    st["days_on_trail"] += 1
    prey_quality = random.randint(1, 5)
    if prey_quality == 1:
        msgs.append("YOU MISSED — AND YOUR DINNER GOT AWAY.")
    elif prey_quality <= 3:
        gained = random.randint(48 - 2 * prey_quality, 52 + prey_quality * 2)
        st["food"] += gained
        cost_bullets = 10 + 3 * prey_quality
        st["bullets"] = max(0, st["bullets"] - cost_bullets)
        msgs.append(f"NICE SHOT — YOU GAINED {gained} food and used {cost_bullets} bullets.")
    else:
        gained = random.randint(52, 58)
        st["food"] += gained
        cost_bullets = random.randint(10, 14)
        st["bullets"] = max(0, st["bullets"] - cost_bullets)
        msgs.append(f"BIG SHOT! You gained {gained} food and used {cost_bullets} bullets.")

    if st["food"] >= 13:
        st["food"] -= 18
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        st["distance"] += max(0, bonus)
        msgs.append(f"You ate a moderate meal (−18 food) and gained a {bonus}‐mile bonus.")

    st["event_counter"] += 1
    if st["event_counter"] >= 1:
        msgs.extend(random_event())
        st["event_counter"] = 0

    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())

    return msgs


def rest_turn():
    msgs = []
    st = game_state
    st["days_on_trail"] += 1
    st["food"] = max(0, st["food"] - st["survivors"])
    msgs.append(f"You rested for a day and used {st['survivors']} food.")

    if st["food"] >= 13:
        st["food"] -= 18
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        st["distance"] += max(0, bonus)
        msgs.append(f"You ate a moderate meal (−18 food) and gained a {bonus}‐mile bonus.")

    st["event_counter"] += 1
    if st["event_counter"] >= 1:
        msgs.extend(random_event())
        st["event_counter"] = 0

    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())

    return msgs


def fort_turn():
    msgs = []
    st = game_state
    if st["money"] >= 50:
        st["food"] += 20
        st["money"] -= 50
        msgs.append("You bought 20 food at the fort for $50.")
    else:
        msgs.append("Not enough money to buy supplies at the fort.")

    st["prev_distance"] = st["distance"]
    st["distance"] += 0
    st["food"] = max(0, st["food"] - (st["survivors"] * 2))
    st["days_on_trail"] += 1

    if st["food"] >= 13:
        st["food"] -= 18
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        st["distance"] += max(0, bonus)
        msgs.append(f"You ate a moderate meal (−18 food) and gained a {bonus}‐mile bonus.")

    st["event_counter"] += 1
    if st["event_counter"] >= 1:
        msgs.extend(random_event())
        st["event_counter"] = 0

    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())

    return msgs


def game_turn(action):
    """
    Perform one “turn” of the game. `action` is one of: "travel", "hunt", "rest", or "fort".
    Returns a list of messages to flash.
    """
    msgs = []

    if game_state["survivors"] <= 0 or game_state["distance"] >= TOTAL_TRAIL:
        return ["Game is already over."]

    if action == "travel":
        msgs = travel_turn()
    elif action == "hunt":
        msgs = hunt_turn()
    elif action == "rest":
        msgs = rest_turn()
    elif action == "fort":
        msgs = fort_turn()
    else:
        msgs = [f"Unknown action: {action}"]

    save_game_state()
    return msgs
