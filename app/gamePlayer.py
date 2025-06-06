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
    """
    Load the current user's game state from the 'stats' table.
    Any fields not present in the table remain at their in‐memory defaults.
    """
    c, db = connect()
    user_id = session.get("user_id")
    if not user_id:
        close(db)
        return

    row = c.execute("""
        SELECT
            distanceTraveled,   -- → game_state['distance']
            daysPassed,         -- → game_state['days_on_trail']
            survivingPeople,    -- → game_state['survivors']
            foodQuantity,       -- → game_state['food']
            money,              -- → game_state['money']
            oxen,               -- → game_state['oxen_spent']
            bullets,            -- → game_state['bullets']
            event_counter,      -- → game_state['event_counter']
            injury,             -- → game_state['injury_flag']
            illness,            -- → game_state['illness_flag']
            blizzard,           -- → game_state['blizzard_flag']
            fort_flag,          -- → game_state['fort_option_flag']
            south_pass_flag     -- → game_state['south_pass_flag']
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
    """
    Write back only those fields that exist in 'stats'. Anything in-memory‐only
    (clothing, misc, shot_skill, etc.) is not saved until you add them to the schema.
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
    in-memory. The user will have to re-run /setup.
    """
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
    """
    In the console you printed “MONDAY <month> <day>, 1847.” We replicate that:
    """
    d3 = game_state["days_on_trail"]
    if d3 == 0:
        return "MONDAY March 29, 1847"
    if 1 <= d3 <= len(DATE_SCHEDULE):
        month, day = DATE_SCHEDULE[d3 - 1]
        return f"MONDAY {month} {day}, 1847"
    return None


def random_event():
    """
    Exactly your console thresholds [6,11,13,15,17,22,32,35,37,42,44,54,64,69,95].
    Return a list of messages describing that event.
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
    msgs = ["WAGON BREAKS DOWN — LOSE TIME AND SUPPLIES FIXING IT."]
    # mileage -= random(1..5), supplies -= 8 in console but we'll interpret “8 supplies” as 8 misc kits.
    mileage_loss = random.randint(1, 5)
    game_state["distance"] = max(0, game_state["distance"] - mileage_loss)
    game_state["misc"] = max(0, game_state["misc"] - 8)
    msgs.append(f"Lost {mileage_loss} miles, used 8 misc kits (if available).")
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
    game_state["misc"] = max(0, game_state["misc"] - (2 + random.randint(0, 3)))
    msgs.append(f"Lost {mileage_loss} miles, used 2–5 misc kits.")
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
    """
    In your console: if distance ≤ 950, lose 10 food, 500 bullets, 15 supplies, 
    and 2–10 miles; otherwise nothing.
    """
    msgs = []
    if game_state["distance"] <= 950:
        msgs.append("HEAVY RAINS — TIME AND SUPPLIES LOST")
        lost_food = min(game_state["food"], 10)
        lost_bullets = min(game_state["bullets"], 500)
        lost_misc = min(game_state["misc"], 15)
        game_state["food"] = max(0, game_state["food"] - lost_food)
        game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
        game_state["misc"] = max(0, game_state["misc"] - lost_misc)
        mileage_loss = 5 + random.randint(0, 10)
        game_state["distance"] = max(0, game_state["distance"] - mileage_loss)
        msgs.append(f"Lost {lost_food} food, {lost_bullets} bullets, {lost_misc} misc kits, {mileage_loss} miles.")
    return msgs


def bandits_attack():
    msgs = ["BANDITS ATTACK!"]
    msgs.extend(shoot_out())
    return msgs


def wagon_fire():
    msgs = ["THERE WAS A FIRE IN YOUR WAGON — FOOD AND SUPPLIES DAMAGED!"]
    lost_food = min(game_state["food"], 40)
    lost_bullets = min(game_state["bullets"], 400)
    lost_misc = min(game_state["misc"], random.randint(3, 10))
    game_state["food"] = max(0, game_state["food"] - lost_food)
    game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
    game_state["misc"] = max(0, game_state["misc"] - lost_misc)
    game_state["distance"] = max(0, game_state["distance"] - 15)
    msgs.append(f"Lost {lost_food} food, {lost_bullets} bullets, {lost_misc} misc kits, 15 miles.")
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
    game_state["misc"] = max(0, game_state["misc"] - 5)
    msgs.append(f"Lost {lost_bullets} bullets, 5 misc kits.")
    if game_state["misc"] < 0:
        msgs.append("YOU DIED OF SNAKEBITE SINCE YOU HAVE NO MEDICINE")
        game_state["survivors"] = 0
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
    lost_misc = min(game_state["misc"], 4 + random.randint(0, 3))
    lost_bullets = min(game_state["bullets"], 200)
    lost_food = min(game_state["food"], 5)
    game_state["misc"] = max(0, game_state["misc"] - lost_misc)
    game_state["bullets"] = max(0, game_state["bullets"] - lost_bullets)
    game_state["food"] = max(0, game_state["food"] - lost_food)
    msgs.append(f"Lost {lost_misc} misc kits, {lost_bullets} bullets, {lost_food} food.")
    return msgs


def friendly_indians():
    msgs = ["HELPFUL INDIANS SHOW YOU WHERE TO FIND MORE FOOD"]
    game_state["food"] += 14
    msgs.append("Gained 14 food.")
    return msgs


def shoot_out():
    """
    Subroutine for attacking hostile bandits (or animals).  
    Uses your shot_skill in exactly the same formula as your console:
      success_chance = 60 + 10 * (5 - shot_skill).
    """
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
    """
    If distance > 950, there's a chance of a rugged mountains event.  
    Exactly matches your console logic, including South Pass checks.
    """
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
            lost_misc = min(st["misc"], 5)
            lost_bullets = min(st["bullets"], 200)
            mileage_loss = 20 + 30 * random.random()
            st["misc"] -= lost_misc
            st["bullets"] -= lost_bullets
            st["distance"] = max(0, st["distance"] - int(mileage_loss))
            msgs.append(f"Used {lost_misc} misc kits, lost {lost_bullets} bullets, ~{int(mileage_loss)} miles.")
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
                lost_misc = min(st["misc"], 10)
                lost_bullets = min(st["bullets"], 300)
                mileage_loss = 30 + 40 * random.random()
                st["food"] -= lost_food
                st["misc"] -= lost_misc
                st["bullets"] -= lost_bullets
                st["distance"] = max(0, st["distance"] - int(mileage_loss))
                msgs.append(f"Lost {lost_food} food, {lost_misc} misc kits, {lost_bullets} bullets, ~{int(mileage_loss)} miles.")
                if st["clothing"] < 18 + 2 * random.random():
                    msgs.append("YOU DIED IN BLIZZARD — NOT ENOUGH CLOTHING")
                    st["survivors"] = 0
            st["south_pass_flag"] = True

    return msgs


def check_illness():
    """
    Mirroring your console code's exact percentages:
      - Wild Illness:    < 10 + 35 * (eating_choice − 1)  (needs medicine)
      - Bad Illness:     elif < 100 − (40 / (4^(eating_choice − 1))) (needs medicine)
      - Else:            Serious Ill — “must stop for Medical Attention” (–10 misc kits)

    If misc kits < 10 after that, you “die of no_supplies.”
    """
    msgs = []
    st = game_state

    if st["blizzard_flag"] or st["injury_flag"]:
        return []

    e_level = st.get("eating_choice", 2)


    if random.randint(1, 100) < 10 + 35 * (e_level - 1):
        msgs.append("WILD ILLNESS — MEDICINE USED")
        st["distance"] = max(0, st["distance"] - 5)
        st["misc"] = st["misc"] - 2
        msgs.append("Lost 5 miles, used 2 misc kits.")

    elif random.randint(1, 100) < int(100 - (40 / (4 ** (e_level - 1)))):
        msgs.append("BAD ILLNESS — MEDICINE USED")
        st["distance"] = max(0, st["distance"] - 5)
        st["misc"] = st["misc"] - 5
        msgs.append("Lost 5 miles, used 5 misc kits.")
    else:
        msgs.append("SERIOUS ILLNESS — YOU MUST STOP FOR MEDICAL ATTENTION")
        st["illness_flag"] = False
        st["misc"] = st["misc"] - 10
        msgs.append("Used 10 misc kits.")

    if st["misc"] < 10:
        msgs.append("YOU RAN OUT OF MEDICAL SUPPLIES — YOU DIED OF ILLNESS")
        st["survivors"] = 0

    return msgs


def check_end_conditions():
    """
    Check if starved or arrived.
    """
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
    """
    EXACTLY as your console `eat_and_travel` + event checks:
      - Travel 10–30 miles
      - Consume 2 lbs of food per person
      - If food ≥ 13, do a moderate meal (−18 food) and gain a bonus
      - Then random_event() if event_counter ≥ 1
      - Then check_mountains, check_illness, check_end_conditions
    """
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
    """
    EXACTLY as your console `hunt_turn`:
      - If bullets ≤ 0, fail
      - days_on_trail += 1
      - Random prey quality (1..5):
          * 1 → Missed
          * 2–3 → gain 48–52 ± small, bullets − (10 + 3*quality)
          * 4–5 → gain 52–58 ± small, bullets − (10–14)
      - Then if food ≥ 13 → moderate meal (−18, plus bonus)
      - Then random_event, mountains, illness, end checks
    """
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
    """
    EXACTLY as your console `rest_turn`:
      - days_on_trail += 1
      - Consume 1 lb of food per person
      - If food ≥ 13 → moderate meal (−18, plus bonus)
      - Then random_event, mountains, illness, end
    """
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
    """
    EXACTLY as your console's “Visit Fort” logic (in your console, 
    you bought at a reduced 2/3 price on all items—but we simplify
    as in your console code snippet: 1 day passes, you spend up to 
    whatever, etc.  We replicate your console `fort()` almost verbatim).
    """
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
    """
    Called by Flask each time the user posts “action=travel/hunt/rest/fort.” 
    Return a list of strings to flash. If the game is already over, return a single message.
    """
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
