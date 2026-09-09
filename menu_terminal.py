#!/usr/bin/env python3
"""IDeK shared helpers — original command-line version (restored from pre-GUI version).
https://youtu.be/RDFGkBE2O50?si=yXnJloCW18_o94bB - Inspiration for "Shell Searching"

Used by main_terminal.py and market_terminal.py.
"""
import random
import os
import time
import csv
import sys
import tty
import termios
from functions_terminal import body_text, clear_screen, action_csv
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
    if choice == 1: # Market
        space = f"Market:\nxyz\nzxy\nyxz"
        body_text(name,space,2)

    elif choice == 2: # Inventory
        space = f""
        open_inventory(name,balance,networth)
    elif choice == 3: # Achievements
        pass
    elif choice == 4: # Leaderboard
        open_leaderboard(name,balance,networth)

def open_market(name,balance,networth):
    pass

def open_inventory(name,balance,networth):

    action_csv(name,name,"user_inventories.csv","set","username","bit_inv","")
    print("hi")
    # Use Bitwise!
    #if  & 5:

def open_achievements(name,balance,networth):
    pass

def open_leaderboard(name,balance,networth):
    #data = []           NOTE: REMOVE
    leaderboard = []
    filename = "user_wallets.csv"
    with open(filename, mode="r", newline="", encoding="utf-8") as f:
        
        data_list = list(csv.DictReader(f))

        #total_rows = len(data_list)           NOTE: REMOVE
        #integer = -1           NOTE: REMOVE
        
        for row in data_list:
           
            temp_usr = []
            temp_usr.append(row["username"])
            temp_usr.append(float(row["cash"]))
            leaderboard.append(temp_usr)

            """
            #print(leaderboard, "elade")
            
            #if integer == 0:
            #    temp_usr_compare = leaderboard[integer]
            #    leaderboard.append(temp_usr)
            
            #for entry in range(0,total_rows):
            #print("in for")           NOTE: REMOVE
            #temp_usr_compare = leaderboard[integer]
            
            if len(leaderboard) == 0:
                #print(len(leaderboard), "leaderboard length")           NOTE: REMOVE
                leaderboard.append(temp_usr)
                #print(f"Here is current LB: {leaderboard}, integer: {integer} 1")           NOTE: REMOVE



            elif len(leaderboard) > 0:
                #print(f"Here is current LB: {leaderboard}, integer: {integer} 2")           NOTE: REMOVE

                #temp_usr_compare = leaderboard[integer - 1]           NOTE: REMOVE
                #print(f"Here is current temp_usr_compare: {temp_usr_compare}")
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
                            #print(f"added {temp_usr} as greater value compared to {temp_usr_compare}")

                            not_in = not_in + 1

                        elif not_in == len(leaderboard):
                            leaderboard.append(temp_usr)
                            #print(f"added {temp_usr} as lesser value compared to {temp_usr_compare}")
                        

            #integer = integer + 1           NOTE: REMOVE

            #except:
             #   print("error")
                

            #leaderboard.append(temp_usr)

        print(leaderboard)
        """

        leaderboard = shell_sort_nested(leaderboard)
        space = f"Cash Leaderboard:"
        place = 1
        for row in leaderboard:
            cash = f"{round(row[1],2):.2f}"
            cash_deci = list(str(cash))
            cash_deci = cash_deci[-3:]
            user_row = f'\n{place}. {row[0]} - ${format_numbers_2(cash[:-3])}{"".join(cash_deci)}'
            space = f"{space}{user_row}"
            place = place + 1
        body_text(name,space,2)


def format_numbers_2(orig):
    string = str(orig)
    split_curr = list(string)
    split_check = list(string)

    while len(split_curr) > 3:
        split_curr = split_curr[:-3]
        split_check.insert(len(split_curr),",")

    return "".join(split_check)


def shell_sort_nested(arr):
    n = len(arr)
    gap = n // 2

    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            
            # Key Change: Compare index 1 of the sub-arrays instead of the whole array
            while j >= gap and arr[j - gap][1] > temp[1]:
                arr[j] = arr[j - gap]
                j -= gap
                
            arr[j] = temp
            
        gap //= 2
    arr.reverse()
    return arr[:5]


# Example Usage
""""
if __name__ == "__main__":
    data = [54, 26, 93, 17, 77, 31, 44, 55, 20]
    print("Original array:", data)
    
    sorted_data = shell_sort(data)
    print("Sorted array:  ", sorted_data)

"""    

view_menu("Test User", 1000, 1500)

