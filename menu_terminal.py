#!/usr/bin/env python3
"""IDeK shared helpers — original command-line version (restored from pre-GUI version).

Used by main_terminal.py and market_terminal.py.
"""
import random
import os
import time
import csv
import sys
import tty
import termios
from functions_terminal import body_text, clear_screen
#from main_terminal import timing

def view_menu(name,balance=500,networth=500):
    clear_screen()
    space = f"Current Networth: {networth} | Current Account Balance: {balance}\nEnter A Number To Open One Of The Menus Below:\n1. Market\n2. Inventory\n3. Achievements\n4. Leaderboard"
    body_text(name,space,2)
    #try:
    choice = int(input(f"Navigate To: "))
    if choice <= 4 and choice >= 1:
        navigation_menu(name,choice,balance,networth)
    else: 
        print("Input out of range!")
    #except:
    #    print("Invalid Input")

    


def navigation_menu(name,choice,balance,networth):
    if choice == 1:
        space = f"Market:\nxyz\nzxy\nyxz"
        body_text(name,space,2)

    elif choice == 2:
        space = f""
    elif choice == 3:
        pass
    elif choice == 4:
        open_leaderboard(name,balance,networth)

def open_market(name,balance,networth):
    pass

def open_inventory(name,balance,networth):
    pass

def open_achievements(name,balance,networth):
    pass

def open_leaderboard(name,balance,networth):
    data = []
    leaderboard = []
    filename = "user_wallets.csv"
    with open(filename, mode="r", newline="", encoding="utf-8") as f:
        
        data_list = list(csv.DictReader(f))

        total_rows = len(data_list)
        integer = -1
        for row in data_list:
           
            temp_usr = []
            temp_usr.append(row["username"])
            temp_usr.append(row["cash"])
            #print(temp_usr)
            #leaderboard.append(temp_usr)
            #print(leaderboard, "elade")
            
            #if integer == 0:
            #    temp_usr_compare = leaderboard[integer]
            #    leaderboard.append(temp_usr)
            
            #for entry in range(0,total_rows):
            print("in for")
            #temp_usr_compare = leaderboard[integer]
            
            if len(leaderboard) == 0:
                print(len(leaderboard), "leaderboard length")
                leaderboard.append(temp_usr)
                print(f"Here is current LB: {leaderboard}, integer: {integer} 1")



            elif len(leaderboard) > 0:
                print(f"Here is current LB: {leaderboard}, integer: {integer} 2")

                temp_usr_compare = leaderboard[integer - 1]
                print(f"Here is current temp_usr_compare: {temp_usr_compare}")
                if temp_usr[1] >= temp_usr_compare[1]:
                    #print("in if", leaderboard)
                    leaderboard.insert(0,temp_usr)
                    print(f"added {temp_usr} as greater value compared to {temp_usr_compare}")
                else:
                    not_in = 0
                    for i in range(0,len(leaderboard)):
                        print(not_in, len(leaderboard))

                        temp_user_compares = leaderboard[i]

                        if temp_usr[1] >= temp_user_compares[1]:
                    #print("in elif", leaderboard)
                            leaderboard.insert(i, temp_usr)
                            print(f"added {temp_usr} as greater value compared to {temp_usr_compare}")

                            not_in = not_in + 1

                        elif not_in == len(leaderboard):
                            leaderboard.append(temp_usr)
                            print(f"added {temp_usr} as lesser value compared to {temp_usr_compare}")
                        

            integer = integer + 1

            #except:
             #   print("error")
                

            #leaderboard.append(temp_usr)

        print(leaderboard)
            


    


view_menu("Test User", 1000, 1500)

