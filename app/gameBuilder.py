from flask import Flask, render_template, request, session, redirect, url_for

import sqlite3
import os

baseGame = {
    "currPath": [None] * 2,
    "playableCharacters": "",
    "storeItems": {
        "food": {

        },
        "utility": {

        }
    },
    "monuments": {

    }
}

currGame = baseGame.copy()

currEvents = []
currPath = [None] * 2

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

def changePath(start, end):
    print("Changing path")
    currGame["currPath"] = [start, end]
    return currGame.get("currPath")

def saveWork():
    return 0

def reset():
    currEvents.clear()
    # print("Here: " + currEvents)
