# gamePlayer.py

import random
from flask import session
from database import connect, close

# -----------------------------------------------------------------------------
# In‐memory `game_state`. 
# Anything not in the DB schema stays here (companions, party_name, kits, shot_skill, etc.).
# -----------------------------------------------------------------------------
game_state = {
    "party_name": "",             # (in-memory only)
    "companions": [],             # up to five companion names (in-memory only)
    "members": [],                # ["You"] + companions; used to pick who dies
    "distance": 0,                # → stats.distanceTraveled
    "prev_distance": 0,           # purely in-memory
    "days_on_trail": 0,           # → stats.daysPassed
    "year": 1847,                 # fixed
    "food": 0,                    # lbs of food → stats.foodQuantity
    "bullets": 0,                 # total bullets → stats.bullets
    "clothing": 0,                # # of clothing sets (in-memory only)
    "misc": 0,                    # # of misc kits (medicine) (in-memory only)
    "money": 0,                   # → stats.money
    "oxen_spent": 0,              # $ spent on oxen → stats.oxen
    "shot_skill": 0,              # 1–5 (in-memory only)
    "illness_flag": False,        # → stats.illness
    "injury_flag": False,         # → stats.injury
    "blizzard_flag": False,       # → stats.blizzard
    "south_pass_flag": False,     # → stats.south_pass_flag
    "blue_mountains_flag": False, # in-memory only (unused in current console logic)
    "fort_option_flag": False,    # → stats.fort_flag
    "event_counter": 0,           # → stats.event_counter
    "final_fraction": 0,          # in-memory only
    "survivors": 5                # → stats.survivingPeople
}

TOTAL_TRAIL = 2040

DATE_SCHEDULE = [
    ("March", 29),    # turn 1
    ("April", 12),    # turn 2
    ("April", 26),    # turn 3
    ("May", 10),      # turn 4
    ("May", 24),      # turn 5
    ("June", 7),      # turn 6
    ("June", 21),     # turn 7
    ("July", 5),      # turn 8
    ("July", 19),     # turn 9
    ("August", 2),    # turn 10
    ("August", 16),   # turn 11
    ("August", 31),   # turn 12
    ("September", 13),# turn 13
    ("September", 27),# turn 14
    ("October", 11),  # turn 15
    ("October", 25),  # turn 16
    ("November", 8),  # turn 17
    ("November", 22), # turn 18
    ("December", 6),  # turn 19
    ("December", 20)  # turn 20
]

# -----------------------------------------------------------------------------
# LOAD / SAVE / RESET: match your existing `stats` schema exactly.
# Everything not persisted in `stats` stays in memory.
# -----------------------------------------------------------------------------
def load_game_state():
    """
    Load the current user's game state from the 'stats' table.
    Fields not in the table stay at their in-memory defaults.
    """
    c, db = connect()
    user_id = session.get("user_id")
    if not user_id:
        close(db)
        return

    row = c.execute("""
        SELECT
            distanceTraveled,  -- → game_state['distance']
            daysPassed,        -- → game_state['days_on_trail']
            survivingPeople,   -- → game_state['survivors']
            foodQuantity,      -- → game_state['food']
            money,             -- → game_state['money']
            oxen,              -- → game_state['oxen_spent']
            bullets,           -- → game_state['bullets']
            event_counter,     -- → game_state['event_counter']
            injury,            -- → game_state['injury_flag']
            illness,           -- → game_state['illness_flag']
            blizzard,          -- → game_state['blizzard_flag']
            fort_flag,         -- → game_state['fort_option_flag']
            south_pass_flag    -- → game_state['south_pass_flag']
        FROM stats
        WHERE userID = ?
    """, (user_id,)).fetchone()
    close(db)

    if not row:
        return

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

    game_state["oxen_spent"] = ox_val
    game_state["injury_flag"] = bool(inj_f)
    game_state["illness_flag"] = bool(ill_f)
    game_state["blizzard_flag"] = bool(bliz_f)
    game_state["fort_option_flag"] = bool(fort_f)
    game_state["south_pass_flag"] = bool(south_f)

    # “companions”, “members”, “clothing”, “misc”, “shot_skill”, 
    # “blue_mountains_flag”, “party_name” remain at their in-memory defaults.


