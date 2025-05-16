from flask import Flask, render_template, request, session, redirect, url_for

import sqlite3
import os

currGame = []
currPath = []

def getCurrGame():
    # print("In other py file returning this: " + str(currGame))
    return currGame

def getCurrPath():
    # print("In other py file returning this: " + str(currPath))
    return currPath

def addEvent(input):
    currGame.append(input)
    return currGame

def changePath(start, end):
    currPath[0] = start
    currPath[1] = end
    return currPath

def saveWork():
    return 0

def reset():
    currGame.clear()
    # print("Here: " + currGame)
