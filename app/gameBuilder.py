from flask import Flask, render_template, request, session, redirect, url_for

import sqlite3
import os

baseGame = {
    "startDate": 0,
    "currPath": [None] * 2,
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
    "monuments": {

    },
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

currEvents = []
currImages = [None]*4
# currPath = [None] * 2

def addBack(input):
    currImages[0] = input

def addMidOne(input):
    currImages[1] = input

def addMidTwo(input):
    currImages[2] = input

def addFore(input):
    currImages[3] = input

def addMonument(name, type):
    temp = baseMonument.copy()
    temp['type'] = type
    currGame["monuments"][name] = temp

def getMonuments():
    return currGame.get("monuments")

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

def saveWork():
    return 0

def reset():
    currEvents.clear()
    # print("Here: " + currEvents)