def save_game_state():
    """
    Save only those fields that exist in 'stats'.  In-memory–only fields are skipped.
    """
    c, db = connect()
    user_id = session.get("user_id")
    if not user_id:
        close(db)
        return

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


def reset_game_state():
    """
    Resets the current user's stats row back to defaults, and zeroes out everything
    in-memory.  The user will have to re-run setup from scratch.
    """
    c, db = connect()
    user_id = session.get("user_id")
    if not user_id:
        close(db)
        return

    # Reset the DB row to defaults
    c.execute("""
        UPDATE stats
           SET distanceTraveled    = 0,
               daysPassed          = 0,
               survivingPeople     = 5,
               foodQuantity        = 0,
               money               = 0,
               oxen                = 0,
               bullets             = 0,
               event_counter       = 0,
               injury              = 0,
               illness             = 0,
               blizzard            = 0,
               fort_flag           = 0,
               south_pass_flag     = 0
         WHERE userID = ?
    """, (user_id,))
    db.commit()
    close(db)

    # Clear everything in-memory
    for key in list(game_state.keys()):
        if isinstance(game_state[key], bool):
            game_state[key] = False
        elif isinstance(game_state[key], int):
            game_state[key] = 0

    game_state["survivors"] = 5
    game_state["party_name"] = ""
    game_state["companions"] = []
    game_state["members"] = []
    game_state["year"] = 1847
    # shot_skill remains 0 until setup assigns it.


# -----------------------------------------------------------------------------
# UTILITY: Remove exactly one person from `members` and decrement survivors.
# -----------------------------------------------------------------------------
def _one_person_dies():
    """
    Remove one random name from game_state["members"], decrement survivors by 1,
    and return “💀 X has died.”  If no one remains, just decrement survivors.
    """
    if game_state["survivors"] <= 0:
        return None

    if game_state["members"]:
        victim = random.choice(game_state["members"])
        game_state["members"].remove(victim)
    else:
        victim = "Someone"

    game_state["survivors"] = max(0, game_state["survivors"] - 1)
    return f"💀 {victim} has died."


# -----------------------------------------------------------------------------
# ALL OTHER HELPER / GAME LOGIC FUNCTIONS (copied + adjusted from your console code).
# When someone dies, we call `_one_person_dies()` exactly once.
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
    """
    Weighted random events (16 types). Trigger roughly every 2 turns.
    Returns a list of messages (some may include one death).
    """
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
    msgs = ["🔧 Wagon breakdown — lose time and supplies fixing it."]
    # Console: lose 8 supplies and some miles
    game_state["distance"] = max(0, game_state["distance"] - (15 + random.randint(0, 5)))
    game_state["misc"] = max(0, game_state["misc"] - 8)  # lose 8 kits
    return msgs


def ox_injures_leg():
    msgs = ["🐂 Ox injures leg — slows you down rest of trip."]
    game_state["distance"] = max(0, game_state["distance"] - 25)
    game_state["oxen_spent"] = max(0, game_state["oxen_spent"] - 20)
    return msgs


def daughter_breaks_arm():
    msgs = [
        "🤕 Back luck — your daughter broke her arm",
        "🩹 You had to stop and use supplies to make a sling."
    ]
    game_state["distance"] = max(0, game_state["distance"] - (5 + random.randint(0, 4)))
    game_state["misc"] = max(0, game_state["misc"] - 2)  # lose 2 kits
    return msgs


def ox_wanders_off():
    msgs = ["🐂 Ox wanders off — spend time looking for it."]
    game_state["distance"] = max(0, game_state["distance"] - 17)
    return msgs


