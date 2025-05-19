from flask import Flask, render_template, request, session, redirect, url_for

import sqlite3
import os

currEvents = []
currPath = [None] * 2

def getCurrEvents():
    # print("In other py file returning this: " + str(currEvents))
    return currEvents

def getCurrPath():
    # print("In other py file returning this: " + str(currPath))
    return currPath

def getStartPt():
    return currPath[0]

def getEndPt():
    return currPath[1]

def addEvent(input):
    currEvents.append(input)
    return currEvents

def changePath(start, end):
    print("Changing path")
    currPath[0] = start
    currPath[1] = end
    return currPath

def saveWork():
    return 0

def reset():
    currEvents.clear()
    # print("Here: " + currEvents)
