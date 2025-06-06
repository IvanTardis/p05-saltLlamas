import random
import sys
import time

# Game state variables
game_state = {
    "distance": 0,             # M = total miles traveled this trip
    "prev_distance": 0,        # M2 = miles at end of previous turn
    "days_on_trail": 0,        # D3 = turn counter (each turn = 2 weeks increments)
    "year": 1847,              # Fixed starting year
    "day_of_turn": 0,          # Used to calculate exact date from D3
    "food": 0,                 # F = pounds of food remaining
    "bullets": 0,              # B = number of bullets
    "clothing": 0,             # C = amount spent on clothing (used for cold protection)
    "misc": 0,                 # M1 = amount spent on miscellaneous supplies
    "money": 0,                # T = cash on hand
    "oxen_spent": 0,           # A = dollars spent on oxen team
    "shot_skill": 0,           # D9 = rated shooting skill (1–5)
    "illness_flag": False,     # S4 = currently sick
    "injury_flag": False,      # K8 = currently injured
    "blizzard_flag": False,    # L1 = currently in blizzard
    "south_pass_flag": False,  # F1 = have cleared South Pass?
    "blue_mountains_flag": False,  # F2 = have cleared Blue Mountains?
    "fort_option_flag": False, # X1 = whether forts are an option (>0 after first turn)
    "event_counter": 0,        # D1 = counter when choosing a random event
    "final_fraction": 0,       # F9 = fraction of final two-week period on last turn
    "survivors": 5            # number of people still alive
}

# Constants
TOTAL_TRAIL = 2040  # total miles from Independence, MO to Oregon City, OR


# Date lookup: each turn is 14 days (2 weeks). We'll map D3 to calendar dates.
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


def print_instructions():
    print("\n" * 2)
    print("THIS PROGRAM SIMULATES A TRIP OVER THE OREGON TRAIL FROM")
    print("INDEPENDENCE, MISSOURI TO OREGON CITY, OREGON IN 1847.")
    print("YOUR FAMILY OF FIVE WILL COVER THE 2040 MILE OREGON TRAIL")
    print("IN 5-6 MONTHS --- IF YOU MAKE IT ALIVE.\n")
    print("YOU HAD SAVED $900 TO SPEND FOR THE TRIP, AND YOU'VE JUST")
    print("   PAID $200 FOR A WAGON.")
    print("YOU WILL NEED TO SPEND THE REST OF YOUR MONEY ON THE")
    print("   FOLLOWING ITEMS:\n")
    print("     OXEN - YOU CAN SPEND $200-$300 ON YOUR TEAM")
    print("            THE MORE YOU SPEND, THE FASTER YOU'LL GO")
    print("               BECAUSE YOU'LL HAVE BETTER ANIMALS\n")
    print("     FOOD - THE MORE YOU HAVE, THE LESS CHANCE THERE")
    print("               IS OF GETTING SICK\n")
    print("     AMMUNITION - $1 BUYS A BELT OF 50 BULLETS")
    print("            YOU WILL NEED BULLETS FOR ATTACKS BY ANIMALS")
    print("               AND BANDITS, AND FOR HUNTING FOOD\n")
    print("     CLOTHING - THIS IS ESPECIALLY IMPORTANT FOR THE COLD")
    print("               WEATHER YOU WILL ENCOUNTER WHEN CROSSING")
    print("               THE MOUNTAINS\n")
    print("     MISCELLANEOUS SUPPLIES - THIS INCLUDES MEDICINE AND")
    print("               OTHER THINGS YOU WILL NEED FOR SICKNESS")
    print("               AND EMERGENCY REPAIRS\n")
    print("\nYOU CAN SPEND ALL YOUR MONEY BEFORE YOU START YOUR TRIP -")
    print("OR YOU CAN SAVE SOME OF YOUR CASH TO SPEND AT FORTS ALONG")
    print("THE WAY WHEN YOU RUN LOW. HOWEVER, ITEMS COST MORE AT")
    print("THE FORTS. YOU CAN ALSO GO HUNTING ALONG THE WAY TO GET")
    print("MORE FOOD.")
    print("\nWHENEVER YOU HAVE TO USE YOUR TRUSTY RIFLE ALONG THE WAY,")
    print("YOU WILL BE TOLD TO TYPE IN A WORD (ONE THAT SOUNDS LIKE A")
    print("GUN SHOT). THE FASTER YOU TYPE IN THAT WORD AND HIT THE")
    print('"RETURN" KEY, THE BETTER LUCK YOU\'LL HAVE WITH YOUR GUN."\n')
    print("AT EACH TURN, ALL ITEMS ARE SHOWN IN DOLLAR AMOUNTS")
    print("EXCEPT BULLETS")
    print('WHEN ASKED TO ENTER MONEY AMOUNTS, DON\'T USE A "$".\n')
    print("GOOD LUCK!!!\n")