def son_gets_lost():
    msgs = ["👦 Your son gets lost — spend half the day looking for him."]
    game_state["distance"] = max(0, game_state["distance"] - 10)
    return msgs


def unsafe_water():
    msgs = ["💧 Unsafe water — lose time looking for clean spring."]
    game_state["distance"] = max(0, game_state["distance"] - (2 + random.randint(0, 10)))
    return msgs


def heavy_rains():
    msgs = []
    if game_state["distance"] <= 950:
        msgs.append("🌧️ Heavy rains — time and supplies lost.")
        game_state["food"] = max(0, game_state["food"] - 10)
        game_state["bullets"] = max(0, game_state["bullets"] - 500)
        game_state["misc"] = max(0, game_state["misc"] - 15)  # lose 15 kits
        game_state["distance"] = max(0, game_state["distance"] - (5 + random.randint(0, 10)))
    return msgs


def bandits_attack():
    msgs = ["🏴‍☠️ Bandits attack!"]
    msgs.extend(shoot_out())
    return msgs


def wagon_fire():
    msgs = ["🔥 There was a fire in your wagon — food and supplies damaged!"]
    game_state["food"] = max(0, game_state["food"] - 40)
    game_state["bullets"] = max(0, game_state["bullets"] - 400)
    game_state["misc"] = max(0, game_state["misc"] - random.randint(3, 10))  # lose 3–10 kits
    game_state["distance"] = max(0, game_state["distance"] - 15)
    return msgs


def lose_way_in_fog():
    msgs = ["🌫️ Lose your way in heavy fog — time is lost."]
    game_state["distance"] = max(0, game_state["distance"] - (10 + random.randint(0, 5)))
    return msgs


def snake_bite():
    msgs = ["🐍 You killed a poisonous snake after it bit you."]
    game_state["bullets"] = max(0, game_state["bullets"] - 10)
    game_state["misc"] = max(0, game_state["misc"] - 5)  # lose 5 kits
    if game_state["misc"] < 0:
        msgs.append("🩺 You died of snakebite — no medicine.")
        death_msg = _one_person_dies()
        if death_msg:
            msgs.append(death_msg)
    return msgs


def ford_river_swamped():
    msgs = ["🌊 Wagon gets swamped fording river — lose food and clothes."]
    game_state["food"] = max(0, game_state["food"] - 30)
    game_state["clothing"] = max(0, game_state["clothing"] - 20)
    game_state["distance"] = max(0, game_state["distance"] - (20 + random.randint(0, 20)))
    return msgs


def wild_animals_attack():
    msgs = ["🐺 Wild animals attack!"]
    if game_state["bullets"] > 39:
        b1 = random.randint(1, 4)
        if b1 <= 2:
            msgs.append("🎯 Nice shootin' partner — they didn't get much.")
            game_state["bullets"] = max(0, game_state["bullets"] - 20 * b1)
            game_state["clothing"] = max(0, game_state["clothing"] - 4 * b1)
            game_state["food"] = max(0, game_state["food"] - 8 * b1)
        else:
            msgs.append("🐺 Slow on the draw — they got at your food and clothes.")
            game_state["bullets"] = max(0, game_state["bullets"] - 20 * b1)
            game_state["clothing"] = max(0, game_state["clothing"] - 4 * b1)
            game_state["food"] = max(0, game_state["food"] - 8 * b1)
    else:
        msgs.append("⚔️ You were too low on bullets — the wolves overpowered you.")
        msgs.append("💀 One person got injured and died.")
        game_state["injury_flag"] = True
        death_msg = _one_person_dies()
        if death_msg:
            msgs.append(death_msg)
    return msgs


def cold_weather():
    msgs = ["❄️ Cold weather — BRRRRRRR! You "]
    threshold = 22 + 4 * random.random()
    if game_state["clothing"] > threshold:
        msgs[-1] += "have enough clothing to keep you warm."
    else:
        msgs[-1] += "don't have enough clothing to keep you warm."
        msgs.append("💀 One person succumbed to the cold.")
        game_state["injury_flag"] = True
        death_msg = _one_person_dies()
        if death_msg:
            msgs.append(death_msg)
    return msgs


