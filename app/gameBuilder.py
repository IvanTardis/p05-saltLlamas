from flask import Flask, render_template, request, session, redirect, url_for

import sqlite3
import os

currGame = []

def getCurrGame():
    print("In other py file returning this: " + str(currGame))
    return currGame

def addEvent(input):
    currGame.append(input)
    return currGame

def saveWork():
    return 0

def reset():
    clear(currGame)
    print("Here: " + currGame)
