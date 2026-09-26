#!/usr/bin/env python3
"""IDeK — original command-line entry point (restored from pre-GUI version).

Run:  python3 main_terminal.py

Uses functions_terminal.py (not the browser/Tkinter modules).
"""
import os
import sys
import shutil
import time
import random
import csv

DATA_HEADERS = {
    "user_pass.csv": ["username", "pass_id", "pass"],
    "user_wallets.csv": ["username", "cash"],
    "user_holdings.csv": ["username", "risk_id", "cost", "quantity"],
    "user_inventories.csv": ["username", "bit_inv", "None"],
    "user_ach.csv": ["username", "bit_inv_ach", "bit_inv_read"],
}


def prepare_data_files():
    # Save files live next to the executable, not in the temp folder PyInstaller unpacks into.
    if getattr(sys, "frozen", False):
        app_dir = os.path.dirname(sys.executable)
        bundle_dir = getattr(sys, "_MEIPASS", app_dir)
    else:
        app_dir = bundle_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

    if not os.path.exists("pass_list.csv"):
        shutil.copy(os.path.join(bundle_dir, "pass_list.csv"), "pass_list.csv")
    for filename, headers in DATA_HEADERS.items():
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            with open(filename, mode="w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(headers)


prepare_data_files()

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
        while stage == "Not-Logged-In":
            print("Incorrect password, please try again!")
            stage, name = login_check(name,name_check,timing)


        if stage == "New-User":
            pass_opt = call_password_select(name)
            
            pass_select = int(input("Enter Choice (#): ")) - 1
            while pass_select > 2 or pass_select < 0:
                pass_select = int(input("Please Re-Enter Your Choice (#): ")) - 1
            action_csv(pass_opt[pass_select]['pass'],name, "user_pass.csv","set", pass_opt[pass_select]['id'],"pass_id","pass")
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
username = input("Enter Username: ").strip()
while not username:
    username = input("You must enter a name! Enter Username: ").strip()
play(username)

