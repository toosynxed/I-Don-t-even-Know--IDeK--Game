import os
import time
import random
import csv
from functions import body_text, action_csv, clear_screen, mask_input





def play(name):
    
    timing = float(input("Enter speed (1-10): "))/10
    iteration = 1
    #Up_text = f"----------- Welcome, {name} -----------\nLoading{iteration * '.'}\n---------------------{len(name)*'-'}------------"
    #Low_Text = f"---------------------{len(name)*'-'}------------"
    
    name_check = action_csv(1,name,"user_pass.csv","check")
    
    


    if not name:
        print("You must enter a name!")
        return TypeError
    elif name_check == 1:
        #Needs to do the enter password to "Login" method/check 
        space = f"\033[0mPlease enter your password!\nRemember, your password is \033[3mCase-Sensitive\033[0m!"
        basic_details = action_csv(1,name,"user_pass.csv","get")
        name = basic_details["username"]
        body_text(name,space,3)
        password_input = mask_input()
        if password_input == basic_details["pass"]:

            stage = "Logged-In"

    else:
        #body_text(name, f"Loading{iteration * '.'}", 4, timing)
        iteration = 1
        for i in range(0,15):
            space = f"Loading{iteration * '.'}"
            iteration = iteration + 1
            time.sleep(timing)
            if iteration > 3:
                iteration = 0

            clear_screen()
            body_text(name, space, 2)
        for i in range(0,4):
            clear_screen()
            if i % 2 == 0:
                space = "Loaded"
                body_text(name, space, 2)
                time.sleep(1)
            else:
                
                space = ''
                body_text(name, space, 2)
                time.sleep(1)
        time.sleep(1)
        clear_screen()

        pass_opt = action_csv(1,name,"pass_list.csv","pass")
        space = f"Select Password Option:\n1. {pass_opt[0]['pass']}\n2. {pass_opt[1]['pass']}\n3. {pass_opt[2]['pass']}"
        #Select Password Option:\n1. {pass_opt[0]['pass']}\n2. {pass_opt[1]['pass']}\n3. {pass_opt[2]['pass']} 
        body_text(name, space, 3)
        
        try:

            pass_select = int(input("Enter Choice (#): ")) - 1
            while pass_select > 2 or pass_select < 0:
                pass_select = int(input("Please Re-Enter Your Choice (#): ")) - 1
            action_csv(pass_opt[pass_select]['pass'],name, "user_pass.csv","set", pass_opt[pass_select]['id'])
            print(f">> You must remember your username and password: {name}, {pass_opt[pass_select]['pass']}!")
            next = input(f"Press \033[1mEnter\033[0m To Continue! ")
            if next == "":
                stage = "Logged-In"

        except:
            return TypeError
        
        print(pass_opt)
    try:
        if stage == "Logged-In":
            print("logged in, checked via conditional.")
    except:
        print("You are not logged-in!\nPlease restart the proccess!")
        


        
play(input("Enter Username: "))