def get_shooting_skill():
    while True:
        print("HOW GOOD A SHOT ARE YOU WITH YOUR RIFLE?")
        print("  (1) ACE MARKSMAN,  (2) GOOD SHOT,  (3) FAIR TO MIDDLIN'")
        print("         (4) NEED MORE PRACTICE,  (5) SHAKY KNEES")
        choice = input("ENTER ONE OF THE ABOVE -- ")
        try:
            val = int(choice)
            if 1 <= val <= 5:
                return val
        except ValueError:
            pass
        print("PLEASE ENTER A NUMBER FROM 1 TO 5.")


def initial_purchases():
    """
    Ask the player to allocate their $700 (after $200 for wagon) among
    oxen, food, ammunition, clothing, and miscellaneous supplies.
    """
    state = game_state
    state["money"] = 700

    # Oxen: must spend between 200 and 300
    while True:
        try:
            amt = int(input("HOW MUCH DO YOU WANT TO SPEND ON YOUR OXEN TEAM? "))
            if 200 <= amt <= 300:
                state["oxen_spent"] = amt
                state["money"] -= amt
                break
            elif amt < 200:
                print("NOT ENOUGH. MINIMUM IS $200.")
            else:
                print("TOO MUCH. MAXIMUM IS $300.")
        except ValueError:
            print("ENTER A VALID INTEGER AMOUNT.")

    # Food
    while True:
        try:
            amt = int(input("HOW MUCH DO YOU WANT TO SPEND ON FOOD? "))
            if amt >= 0 and amt <= state["money"]:
                state["food"] = amt  # store dollars; conversion to pounds happens in-turn
                state["money"] -= amt
                break
            else:
                print("IMPOSSIBLE: Enter a non‐negative amount ≤ your remaining money.")
        except ValueError:
            print("ENTER A VALID INTEGER AMOUNT.")

    # Ammunition
    while True:
        try:
            amt = int(input("HOW MUCH DO YOU WANT TO SPEND ON AMMUNITION? "))
            if amt >= 0 and amt <= state["money"]:
                state["bullets"] = amt * 50  # $1 buys 50 bullets
                state["money"] -= amt
                break
            else:
                print("IMPOSSIBLE: Enter a non‐negative amount ≤ your remaining money.")
        except ValueError:
            print("ENTER A VALID INTEGER AMOUNT.")

    # Clothing
    while True:
        try:
            amt = int(input("HOW MUCH DO YOU WANT TO SPEND ON CLOTHING? "))
            if amt >= 0 and amt <= state["money"]:
                state["clothing"] = amt
                state["money"] -= amt
                break
            else:
                print("IMPOSSIBLE: Enter a non‐negative amount ≤ your remaining money.")
        except ValueError:
            print("ENTER A VALID INTEGER AMOUNT.")

    # Miscellaneous supplies
    while True:
        try:
            amt = int(input("HOW MUCH DO YOU WANT TO SPEND ON MISCELLANEOUS SUPPLIES? "))
            if amt >= 0 and amt <= state["money"]:
                state["misc"] = amt
                state["money"] -= amt
                break
            else:
                print("IMPOSSIBLE: Enter a non‐negative amount ≤ your remaining money.")
        except ValueError:
            print("ENTER A VALID INTEGER AMOUNT.")

    print(f"\nAFTER ALL YOUR PURCHASES, YOU NOW HAVE ${state['money']} LEFT.\n")
    print("MONDAY MARCH 29 1847\n")


