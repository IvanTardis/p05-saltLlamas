import sqlite3
import random

# Database Initialization
def build():
    database = sqlite3.connect("rest.db")
    c = database.cursor()

    # Create users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        password TEXT,
        highScore INTEGER DEFAULT 0,
        pfp TEXT,
        userID INTEGER PRIMARY KEY AUTOINCREMENT
        backgroundImagePath TEXT
        midgroundImageOnePath TEXT
        midgroundImageTwoPath TEXT
        wagonImagePath TEXT
    )
    """)

    # Create game stats table
    c.execute("""
    CREATE TABLE IF NOT EXISTS stats(
        distanceTraveled INTEGER DEFAULT 0,
        daysPassed INTEGER DEFAULT 0,
        survivingPeople INTEGER DEFAULT 5,
        foodQuantity INTEGER DEFAULT 100,
        money INTEGER DEFAULT 700,
        oxen INTEGER DEFAULT 2,
        bullets INTEGER DEFAULT 50,
        mileage INTEGER DEFAULT 0,
        event_counter INTEGER DEFAULT 0,
        injury BOOLEAN DEFAULT 0,
        illness BOOLEAN DEFAULT 0,
        blizzard BOOLEAN DEFAULT 0,
        fort_flag BOOLEAN DEFAULT 0,
        south_pass_flag BOOLEAN DEFAULT 0,
        userID INTEGER,
        FOREIGN KEY (userID) REFERENCES users(userID)
    )
    """)

    # Migration for existing databases
    try:
        c.execute("ALTER TABLE stats ADD COLUMN mileage INTEGER DEFAULT 0")
        c.execute("ALTER TABLE stats ADD COLUMN event_counter INTEGER DEFAULT 0")
        c.execute("ALTER TABLE stats ADD COLUMN injury BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE stats ADD COLUMN illness BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE stats ADD COLUMN blizzard BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE stats ADD COLUMN fort_flag BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE stats ADD COLUMN south_pass_flag BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        # Columns already exist, ignore the error
        pass

    database.commit()
    database.close()

# Database Connection
def connect():
    db = sqlite3.connect("rest.db")
    c = db.cursor()
    return c, db

def close(db):
    db.commit()
    db.close()

# AUTHENTICATION FUNCTIONS
def auth(username, password):
    """
    Authenticate user credentials.
    """
    c, db = connect()
    user = c.execute("SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password,)).fetchone()
    close(db)
    return user

def createUser(username, password):
    """
    Register a new user if username is not taken.
    """
    c, db = connect()
    existing_user = c.execute("SELECT * FROM users WHERE username = ?",
        (username,)).fetchone()
    if not existing_user:
        c.execute("""
        INSERT INTO users(username, password, highScore, pfp)
        VALUES(?, ?, ?, ?)
        """, (username, password, 0, "default.png"))

        user_id = c.lastrowid

        # Initialize game state for the user
        c.execute("""
        INSERT INTO stats(userID) VALUES(?)
        """, (user_id,))

        db.commit()
        close(db)
        return True
    close(db)
    return False

def getHighScore(user_id):
    """
    Retrieve the high score of the user.
    """
    c, db = connect()
    high_score = c.execute("SELECT highScore FROM users WHERE userID = ?",
        (user_id,)).fetchone()
    close(db)
    return high_score[0] if high_score else 0

def createBackgroundImage(path):
    """Create background image path for a user"""
    c, db = connect()
    c.execute("""
        INSERT INTO users(backgroundImagePath)
        VALUES(?)""",
        (path))
    db.commit()
    close(db)

def createMidgroundImageOne(path):
    """Create midground image one path for a user"""
    c, db = connect()
    c.execute("""
        INSERT INTO users(midgroundImageOnePath)
        VALUES(?)""",
        (path))
    db.commit()
    close(db)

def createMidgroundImageTwo(path):
    """Create midground image two path for a user"""
    c, db = connect()
    c.execute("""
        INSERT INTO users(midgroundImageTwoPath)
        VALUES(?)""",
        (path))
    db.commit()
    close(db)

def createWagonImage(path):
    """Create wagon image path for a user"""
    c, db = connect()
    c.execute("""
        INSERT INTO users(wagonImagePath)
        VALUES(?)""",
        (path))
    db.commit()
    close(db)

def getBackgroundImagePath(user_id):
    """
    Retrieve the user's backgroundImagePath
    """
    c, db = connect()
    background_image_path = c.execute("SELECT backgroundImagePath FROM users WHERE userID = ?",
        (user_id,)).fetchone()
    close(db)
    return background_image_path[0] if background_image_path else 0

def getMidgroundImageOnePath(user_id):
    """
    Retrieve the user's First MidgroundImagePath
    """
    c, db = connect()
    midground_image_one_path = c.execute("SELECT midgroundImageOnePath FROM users WHERE userID = ?",
        (user_id,)).fetchone()
    close(db)
    return midground_image_one_path[0] if midground_image_one_path else 0

def getMidgroundImageTwoPath(user_id):
    """
    Retrieve the user's Second MidgroundImagePath
    """
    c, db = connect()
    midground_image_one_path = c.execute("SELECT midgroundImageTwoPath FROM users WHERE userID = ?",
        (user_id,)).fetchone()
    close(db)
    return midground_image_two_path[0] if midground_image_two_path else 0

def getWagonImagePath(user_id):
    """
    Retrieve the user's wagonImagePath
    """
    c, db = connect()
    wagon_image_path = c.execute("SELECT wagonImagePath FROM users WHERE userID = ?",
        (user_id,)).fetchone()
    close(db)
    return wagon_image_path[0] if wagon_image_path else 0

db = sqlite3.connect("rest.db")
c = db.cursor()

print("== Users Table ==")
c.execute("PRAGMA table_info(users)")
print(c.fetchall())

print("\n== Stats Table ==")
c.execute("PRAGMA table_info(stats)")
print(c.fetchall())

db.close()