def hail_storm():
    msgs = ["⛈️ Hail storm — supplies damaged."]
    game_state["misc"] = max(0, game_state["misc"] - (random.randint(0, 10) + 4))  # lose 4–14 kits
    game_state["bullets"] = max(0, game_state["bullets"] - 200)
    game_state["food"] = max(0, game_state["food"] - 5)
    return msgs


def friendly_indians():
    msgs = ["🪶 Helpful Indians show you where to find more food and bullets."]
    game_state["food"] += 14
    gained_bullets = random.randint(10, 30)
    game_state["bullets"] += gained_bullets
    msgs.append(f"You gained {gained_bullets} bullets (in addition to 14 food).")
    return msgs


def shoot_out():
    """
    Simulated shoot‐out. Uses shot_skill to weight success (higher skill = better chance).
    Always returns a list of messages—and possibly kills exactly one person.
    """
    msgs = []
    skill = game_state["shot_skill"]
    success_chance = 60 + 10 * (5 - skill)  # easier if skill is high
    if random.randint(1, 100) <= success_chance:
        lost_bullets = random.randint(1, 3) * 20 + 80
        game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
        game_state["food"] += 15
        game_state["money"] = max(0, game_state["money"] - 10)
        msgs.append("🤠 Quickest draw outside of Dodge City! You got 'em!")
    else:
        msgs.append("💥 Lousy shot — you got knifed!")
        game_state["injury_flag"] = True
        game_state["money"] = max(0, game_state["money"] - 20)
        game_state["misc"] = max(0, game_state["misc"] - 5)
        msgs.append("💀 One person got injured and died in the shoot‐out.")
        death_msg = _one_person_dies()
        if death_msg:
            msgs.append(death_msg)
    return msgs


def check_mountains():
    """
    If distance > 950: mountain events. Blizzard chance, travel slowdowns.
    Returns a list of messages, maybe one death.
    """
    msgs = []
    st = game_state
    if st["distance"] <= 950:
        return []

    difficulty = ((st["distance"] / 100 - 15) ** 2 + 72)
    threshold = 9 - difficulty / (difficulty + 12)
    if random.random() * 10 > threshold:
        msgs.append("⛰️ Rugged mountains")
        r = random.random()
        if r < 0.1:
            msgs.append("You got lost — lose valuable time trying to find trail!")
            st["distance"] = max(0, st["distance"] - 60)
        elif 0.1 <= r < 0.11:
            msgs.append("Wagon damaged! — lose time and supplies")
            st["misc"] = max(0, st["misc"] - 5)
            st["bullets"] = max(0, st["bullets"] - 200)
            st["distance"] = max(0, st["distance"] - (20 + 30 * random.random()))
        else:
            msgs.append("The going gets slow")
            st["distance"] = max(0, st["distance"] - (45 + random.random() / 0.02))

        if not st["south_pass_flag"] and st["distance"] >= 1700:
            if random.random() < 0.8:
                msgs.append("🎉 You made it safely through South Pass — no snow")
            else:
                msgs.append("⛄ Blizzard in South Pass — time and supplies lost")
                st["blizzard_flag"] = True
                st["food"] = max(0, st["food"] - 25)
                st["misc"] = max(0, st["misc"] - 10)
                st["bullets"] = max(0, st["bullets"] - 300)
                st["distance"] = max(0, st["distance"] - (30 + 40 * random.random()))
                if st["clothing"] < 18 + 2 * random.random():
                    msgs.append("💀 You died in blizzard — not enough clothing")
                    death_msg = _one_person_dies()
                    if death_msg:
                        msgs.append(death_msg)
            st["south_pass_flag"] = True

    return msgs