def display_status():
    """
    Display current game status: mileage, supplies, cash, etc.
    """
    st = game_state
    miles = st["distance"]
    food = st["food"]
    bullets = st["bullets"]
    clothing = st["clothing"]
    misc = st["misc"]
    cash = st["money"]

    print(f"TOTAL MILEAGE: {miles}")
    print(f"FOOD (dollars): {food}")
    print(f"BULLETS: {bullets}")
    print(f"CLOTHING (dollars): {clothing}")
    print(f"MISC. SUPPLIES (dollars): {misc}")
    print(f"CASH: ${cash}\n")


def current_date_str():
    """
    Given D3 (turn counter), return the date string. Each turn is 14 days.
    """
    d3 = game_state["days_on_trail"]
    if d3 <= 20:
        month, day = DATE_SCHEDULE[d3 - 1]
        return f"{month} {day}, {game_state['year']}"
    else:
        # If they've been on the trail too long
        return None


def prompt_action():
    """
    Ask the player what they want to do each turn:
    If first turn, they can only Hunt or Continue.
    Otherwise, they can Stop at Fort, Hunt, or Continue.
    """
    st = game_state
    if not st["fort_option_flag"]:
        while True:
            print("DO YOU WANT TO (1) HUNT, OR (2) CONTINUE?")
            choice = input()
            if choice == "1":
                return "hunt"
            elif choice == "2":
                return "continue"
            else:
                print("ENTER 1 OR 2, PLEASE.")
    else:
        while True:
            print("DO YOU WANT TO (1) STOP AT THE NEXT FORT, (2) HUNT, OR (3) CONTINUE?")
            choice = input()
            if choice in ("1", "2", "3"):
                return {"1": "fort", "2": "hunt", "3": "continue"}[choice]
            else:
                print("ENTER 1, 2, OR 3, PLEASE.")


def eat_and_travel(food_consumption_multiplier=2):
    """
    When traveling, consume food: each person eats 2 pounds per turn by default.
    """
    st = game_state
    st["distance"] += random.randint(10, 30)  # travel 10–30 miles
    food_cost = st["survivors"] * food_consumption_multiplier
    st["food"] -= food_cost
    st["days_on_trail"] += 1
    # After first turn, forts become an option
    st["fort_option_flag"] = True


def hunt():
    st = game_state
    if st["bullets"] <= 0:
        print("TOUGH — YOU NEED MORE BULLETS TO GO HUNTING.")
        return

    st["days_on_trail"] += 1
    st["distance"] -= 0  # no miles traveled
    prey_quality = random.randint(1, 5)
    # Simplified outcome: multiply prey_quality to yield random food
    if prey_quality == 1:
        print("YOU MISSED — AND YOUR DINNER GOT AWAY.")
    elif prey_quality <= 3:
        gained = random.randint(48 - 2 * prey_quality, 52 + prey_quality * 2)
        print("NICE SHOT — RIGHT ON TARGET — GOOD EATIN' TONIGHT!!")
        st["food"] += gained
        st["bullets"] -= (10 + 3 * prey_quality)
    else:
        print("RIGHT BETWEEN THE EYES — YOU GOT A BIG ONE! FULL BELLIES TONIGHT!")
        gained = random.randint(52, 58)
        st["food"] += gained
        st["bullets"] -= random.randint(10, 14)
    # Cap food at a minimum of 0
    if st["food"] < 0:
        st["food"] = 0


