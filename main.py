import os
import time
import random
import csv
from functions import body_text, action_csv, clear_screen


### TODO: Typewriter-like animation for passwords showing up on screen



def play(name):
    
    timing = float(input("Enter speed (1-10): "))/10
    iteration = 1
    #Up_text = f"----------- Welcome, {name} -----------\nLoading{iteration * '.'}\n---------------------{len(name)*'-'}------------"
    #Low_Text = f"---------------------{len(name)*'-'}------------"
    
    if not name:
        print("You must enter a name!")
        return TypeError
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
        space = f"Hello, Ainslie\nWong"
        #Select Password Option:\n1. {pass_opt[0]['pass']}\n2. {pass_opt[1]['pass']}\n3. {pass_opt[2]['pass']} 
        body_text(name, space, 3)
        
        try:

            pass_select = int(input("Enter Choice (#): ")) - 1
            action_csv(pass_opt[pass_select]['pass'],name, "user_pass.csv","set")

        except:
            return TypeError
        
        print(pass_opt)

            


        
play(input("Enter Name: "))