def check_illness():
    """
    Each turn, ~45% × 0.5 = ~22.5% chance of a “wild illness.”
    Then ~some smaller chance of “bad illness.” Adjusted so they don't die too quickly.
    Returns a list of messages, maybe one death.
    """
    msgs = []
    st = game_state
    if st["blizzard_flag"] or st["injury_flag"]:
        return []

    # ~22.5% wild illness
    chance_wild = (10 + 35 * (2 - 1))  # because we default e_level=2 (moderate)
    if random.randint(1, 100) < chance_wild * 0.5:
        msgs.append("🤒 Wild illness — medicine used (−2 kits)")
        st["distance"] = max(0, st["distance"] - 5)
        st["misc"] = max(0, st["misc"] - 2)
    else:
        chance_bad = 100 - (40 / (4 ** (2 - 1)))  # 90
        if random.randint(1, 100) < chance_bad * 0.5:
            msgs.append("🤢 Bad illness — medicine used (−5 kits)")
            st["distance"] = max(0, st["distance"] - 5)
            st["misc"] = max(0, st["misc"] - 5)
        else:
            # console says “Serious illness – must stop for medical attention (−10 kits)”
            msgs.append("🤮 Serious illness — must stop for medical attention (−10 kits)")
            st["illness_flag"] = True
            st["misc"] = max(0, st["misc"] - 10)

    if st["misc"] < 0:
        msgs.append("🩺 You ran out of medical supplies — one person died of illness.")
        death_msg = _one_person_dies()
        if death_msg:
            msgs.append(death_msg)
    return msgs


def check_end_conditions():
    """
    Check if starved or arrived. Return list of messages.
    """
    msgs = []
    st = game_state

    # Starvation: lose one person at a time if no food
    if st["food"] <= 0 and st["survivors"] > 0:
        msgs.append("🍽️ You ran out of food — one person starved to death.")
        death_msg = _one_person_dies()
        if death_msg:
            msgs.append(death_msg)

    # Arrival
    if st["distance"] >= TOTAL_TRAIL and st["survivors"] > 0:
        fraction = (TOTAL_TRAIL - st["prev_distance"]) / max(1, (st["distance"] - st["prev_distance"]))
        st["final_fraction"] = fraction
        msgs.append("🏁 You finally arrived at Oregon City — after 2040 long miles! Hooray!")
        msgs.append("🎩 President James K. Polk sends you his heartiest congratulations")
        msgs.append("🎉 And wishes you a prosperous life ahead at your new home")
        st["survivors"] = 0  # end game

    return msgs


def travel_turn(eat_choice=None):
    """
    Travel:
      - Move 10–30 miles
      - Consume 1 lb of food per person
      - Ask the user (via Flask form) whether to eat Poorly/Moderately/Well.
        If no choice supplied, default to “Moderately.”
      - Apply that meal’s cost & bonus:
        * Poorly:   – (8 + 5*1) = –13 food, small bonus
        * Moderately: – (8 + 5*2) = –18 food, medium bonus
        * Well:     – (8 + 5*3) = –23 food, big bonus
      - Every 2 turns, random_event()
      - Then check mountains, illness, end conditions
    All returns exactly what the user will see as flashed messages.
    """
    msgs = []
    st = game_state

    # 1) Move 10–30 miles
    miles = random.randint(10, 30)
    st["prev_distance"] = st["distance"]
    st["distance"] += miles
    msgs.append(f"🚶 You traveled {miles} miles down the trail.")

    # 2) Consume 1 lb food per person
    cost_food = st["survivors"] * 1
    st["food"] = max(0, st["food"] - cost_food)
    msgs.append(f"🥖 You consumed {cost_food} pounds of food.")

    # 3) Advance one day
    st["days_on_trail"] += 1
    st["fort_option_flag"] = True

    # 4) Eating choice
    #   In console: prompt “Do you want to eat (1) Poorly (2) Moderately (3) Well?”
    #   Poorly  → –(8 + 5*1)=–13 food, bonus = 200 + random formula
    #   Moderately → –(8 + 5*2)=–18 food, bigger bonus
    #   Well → –(8 + 5*3)=–23 food, biggest bonus
    #
    #   We require the Flask form to POST `eat_choice` (1, 2, or 3). 
    #   If None or invalid, default to 2 (Moderately).
    e = 2
    if eat_choice in ("1", "2", "3"):
        e = int(eat_choice)
    # cost = 8 + 5* e 
    actual_cost = 8 + 5 * e
    if st["food"] >= actual_cost:
        st["food"] -= actual_cost
        # distance bonus formula (console):
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        if bonus < 0:
            bonus = 0
        st["distance"] += bonus
        meal_str = {1: "Poorly", 2: "Moderately", 3: "Well"}[e]
        msgs.append(f"🍽️ You ate {meal_str} (−{actual_cost} food) and gained a {bonus}-mile bonus.")
    else:
        msgs.append("⚠️ You didn’t have enough food to eat that well, so you ate poorly by default.")
        # Even if they can’t pay full, do as much as possible:
        st["food"] = 0

    # 5) Random events every 2 turns
    st["event_counter"] += 1
    if st["event_counter"] >= 2:
        msgs.extend(random_event())
        st["event_counter"] = 0

    # 6) Mountains / Illness / End‐of‐trail
    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())
    return msgs