def eat_meal():
    """
    If food >= 13, they must choose to eat poorly (1), moderately (2), or well (3).
    """
    st = game_state
    while True:
        print("DO YOU WANT TO EAT (1) POORLY  (2) MODERATELY  (3) WELL?")
        choice = input()
        if choice not in ("1", "2", "3"):
            print("ENTER 1, 2, OR 3.")
            continue
        e = int(choice)
        cost = 8 + 5 * e
        if st["food"] >= cost:
            st["food"] -= cost
            # Random addition to mileage based on oxen spending and random factor
            st["distance"] += int((1 - ((TOTAL_TRAIL - st["distance"]) / TOTAL_TRAIL)) *
                                   (8 + (st["oxen_spent"] - 220) / 5 + random.randint(0, 9)))
            break
        else:
            print("YOU CAN'T EAT THAT WELL.")
    return


def encounter_riders():
    """
    Riders ahead: 80% chance they look hostile. Player chooses tactics.
    """
    st = game_state
    print("RIDERS AHEAD.  THEY ", end="")
    hostile = random.random() < 0.8
    if not hostile:
        print("DON'T LOOK HOSTILE.")
    else:
        print("LOOK HOSTILE.")
    print("TACTICS: (1) RUN  (2) ATTACK  (3) CONTINUE  (4) CIRCLE WAGONS")
    while True:
        choice = input()
        if choice not in ("1", "2", "3", "4"):
            print("ENTER 1, 2, 3, OR 4.")
            continue
        t = int(choice)
        break

    if not hostile:
        # Friendly riders scenario
        if t == 1:
            st["distance"] += 15
            st["oxen_spent"] -= 10
            print("THEY DID NOT ATTACK.")
        elif t == 2:
            st["food"] += 15
            st["money"] -= 10
            print("YOU GOT MONEH OR FOOD??")
        elif t == 3:
            st["food"] -= 5
            st["bullets"] -= 100
        else:
            st["food"] -= 20
            print("RIDERS WERE FRIENDLY, BUT CHECK FOR POSSIBLE LOSSES")
        return

    # Hostile riders
    if t == 1:
        # Run: possible to lose time, supplies
        st["distance"] += 20
        st["food"] -= 15
        st["bullets"] -= 150
        st["money"] -= 40
        print("YOU RAN; LOST SUPPLIES.")
    elif t == 2:
        # Attack: do a shoot-out
        shoot_out()
    elif t == 3:
        # Continue: lose supplies but safe?
        st["food"] -= 5
        st["bullets"] -= 100
        print("YOU CONTINUED; LOST FOOD AND BULLETS.")
    else:
        # Circle wagons: try to defend
        st["food"] -= 20
        print("YOU CIRCLED WAGONS; LOST SOME SUPPLIES.")
    return


def shoot_out():
    """
    Subroutine for attacking hostile riders. Uses the timed typing mechanic.
    Simulated here by a random skill check & shooting skill.
    """
    st = game_state
    # Choose a random word
    words = ["BANG", "BLAM", "POW", "WHAM"]
    shot_word = random.choice(words)
    print(f"TYPE {shot_word}")
    start = time.time()
    typed = input()
    elapsed = time.time() - start
    user_time = elapsed * 3600 - (st["shot_skill"] - 1)  # mimic original timing formula
    if typed.strip().upper() == shot_word and user_time > 0:
        # Good shot
        lost_bullets = random.randint(1, 3) * 20 + 80
        st["bullets"] -= lost_bullets
        st["food"] += 15
        st["money"] -= 10
        print("QUICKEST DRAW OUTSIDE OF DODGE CITY!!! YOU GOT 'EM!")
    else:
        # Bad shot: get injured or lose supplies
        print("LOUSY SHOT — YOU GOT KNIFED!")
        st["injury_flag"] = True
        st["money"] -= 20
        st["misc"] -= 5
    return


def wagon_breakdown():
    print("WAGON BREAKS DOWN — LOSE TIME AND SUPPLIES FIXING IT.")
    game_state["distance"] -= 15 + random.randint(0, 5)
    game_state["misc"] -= 8
    return


def ox_injures_leg():
    print("OX INJURES LEG — SLOWS YOU DOWN REST OF TRIP")
    game_state["distance"] -= 25
    game_state["oxen_spent"] -= 20
    return


