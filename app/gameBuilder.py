from flask import Flask, render_template, request, session, redirect, url_for

import sqlite3
import os

currGame = []

def getCurrGame():
    return currGame

def addEvent(input):
    currGame.append(input)
    return currGame

def saveWork():
    return 0

def reset():
    clear(currGame)
    print("Here: " + currGame)
