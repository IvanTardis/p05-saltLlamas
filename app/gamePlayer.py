import random
from flask import session
from database import connect, close

game_state = {
    "party_name": "",
    "companions": [],
    "distance": 0,
    "prev_distance": 0,
    "days_on_trail": 0,
    "food": 0,
    "money": 0,
    "oxen_spent": 0,
    "bullets": 0,
    "event_counter": 0,
    "injury_flag": False,
    "illness_flag": False,
    "blizzard_flag": False,
    "fort_option_flag": False,
    "south_pass_flag": False,
    "survivors": 5,
    "clothing": 0,
    "misc": 0,
    "shot_skill": 0,
    "blue_mountains_flag": False,
    "final_fraction": 0
}

TOTAL_TRAIL = 2040

DATE_SCHEDULE = [
    ("March", 29), ("April", 12), ("April", 26), ("May", 10), ("May", 24),
    ("June", 7), ("June", 21), ("July", 5), ("July", 19), ("August", 2),
    ("August", 16), ("August", 31), ("September", 13), ("September", 27),
    ("October", 11), ("October", 25), ("November", 8), ("November", 22),
    ("December", 6), ("December", 20)
]

def load_game_state():
    c, db = connect()
    user_id = session.get("user_id")
    if not user_id:
        close(db)
        return
    row = c.execute("""
        SELECT
            distanceTraveled,
            daysPassed,
            survivingPeople,
            foodQuantity,
            money,
            oxen,
            bullets,
            event_counter,
            injury,
            illness,
            blizzard,
            fort_flag,
            south_pass_flag
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

def save_game_state():
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
    c, db = connect()
    user_id = session.get("user_id")
    if not user_id:
        close(db)
        return
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
    for key in list(game_state.keys()):
        if isinstance(game_state[key], bool):
            game_state[key] = False
        elif isinstance(game_state[key], int):
            game_state[key] = 0
    game_state["survivors"] = 5
    game_state["party_name"] = ""
    game_state["companions"] = []
    game_state["shot_skill"] = 0

def get_current_date_message():
    d3 = game_state["days_on_trail"]
    if d3 == 0:
        return "MONDAY March 29, 1847"
    if 1 <= d3 <= len(DATE_SCHEDULE):
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
    mileage_loss = random.randint(1, 5)
    game_state["distance"] = max(0, game_state["distance"] - mileage_loss)
    msgs.append(f"Lost {mileage_loss} miles.")
    return msgs

def ox_injures_leg():
    msgs = ["OX INJURES LEG — SLOWS YOU DOWN FOR THE REST OF TRIP"]
    game_state["distance"] = max(0, game_state["distance"] - 25)
    game_state["oxen_spent"] = max(0, game_state["oxen_spent"] - 20)
    msgs.append("Lost 25 miles, lost $20 of oxen value.")
    return msgs

def daughter_breaks_arm():
    msgs = [
        "BACK LUCK — YOUR DAUGHTER BROKE HER ARM",
        "YOU HAD TO STOP AND USE SUPPLIES TO MAKE A SLING"
    ]
    mileage_loss = 5 + random.randint(0, 4)
    game_state["distance"] = max(0, game_state["distance"] - mileage_loss)
    msgs.append(f"Lost {mileage_loss} miles.")
    return msgs

def ox_wanders_off():
    msgs = ["OX WANDERS OFF — SPEND TIME LOOKING FOR IT"]
    game_state["distance"] = max(0, game_state["distance"] - 17)
    msgs.append("Lost 17 miles.")
    return msgs

def son_gets_lost():
    msgs = ["YOUR SON GETS LOST — SPEND HALF THE DAY LOOKING FOR HIM"]
    game_state["distance"] = max(0, game_state["distance"] - 10)
    msgs.append("Lost 10 miles.")
    return msgs

def unsafe_water():
    msgs = ["UNSAFE WATER — LOSE TIME LOOKING FOR CLEAN SPRING"]
    mileage_loss = 2 + random.randint(0, 10)
    game_state["distance"] = max(0, game_state["distance"] - mileage_loss)
    msgs.append(f"Lost {mileage_loss} miles.")
    return msgs

def heavy_rains():
    msgs = []
    if game_state["distance"] <= 950:
        msgs.append("HEAVY RAINS — TIME AND SUPPLIES LOST")
        lost_food = min(game_state["food"], 10)
        lost_bullets = min(game_state["bullets"], 500)
        game_state["food"] = max(0, game_state["food"] - lost_food)
        game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
        mileage_loss = 5 + random.randint(0, 10)
        game_state["distance"] = max(0, game_state["distance"] - mileage_loss)
        msgs.append(f"Lost {lost_food} food, {lost_bullets} bullets, {mileage_loss} miles.")
    return msgs

def bandits_attack():
    msgs = ["BANDITS ATTACK!"]
    msgs.extend(shoot_out())
    return msgs

def wagon_fire():
    msgs = ["THERE WAS A FIRE IN YOUR WAGON — FOOD AND SUPPLIES DAMAGED!"]
    lost_food = min(game_state["food"], 40)
    lost_bullets = min(game_state["bullets"], 400)
    game_state["food"] = max(0, game_state["food"] - lost_food)
    game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
    game_state["distance"] = max(0, game_state["distance"] - 15)
    msgs.append(f"Lost {lost_food} food, {lost_bullets} bullets, 15 miles.")
    return msgs

def lose_way_in_fog():
    msgs = ["LOSE YOUR WAY IN HEAVY FOG — TIME IS LOST"]
    mileage_loss = 10 + random.randint(0, 5)
    game_state["distance"] = max(0, game_state["distance"] - mileage_loss)
    msgs.append(f"Lost {mileage_loss} miles.")
    return msgs

def snake_bite():
    msgs = ["YOU KILLED A POISONOUS SNAKE AFTER IT BIT YOU"]
    lost_bullets = min(game_state["bullets"], 10)
    game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
    msgs.append(f"Lost {lost_bullets} bullets.")
    if game_state["misc"] <= 0:
        victim = _pick_victim()
        msgs.append(f"{victim} died of snakebite.")
        game_state["survivors"] -= 1
    return msgs

def ford_river_swamped():
    msgs = ["WAGON GETS SWAMPED FORDING RIVER — LOSE FOOD AND CLOTHES"]
    lost_food = min(game_state["food"], 30)
    lost_clothing = min(game_state["clothing"], 20)
    game_state["food"] = max(0, game_state["food"] - lost_food)
    game_state["clothing"] = max(0, game_state["clothing"] - lost_clothing)
    mileage_loss = 20 + random.randint(0, 20)
    game_state["distance"] = max(0, game_state["distance"] - mileage_loss)
    msgs.append(f"Lost {lost_food} food, {lost_clothing} clothing, {mileage_loss} miles.")
    return msgs

def wild_animals_attack():
    msgs = ["WILD ANIMALS ATTACK!"]
    if game_state["bullets"] > 39:
        b1 = random.randint(1, 4)
        if b1 <= 2:
            msgs.append("NICE SHOOTIN' PARTNER — THEY DIDN'T GET MUCH")
            lost_bullets = min(game_state["bullets"], 20 * b1)
            lost_clothing = min(game_state["clothing"], 4 * b1)
            lost_food = min(game_state["food"], 8 * b1)
            game_state["bullets"] -= lost_bullets
            game_state["clothing"] -= lost_clothing
            game_state["food"] -= lost_food
            msgs.append(f"Lost {lost_bullets} bullets, {lost_clothing} clothing, {lost_food} food.")
        else:
            msgs.append("SLOW ON THE DRAW — THEY GOT AT YOUR FOOD AND CLOTHES")
            lost_bullets = min(game_state["bullets"], 20 * b1)
            lost_clothing = min(game_state["clothing"], 4 * b1)
            lost_food = min(game_state["food"], 8 * b1)
            game_state["bullets"] -= lost_bullets
            game_state["clothing"] -= lost_clothing
            game_state["food"] -= lost_food
            msgs.append(f"Lost {lost_bullets} bullets, {lost_clothing} clothing, {lost_food} food.")
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
    lost_bullets = min(game_state["bullets"], 200)
    lost_food = min(game_state["food"], 5)
    game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
    game_state["food"] = max(0, game_state["food"] - lost_food)
    msgs.append(f"Lost {lost_bullets} bullets, {lost_food} food.")
    return msgs

def friendly_indians():
    msgs = ["HELPFUL INDIANS SHOW YOU WHERE TO FIND MORE FOOD"]
    game_state["food"] += 14
    msgs.append("Gained 14 food.")
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
        msgs.append(f"QUICKEST DRAW OUTSIDE OF DODGE CITY!!! YOU GOT 'EM! Lost {lost_bullets} bullets, +15 food, −$10.")
    else:
        msgs.append("LOUSY SHOT — YOU GOT KNIFED!")
        game_state["injury_flag"] = True
        game_state["money"] = max(0, game_state["money"] - 20)
        game_state["misc"] = max(0, game_state["misc"] - 5)
        msgs.append("Used 5 misc kits for treatment (if available).")
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
            msgs.append("YOU GOT LOST — LOSE VALUABLE TIME TRYING TO FIND THE TRAIL!")
            st["distance"] = max(0, st["distance"] - 60)
        elif 0.1 <= r < 0.21:
            msgs.append("WAGON DAMAGED! — LOSE TIME AND SUPPLIES")
            lost_bullets = min(st["bullets"], 200)
            mileage_loss = 20 + 30 * random.random()
            st["bullets"] -= lost_bullets
            st["distance"] = max(0, st["distance"] - int(mileage_loss))
            msgs.append(f"Lost {lost_bullets} bullets, ~{int(mileage_loss)} miles.")
        else:
            msgs.append("THE GOING GETS SLOW")
            mileage_loss = 45 + random.random() / 0.02
            st["distance"] = max(0, st["distance"] - int(mileage_loss))
            msgs.append(f"Lost ~{int(mileage_loss)} miles.")
        if not st["south_pass_flag"] and st["distance"] >= 1700:
            if random.random() < 0.8:
                msgs.append("YOU MADE IT SAFELY THROUGH SOUTH PASS — NO SNOW")
            else:
                msgs.append("BLIZZARD IN SOUTH PASS — TIME AND SUPPLIES LOST")
                st["blizzard_flag"] = True
                lost_food = min(st["food"], 25)
                lost_bullets = min(st["bullets"], 300)
                mileage_loss = 30 + 40 * random.random()
                st["food"] -= lost_food
                st["bullets"] -= lost_bullets
                st["distance"] = max(0, st["distance"] - int(mileage_loss))
                msgs.append(f"Lost {lost_food} food, {lost_bullets} bullets, ~{int(mileage_loss)} miles.")
                if st["clothing"] < 18 + 2 * random.random():
                    msgs.append("YOU DIED IN BLIZZARD — NOT ENOUGH CLOTHING")
                    st["survivors"] = 0
            st["south_pass_flag"] = True
    return msgs

def check_illness():
    msgs = []
    st = game_state
    # Skip illness if already in blizzard or injured
    if st["blizzard_flag"] or st["injury_flag"]:
        return []

    roll = random.randint(1, 100)
    # Only a 5% chance of any illness event
    if roll <= 5:
        # Determine type of illness: wild (30% of illness cases) vs. bad (70%)
        if random.random() < 0.3:
            cost = 2
            label = "WILD ILLNESS — MEDICINE USED"
        else:
            cost = 5
            label = "BAD ILLNESS — MEDICINE USED"

        msgs.append(label)
        st["distance"] = max(0, st["distance"] - 5)

        if st["misc"] >= cost:
            st["misc"] -= cost
            msgs.append(f"Used {cost} misc kits—everyone recovers.")
        else:
            # Not enough misc, one person dies
            victim = _pick_victim()
            msgs.append(f"{victim} died of illness.")
            st["survivors"] = max(0, st["survivors"] - 1)

    return msgs

def _pick_victim():
    party = []
    if game_state["party_name"]:
        party.append(game_state["party_name"])
    party.extend(game_state["companions"])
    return random.choice(party) if party else "A party member"



def _pick_victim():
    party = []
    if game_state["party_name"]:
        party.append(game_state["party_name"])
    party.extend(game_state["companions"])
    if not party:
        return "A party member"
    return random.choice(party)

def check_end_conditions():
    msgs = []
    st = game_state
    if st["food"] <= 0 and st["survivors"] > 0:
        msgs.append("YOU RAN OUT OF FOOD AND STARVED TO DEATH.")
        st["survivors"] = 0
    if st["distance"] >= TOTAL_TRAIL and st["survivors"] > 0:
        fraction = (TOTAL_TRAIL - st["prev_distance"]) / max(1, st["distance"] - st["prev_distance"])
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
    cost_food = st["survivors"] * 2
    st["food"] = max(0, st["food"] - cost_food)
    msgs.append(f"You consumed {cost_food} lbs of food.")
    st["days_on_trail"] += 1
    st["fort_option_flag"] = True
    if st["food"] >= 13:
        st["food"] -= 18
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        st["distance"] += max(0, bonus)
        msgs.append(f"You ate a moderate meal (−18 food) and gained a {bonus}-mile bonus from healthy oxen.")
    st["event_counter"] += 1
    if st["event_counter"] >= 1:
        ev_msgs = random_event()
        if ev_msgs:
            msgs.extend(ev_msgs)
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
        gained = random.randint(48 - 2 * prey_quality, 52 + 2 * prey_quality)
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
        msgs.append(f"You ate a moderate meal (−18 food) and gained a {bonus}-mile bonus.")
    st["event_counter"] += 1
    if st["event_counter"] >= 1:
        ev_msgs = random_event()
        if ev_msgs:
            msgs.extend(ev_msgs)
        st["event_counter"] = 0
    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())
    return msgs

def rest_turn():
    msgs = []
    st = game_state
    st["days_on_trail"] += 1
    cost_food = st["survivors"] * 1
    st["food"] = max(0, st["food"] - cost_food)
    msgs.append(f"You rested for a day and used {cost_food} food.")
    if st["food"] >= 13:
        st["food"] -= 18
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        st["distance"] += max(0, bonus)
        msgs.append(f"You ate a moderate meal (−18 food) and gained a {bonus}-mile bonus.")
    st["event_counter"] += 1
    if st["event_counter"] >= 1:
        ev_msgs = random_event()
        if ev_msgs:
            msgs.extend(ev_msgs)
        st["event_counter"] = 0
    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())
    return msgs

def fort_turn():
    msgs = []
    st = game_state
    msgs.append("You arrive at the next fort.")
    msgs.append("No purchases at the Fort (placeholder logic).")
    st["days_on_trail"] += 1
    cost_food = st["survivors"] * 1
    st["food"] = max(0, st["food"] - cost_food)
    msgs.append(f"Used {cost_food} food while at the fort.")
    if st["food"] >= 13:
        st["food"] -= 18
        bonus = int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                    (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
        st["distance"] += max(0, bonus)
        msgs.append(f"You ate a moderate meal (−18 food) and gained a {bonus}-mile bonus.")
    st["event_counter"] += 1
    if st["event_counter"] >= 1:
        ev_msgs = random_event()
        if ev_msgs:
            msgs.extend(ev_msgs)
        st["event_counter"] = 0
    msgs.extend(check_mountains())
    msgs.extend(check_illness())
    msgs.extend(check_end_conditions())
    return msgs

def game_turn(action):
    msgs = []
    st = game_state
    if st["survivors"] <= 0 or st["distance"] >= TOTAL_TRAIL:
        return ["Game is already over. No further actions possible."]
    if action == "travel":
        msgs = travel_turn()
    elif action == "hunt":
        msgs = hunt_turn()
    elif action == "rest":
        msgs = rest_turn()
    elif action == "fort":
        if not st["fort_option_flag"]:
            msgs = ["Fort is not yet available."]
        else:
            msgs = fort_turn()
    else:
        msgs = [f"Unknown action: {action}"]
    save_game_state()
    return msgs