def daughter_breaks_arm():
    print("BACK LUCK — YOUR DAUGHTER BROKE HER ARM")
    print("YOU HAD TO STOP AND USE SUPPLIES TO MAKE A SLING")
    game_state["distance"] -= 5 + random.randint(0, 4)
    game_state["misc"] -= 2 + random.randint(0, 3)
    return


def ox_wanders_off():
    print("OX WANDERS OFF — SPEND TIME LOOKING FOR IT")
    game_state["distance"] -= 17
    return


def son_gets_lost():
    print("YOUR SON GETS LOST — SPEND HALF THE DAY LOOKING FOR HIM")
    game_state["distance"] -= 10
    return


def unsafe_water():
    print("UNSAFE WATER — LOSE TIME LOOKING FOR CLEAN SPRING")
    game_state["distance"] -= 2 + random.randint(0, 10)
    return


def heavy_rains():
    if game_state["distance"] <= 950:
        print("HEAVY RAINS — TIME AND SUPPLIES LOST")
        game_state["food"] -= 10
        game_state["bullets"] -= 500
        game_state["misc"] -= 15
        game_state["distance"] -= 5 + random.randint(0, 10)
    else:
        # If past the first 950 miles, treat as normal travel
        pass
    return


def bandits_attack():
    print("BANDITS ATTACK!")
    shoot_out()


def wagon_fire():
    print("THERE WAS A FIRE IN YOUR WAGON — FOOD AND SUPPLIES DAMAGED!")
    game_state["food"] -= 40
    game_state["bullets"] -= 400
    game_state["misc"] -= random.randint(3, 10)
    game_state["distance"] -= 15
    return


def lose_way_in_fog():
    print("LOSE YOUR WAY IN HEAVY FOG — TIME IS LOST")
    game_state["distance"] -= 10 + random.randint(0, 5)
    return


def snake_bite():
    print("YOU KILLED A POISONOUS SNAKE AFTER IT BIT YOU")
    game_state["bullets"] -= 10
    game_state["misc"] -= 5
    if game_state["misc"] < 0:
        print("YOU DIE OF SNAKEBITE SINCE YOU HAVE NO MEDICINE")
        game_state["survivors"] = 0
    return


def ford_river_swamped():
    print("WAGON GETS SWAMPED FORDING RIVER — LOSE FOOD AND CLOTHES")
    game_state["food"] -= 30
    game_state["clothing"] -= 20
    game_state["distance"] -= 20 + random.randint(0, 20)
    return


def wild_animals_attack():
    print("WILD ANIMALS ATTACK!")
    if game_state["bullets"] > 39:
        b1 = random.randint(1, 4)
        if b1 <= 2:
            print("NICE SHOOTIN' PARTNER — THEY DIDN'T GET MUCH")
            game_state["bullets"] -= 20 * b1
            game_state["clothing"] -= 4 * b1
            game_state["food"] -= 8 * b1
        else:
            print("SLOW ON THE DRAW — THEY GOT AT YOUR FOOD AND CLOTHES")
            game_state["bullets"] -= 20 * b1
            game_state["clothing"] -= 4 * b1
            game_state["food"] -= 8 * b1
    else:
        print("YOU WERE TOO LOW ON BULLETS — THE WOLVES OVERPOWERED YOU")
        game_state["injury_flag"] = True
    return


def cold_weather():
    print("COLD WEATHER — BRRRRRRR! YOU ", end="")
    threshold = 22 + 4 * random.random()
    if game_state["clothing"] > threshold:
        print("HAVE ENOUGH CLOTHING TO KEEP YOU WARM.")
    else:
        print("DON'T HAVE ENOUGH CLOTHING TO KEEP YOU WARM.")
        game_state["injury_flag"] = True
    return


def hail_storm():
    print("HAIL STORM — SUPPLIES DAMAGED")
    game_state["misc"] -= random.randint(0, 10) + 4
    game_state["bullets"] -= 200
    game_state["food"] -= 5
    return


def friendly_indians():
    print("HELPFUL INDIANS SHOW YOU WHERE TO FIND MORE FOOD")
    game_state["food"] += 14
    return


