from flask import Flask, render_template, request, session, redirect, url_for
from database import *

import sqlite3
import os

baseGame = {
    "title": "",
    "startDate": 0,
    "currPath": [None] * 2,
    "distance": 0,
    "playableCharacters": {
        "name": {
            "health": 0,
            "money": 0,
            "bonusStat": 1,
        },
    },
    "storeItems": {
        "food": {
            "base": {
                "weight": 0,
                "price": 0
            }
        },
        "utility": {
            "bullets": {
                "weight": 0,
                "price": 0
            }
        },
        "transportation": {
            "ox": {
                "speed": 0,
                "health": 0
            }
        }
    },
    "obstacle": "",
    "weather": "",
    "prey": ""
}

currGame = baseGame.copy()
baseCharacter = {
    "description": "",
    "health": 0,
    "money": 0,
    "bonusStat": 0
}

baseMonument = {
    "type": "",
}

# danger, search, shop

currTitle = ""
currEvents = []
currImages = [None]*4
# currPath = [None] * 2

def getTitle():
    return currGame.get('title')

def changeTitle(input):
    print("\n\n\nChanging Title\n\n\n")
    currGame['title'] = input
    return input

def getDistance():
    return currGame.get("distance")

def changeDistance(input):
    currGame['distance'] = input
    return input

def addBack(input):
    currImages[0] = input

def addMidOne(input):
    currImages[1] = input

def addMidTwo(input):
    currImages[2] = input

def addFore(input):
    currImages[3] = input

def changeObstacle(name):
    currGame['obstacle'] = name

def getObstacle():
    return currGame.get("obstacle")

def addCharacter(name, description, health, money, bonus):
    temp = baseCharacter.copy()
    temp["description"] = description
    temp["health"] = health
    temp["money"] = money
    temp["bonusStat"] = bonus
    currGame["playableCharacters"][name] = temp

def getCharacters():
    return currGame.get("playableCharacters")

def getCurrEvents():
    # print("In other py file returning this: " + str(currEvents))
    return currEvents

def getCurrPath():
    # print("In other py file returning this: " + str(currPath))
    return currGame.get("currPath")

def getStartPt():
    return currGame.get("currPath")[0]

def getEndPt():
    return currGame.get("currPath")[1]

def addEvent(input):
    currEvents.append(input)
    return currEvents

def changeStartDate(input):
    currGame["startDate"] = input
    return currGame["startDate"]

def getStartDate():
    return currGame["startDate"]

def changePath(start, end):
    print("Changing path to: " + start + end)
    currGame["currPath"] = [start, end]
    return currGame.get("currPath")

def getGame():
    return currGame

def saveWork(usrname):
    print("\n\n\nSAVING HERE\n\n\n\n")
    save_user_game(usrname, currGame.get('title'), currGame)
    currGame.clear()


def reset():
    currGame.clear()
    # print("Here: " + currEvents)
