#!/usr/bin/env python3
"""IDeK — original command-line entry point (restored from pre-GUI version).

Run:  python3 main_terminal.py

Uses functions_terminal.py (not the browser/Tkinter modules).
"""
import os
import time
import random
import csv
from functions_terminal import body_text, action_csv, clear_screen, mask_input, login_check, call_password_select
from menu_terminal import view_menu

def play(name):
    global timing
    timing = float(input("Enter speed (1-10): "))/10
    iteration = 1
    #Up_text = f"----------- Welcome, {name} -----------\nLoading{iteration * '.'}\n---------------------{len(name)*'-'}------------"
    #Low_Text = f"---------------------{len(name)*'-'}------------"
    
    name_check = action_csv(1,name,"user_pass.csv","check")
    stage, name = login_check(name,name_check,timing)

    try:
        while stage != "Logged-In":
            stage, name = login_check(name,name_check,timing)


        if stage != "Logged-In" and stage != "Not-Logged-In":
            pass_opt = call_password_select(name)
            
            pass_select = int(input("Enter Choice (#): ")) - 1
            while pass_select > 2 or pass_select < 0:
                pass_select = int(input("Please Re-Enter Your Choice (#): ")) - 1
            action_csv(pass_opt[pass_select]['pass'],name, "user_pass.csv","set", pass_opt[pass_select]['id'],"username","pass_id","pass")
            print(f">> You must remember your username and password: {name}, {pass_opt[pass_select]['pass']}!")
            next = input(f"Press \033[1mEnter\033[0m To Continue! ")

            if next == "":
                stage = "Logged-In"

    except:
        return TypeError
    
    
    try:
        if stage == "Logged-In":
            print("logged in, checked via conditional.")
            body_text(name,"",4,timing)
            view_menu(name)
        else:
            print("Incorrect password provided!")
    except:
        print("You are not logged-in!\nPlease restart the proccess!")
play(input("Enter Username: "))