def hunt_turn(eat_choice=None):
    """
    Hunt:
      - If no bullets, you fail.
      - Else, random prey quality (1–5):
        * 1 → Miss
        * 2–3 → gained = random.randint(48 − 2*q, 52 + 2*q), cost_bullets = 10 + 3*q
        * 4–5 → gained = random.randint(52, 58), cost_bullets = random.randint(10, 14)
      - Then if ≥ 13 lbs food remain, do the same “eat choice” for a moderate/well/poor meal.
      - Then every 2 turns: random_event()
      - Then mountains, illness, end
    """
    msgs = []
    st = game_state
    if st["bullets"] <= 0:
        msgs.append("🔫 Tough — You need more bullets to go hunting.")
        return msgs

    st["days_on_trail"] += 1
    prey_quality = random.randint(1, 5)
    if prey_quality == 1:
        msgs.append("😞 You missed — and your dinner got away.")
    elif prey_quality <= 3:
        gained = random.randint(48 - 2 * prey_quality, 52 + prey_quality * 2)
        cost_bullets = 10 + 3 * prey_quality
        st["food"] += gained
        st["bullets"] = max(0, st["bullets"] - cost_bullets)
        msgs.append(f"🎯 Nice shot — you gained {gained} food and used {cost_bullets} bullets.")
    else:
        gained = random.randint(52, 58)
        cost_bullets = random.randint(10, 14)
        st["food"] += gained
        st["bullets"] = max(0, st["bullets"] - cost_bullets)
        msgs.append(f"💥 Big shot! You gained {gained} food and used {cost_bullets} bullets.")

    # Eating choice (same as travel)
    e = 2
    if eat_choice in ("1", "2", "3"):
        e = int(eat_choice)
    actual_cost = 8 + 5 * e
    if st["food"] >= actual_cost:
        st["food"] -= actual_cost
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        if bonus < 0:
            bonus = 0
        st["distance"] += bonus
        meal_str = {1: "Poorly", 2: "Moderately", 3: "Well"}[e]
        msgs.append(f"🍽️ You ate {meal_str} (−{actual_cost} food) and gained a {bonus}-mile bonus.")
    else:
        msgs.append("⚠️ You didn’t have enough food to eat that well, so you ate poorly by default.")
        st["food"] = 0

    st["event_counter"] += 1
    if st["event_counter"] >= 2:
        msgs.extend(random_event())
        st["event_counter"] = 0

    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())
    return msgs