def check_mountains():
    """
    If distance > 950: mountain events. Blizzard chance, travel slowdowns.
    """
    st = game_state
    if st["distance"] <= 950:
        return False  # not in mountains yet

    # 10% chance of rough mountains event
    if random.random() * 10 > (9 - (((st["distance"] / 100) - 15) ** 2 + 72) /
                             (((st["distance"] / 100) - 15) ** 2 + 12)):
        print("RUGGED MOUNTAINS")
        if random.random() < 0.1:
            print("YOU GOT LOST — LOSE VALUABLE TIME TRYING TO FIND TRAIL!")
            st["distance"] -= 60
        elif random.random() < 0.11:
            print("WAGON DAMAGED! — LOSE TIME AND SUPPLIES")
            st["misc"] -= 5
            st["bullets"] -= 200
            st["distance"] -= 20 + 30 * random.random()
        else:
            print("THE GOING GETS SLOW")
            st["distance"] -= 45 + random.random() / 0.02

        # First time through South Pass (distance < 1700)
        if not st["south_pass_flag"] and st["distance"] >= 1700:
            if random.random() < 0.8:
                print("YOU MADE IT SAFELY THROUGH SOUTH PASS — NO SNOW")
            else:
                print("BLIZZARD IN SOUTH PASS — TIME AND SUPPLIES LOST")
                st["blizzard_flag"] = True
                st["food"] -= 25
                st["misc"] -= 10
                st["bullets"] -= 300
                st["distance"] -= 30 + 40 * random.random()
                if st["clothing"] < 18 + 2 * random.random():
                    print("YOU DIED IN BLIZZARD — NOT ENOUGH CLOTHING")
                    st["survivors"] = 0
            st["south_pass_flag"] = True

    return True


def random_event():
    """
    Choose one of 16 possible events, weighted by thresholds from the BASIC DATA:
    DATA 6,11,13,15,17,22,32,35,37,42,44,54,64,69,95
    """
    thresholds = [6, 11, 13, 15, 17, 22, 32, 35, 37, 42, 44, 54, 64, 69, 95]
    r = random.randint(1, 100)
    idx = 0
    while idx < len(thresholds) and r > thresholds[idx]:
        idx += 1

    # Map idx (0-based) to a function
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

    if idx < len(event_funcs):
        event_funcs[idx]()


def check_illness():
    """
    Each turn, there is a chance of illness based on how well they ate (E).
    10 + 35*(E-1)
    Then a chance of bad illness if not enough medicine.
    """
    st = game_state
    # If already flagged for blizzard or injury, skip
    if st["blizzard_flag"] or st["injury_flag"]:
        return

    # 35% chance of wild illness for each level E (poor/moderate/well)
    e_level = 2  # default moderate: we don't store E explicitly, assume moderate
    chance_wild = 10 + 35 * (e_level - 1)
    if random.randint(1, 100) < chance_wild:
        print("WILD ILLNESS — MEDICINE USED")
        st["distance"] -= 5
        st["misc"] -= 2
    else:
        chance_bad = 100 - (40 / (4 ** (e_level - 1)))
        if random.randint(1, 100) < chance_bad:
            print("BAD ILLNESS — MEDICINE USED")
            st["distance"] -= 5
            st["misc"] -= 5
        else:
            # No illness
            return

    if st["misc"] < 0:
        print("YOU RAN OUT OF MEDICAL SUPPLIES — YOU DIED OF ILLNESS")
        st["survivors"] = 0
    return