def rest_turn(eat_choice=None):
    """
    Rest:
      - 1 day passes, consume 1 lb per person
      - Then if ≥ 13 lbs remain, do a meal choice
      - Then every 2 turns: random_event()
      - Then mountains, illness, end
    """
    msgs = []
    st = game_state

    st["days_on_trail"] += 1
    cost_food = st["survivors"] * 1
    st["food"] = max(0, st["food"] - cost_food)
    msgs.append(f"😴 You rested for a day and used {cost_food} food.")

    # Eating choice
    e = 2
    if eat_choice in ("1", "2", "3"):
        e = int(eat_choice)
    actual_cost = 8 + 5 * e
    if st["food"] >= actual_cost:
        st["food"] -= actual_cost
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        if bonus < 0:
            bonus = 0
        st["distance"] += bonus
        meal_str = {1: "Poorly", 2: "Moderately", 3: "Well"}[e]
        msgs.append(f"🍽️ You ate {meal_str} (−{actual_cost} food) and gained a {bonus}-mile bonus.")
    else:
        msgs.append("⚠️ You didn’t have enough food to eat that well, so you ate poorly by default.")
        st["food"] = 0

    st["event_counter"] += 1
    if st["event_counter"] >= 2:
        msgs.extend(random_event())
        st["event_counter"] = 0

    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())
    return msgs


def fort_turn(eat_choice=None):
    """
    Visit a Fort:
      - If ≥ $25, buy 10 food for $25; else skip
      - If ≥ $10, buy 50 bullets for $10; else skip
      - 1 day passes, consume 1 lb per person
      - Then if ≥ 13 lbs remain, do a meal choice
      - Then every 2 turns: random_event()
      - Then mountains, illness, end
    """
    msgs = []
    st = game_state

    # Buy food if possible
    if st["money"] >= 25:
        st["food"] += 10
        st["money"] -= 25
        msgs.append("🏘️ You bought 10 food at the fort for $25.")
    else:
        msgs.append("🏘️ Not enough money to buy food at the fort.")

    # Buy bullets if possible
    if st["money"] >= 10:
        st["bullets"] += 50
        st["money"] -= 10
        msgs.append("🏘️ You bought 50 bullets at the fort for $10.")
    else:
        msgs.append("🏘️ Not enough money to buy bullets at the fort.")

    st["days_on_trail"] += 1
    cost_food = st["survivors"] * 1
    st["food"] = max(0, st["food"] - cost_food)
    msgs.append(f"😴 You spent a day at the fort and used {cost_food} food.")

    # Eating choice
    e = 2
    if eat_choice in ("1", "2", "3"):
        e = int(eat_choice)
    actual_cost = 8 + 5 * e
    if st["food"] >= actual_cost:
        st["food"] -= actual_cost
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        if bonus < 0:
            bonus = 0
        st["distance"] += bonus
        meal_str = {1: "Poorly", 2: "Moderately", 3: "Well"}[e]
        msgs.append(f"🍽️ You ate {meal_str} (−{actual_cost} food) and gained a {bonus}-mile bonus.")
    else:
        msgs.append("⚠️ You didn’t have enough food to eat that well, so you ate poorly by default.")
        st["food"] = 0

    st["event_counter"] += 1
    if st["event_counter"] >= 2:
        msgs.extend(random_event())
        st["event_counter"] = 0

    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())
    return msgs


def game_turn(action, eat_choice=None):
    """
    Perform exactly one turn based on action: 'travel', 'hunt', 'rest', or 'fort'.
    `eat_choice` is a string "1","2","3" indicating Poorly/Moderately/Well.
    Returns a list of messages to flash.
    """
    msgs = []
    if game_state["survivors"] <= 0 or game_state["distance"] >= TOTAL_TRAIL:
        return ["🔒 Game is already over."]

    if action == "travel":
        msgs = travel_turn(eat_choice)
    elif action == "hunt":
        msgs = hunt_turn(eat_choice)
    elif action == "rest":
        msgs = rest_turn(eat_choice)
    elif action == "fort":
        msgs = fort_turn(eat_choice)
    else:
        msgs = [f"❓ Unknown action: {action}"]

    # Immediately save to the DB so that GET/redirect will show exactly the same values
    save_game_state()
    return msgs