def check_end_conditions():
    """
    Check if the player has finished the trail or died.
    """
    st = game_state
    # Starvation
    if st["food"] <= 0:
        print("\nYOU RAN OUT OF FOOD AND STARVED TO DEATH.")
        st["survivors"] = 0
    # If distance ≥ 2040, they've arrived
    if st["distance"] >= TOTAL_TRAIL:
        # Final two-week stretch fraction
        fraction = (TOTAL_TRAIL - st["prev_distance"]) / (st["distance"] - st["prev_distance"])
        st["final_fraction"] = fraction
        print("\nYOU FINALLY ARRIVED AT OREGON CITY — AFTER 2040 LONG MILES! HOORAY!")
        # Compute arrival day of week
        total_turns = st["days_on_trail"] * 14 * 7  # approximating days
        days_passed = int(total_turns / 7)
        day_of_week = (st["days_on_trail"] * 7 + int(fraction * 7)) % 7
        dow_str = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"][day_of_week]
        # Calculate arrival date in 1847
        turned_weeks = (st["days_on_trail"] - 1) * 2  # each turn is 2 weeks
        day_offset = int(fraction * 14) + 29  # starting March 29
        # Simplify: just print year and hope it's roughly correct
        print(f"{dow_str} July {int(fraction * 14 + 1)} 1847")
        print("\nPRESIDENT JAMES K. POLK SENDS YOU HIS HEARTIEST CONGRATULATIONS")
        print("AND WISHES YOU A PROSPEROUS LIFE AHEAD AT YOUR NEW HOME\n")
        st["survivors"] = 0  # End game
    return


def main():
    print("\n=== OREGON TRAIL ===\n")
    need_instr = input("DO YOU NEED INSTRUCTIONS (YES/NO)? ").strip().upper()
    if need_instr == "YES":
        print_instructions()

    game_state["shot_skill"] = get_shooting_skill()
    initial_purchases()

    # Main game loop
    while game_state["survivors"] > 0 and game_state["distance"] < TOTAL_TRAIL:
        # Beginning of each turn
        game_state["prev_distance"] = game_state["distance"]
        game_state["days_on_trail"] += 0  # keep track for dates

        # Print date
        date_str = current_date_str()
        if date_str:
            print(f"MONDAY {date_str}")
        else:
            print("\nYOU HAVE BEEN ON THE TRAIL TOO LONG — YOUR FAMILY DIES IN THE FIRST BLIZZARD OF WINTER.")
            break

        # Display status
        display_status()

        # Check supplies, prompt to hunt or buy food
        if game_state["food"] < 13:
            print("YOU'D BETTER DO SOME HUNTING OR BUY FOOD SOON!!!!")

        # Ask action
        action = prompt_action()
        print()

        # Execute action
        if action == "fort":
            # Buying supplies at fort
            if game_state["money"] >= 50:
                game_state["food"] += 20
                game_state["money"] -= 50
                print("YOU BOUGHT SUPPLIES AT THE FORT!")
            else:
                print("NOT ENOUGH MONEY TO BUY SUPPLIES AT THE FORT.")
        elif action == "hunt":
            hunt()
        elif action == "continue":
            eat_and_travel()

        # Eating phase if enough food
        if game_state["food"] >= 13:
            eat_meal()

        # Random events (only if they've traveled > 0)
        if game_state["distance"] > 0:
            game_state["event_counter"] += 1
            if game_state["event_counter"] >= 1:
                random_event()
                game_state["event_counter"] = 0

        # Mountain logic
        if check_mountains():
            pass

        # Illness check
        check_illness()

        # Check end conditions
        check_end_conditions()

        # If survivors is 0, break
        if game_state["survivors"] <= 0:
            break

        print("\n-----------------------------\n")

    # Game over prompts (if died)
    if game_state["survivors"] <= 0 and game_state["distance"] < TOTAL_TRAIL:
        print("\nDUE TO YOUR UNFORTUNATE SITUATION, THERE ARE A FEW FORMALITIES WE MUST GO THROUGH\n")
        next_of_kin = input("WOULD YOU LIKE US TO INFORM YOUR NEXT OF KIN? (YES/NO)? ").strip().upper()
        if next_of_kin == "YES":
            print("THAT WILL BE $4.50 FOR THE TELEGRAPH CHARGE.")
        print("\nWE THANK YOU FOR THIS INFORMATION AND WE ARE SORRY YOU DIDN'T MAKE IT TO THE GREAT TERRITORY OF OREGON\n")
        print("BETTER LUCK NEXT TIME\n")
        print("           SINCERELY")
        print("       THE OREGON CITY CHAMBER OF COMMERCE\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
        sys.exit(0)
