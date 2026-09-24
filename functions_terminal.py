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
#from main_terminal import timing


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
def crash():
    time.sleep(5)
    #os.system("shutdown /s /t 0" if os.name == 'nt' else "sudo shutdown now")

def body_text(name, space, type,timing=0.5):
    temp_space = ''
    Up_text = f"----------- Welcome, {name} -----------\n{space}\n---------------------{len(name)*'-'}------------"
    try:
        if type == 1: #value
            return Up_text
        elif type == 2: #print
            print(Up_text)

        elif type == 3: #typewriter effect
            writing_length = len(space)
            for i in range(0,writing_length):
                temp_space = ''
                for x in range(0,(i+1)):
                    temp_space = f"{temp_space}{space[x]}"
                #time.sleep(0.1)
                Up_text = f"----------- Welcome, {name} -----------\n{temp_space}\n---------------------{len(name)*'-'}------------"

                print(Up_text)
                time.sleep(timing)
                clear_screen()
        elif type == 4:
            iteration = 1
            for i in range(0,15):
                temp_space = f"Please Wait While We Load Your Profile{iteration * '.'}"
                Up_text = f"----------- Welcome, {name} -----------\n{temp_space}\n---------------------{len(name)*'-'}------------"

                
                if iteration > 3:
                    iteration = 0
                else:
                    iteration = iteration + 1
                    time.sleep(timing)

                clear_screen()
                print(Up_text)
            for i in range(0,4):
                clear_screen()
                if i % 2 == 0:
                    space = "Loaded"
                    print(Up_text)
                    time.sleep(1)
                else:
                    
                    space = ''
                    print(Up_text)
                    time.sleep(1)
        elif type == 5:
            
            Up_text = f"----------- Welcome, {name} -----------\n{temp_space}\n---------------------{len(name)*'-'}------------"

            print(Up_text)
    except:
        print("Type not valid")



def action_csv(third_info, name, file_name, type, first_col=None,second_col=None,third_col=None,bit_ach=None):
    random.seed(42) # num1: 41, num2: 8, num3: 2
    with open(file_name, mode='r', newline='', encoding='utf-8') as file:
        data_list = list(csv.DictReader(file))
        
        total_rows = len(data_list)
        #print(f"Total data rows in file: {total_rows}")
        if type == "pass":
            pass_opt = []
            global opt1
            global opt2
            global opt3
            num1 = random.randint(1, total_rows)
            num2 = random.randint(1, total_rows)
            num3  = random.randint(1, total_rows)
            while num1 == num2 is True or num1 == num3 is True or num2 == num3 is True:
                num1 = random.randint(1, total_rows)
                num2 = random.randint(1, total_rows)
                num3 = random.randint(1, total_rows)
                print(num1, num2, num3)
            opt1 = data_list[num1]
            opt2 = data_list[num2]
            opt3 = data_list[num3]
            pass_opt.append(opt1)
            pass_opt.append(opt2)
            pass_opt.append(opt3)


            return pass_opt
        
        elif type == "set":
            data = []
            filename = file_name
            with open(filename, mode="a", newline="", encoding="utf-8") as f:
                data.append({"username": name, f"{second_col}": second_col, f"{third_col}": third_info})#first / name - username, second / secondinput - pass_id, third / thirdinput - pass
                writer = csv.DictWriter(f, fieldnames=["username", f"{second_col}", f"{third_col}"])  #
                #writer.writeheader()
                writer.writerows(data)

        elif type == "check":
            data = []
            filename = file_name
            with open(filename, mode="r", newline="", encoding="utf-8") as f:
                exist = 0
                data_list = list(csv.DictReader(f))
        
                total_rows = len(data_list)

                for row in data_list:
                    if row["username"].lower() == name.lower():
                        return 1
                return 0
                
        elif type == "get":
            data = []
            filename = file_name
            with open(filename, mode="r", newline="", encoding="utf-8") as f:
                data_list = (csv.DictReader(f))
                for row in data_list:
                            # Check if the field matches the target value
                    if row["username"].lower() == name.lower():
                        print("\033[3mTerminal: Found User!\033[0m")
                        return row

            return None  
        elif type == "update":
            data = []
            filename = file_name
            with open(filename, mode="a", newline="", encoding="utf-8") as f:
                data.append({"username": name, f"{second_col}": third_info, f"{third_col}": third_col})#first / name - username, second / secondinput - pass_id, third / thirdinput - pass
                writer = csv.DictWriter(f, fieldnames=["username", f"{second_col}", f"{third_col}"])  #
                #writer.writeheader()
                writer.writerows(data)

        elif type == "change":
            data = []
            filename = file_name

       
            with open(filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader) 
            target_row_index = rows.index([name, f"{second_col}", f"{third_col}"])
            rows[target_row_index] = [name, f"{bit_ach}", f"{third_info}"]

            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(rows)




def mask_input(prompt="Enter Password: "):
    print(prompt, end="", flush=True)
    password = ""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            char = sys.stdin.read(1)
            if char in ('\r', '\n'): # Enter key
                break
            elif char == '\x7f': # Backspace key
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                password += char
                sys.stdout.write('#')
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    print()
    return password


def login_check(name,name_check,timing):
    if not name:
        print("You must enter a name!")
        return TypeError
    elif name_check == 1:
        try:
            #Needs to do the enter password to "Login" method/check 
            space = f"\033[0mPlease enter your password!\nRemember, your password is \033[3mCase-Sensitive\033[0m!"
            basic_details = action_csv(1,name,"user_pass.csv","get")
            name = basic_details["username"]
            body_text(name,space,3,0.05)
            password_input = mask_input()
            if password_input == basic_details["pass"]:
                print("yes")
                stage = "Logged-In"
                return stage, name
            else:
                stage = "Not-Logged-In"
                return stage
        except:
            stage = "Not-Logged-In"
            return stage

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


def call_password_select(name):
    pass_opt = action_csv(1,name,"pass_list.csv","pass")
    space = f"Select Password Option:\n1. {pass_opt[0]['pass']}\n2. {pass_opt[1]['pass']}\n3. {pass_opt[2]['pass']}"
    #Select Password Option:\n1. {pass_opt[0]['pass']}\n2. {pass_opt[1]['pass']}\n3. {pass_opt[2]['pass']} 
    body_text(name, space, 3,0.05)
    return pass_opt


def bit_check(bit_value):
    inventory = []
    if (bit_value & 1) != 0:
        inventory.append("- Item 1")
    if (bit_value & 2) != 0:
        inventory.append("- Item 2")
    if (bit_value & 4) != 0:
        inventory.append("- Item 3")
    if (bit_value & 8) != 0:
        inventory.append("- Item 4")
    if (bit_value & 16) != 0:
        inventory.append("- Item 5")
    if (bit_value & 32) != 0:
        inventory.append("- Item 6")        
    if (bit_value & 64) != 0:
        inventory.append("- Item 7")
    if (bit_value & 128) != 0:
        inventory.append("- Item 8")
    if (bit_value & 256) != 0:
        inventory.append("- Item 9")
    if (bit_value & 512) != 0:
        inventory.append("- Item 10")
    if (bit_value & 1024) != 0:
        inventory.append("- Item 11")
    if (bit_value & 2048) != 0:
        inventory.append("- Item 12")
    return inventory 




def bit_check_ach(bit_value, bit_read):
    achievements = []
    if (bit_value & 1) != 0:
        if (bit_read & 1) != 0:
            achievements.append('- "Open Inventory" (NEW)')
        else:
            achievements.append('- "Open Inventory"')
    if (bit_value & 2) != 0:
        if (bit_read & 2) != 0:
            achievements.append('- Make Your First Trade (NEW)')
        else:
            achievements.append('- Make Your First Trade')
    if (bit_value & 4) != 0:
        if (bit_read & 4) != 0:
            achievements.append("- Achievement 3 (NEW)")
        else:
            achievements.append("- Achievement 3")
    if (bit_value & 8) != 0:
        if (bit_read & 8) != 0:
            achievements.append("- Achievement 4 (NEW)")
        else:
            achievements.append("- Achievement 4")
    if (bit_value & 16) != 0:
        if (bit_read & 16) != 0:
            achievements.append("- Achievement 5 (NEW)")
        else:
            achievements.append("- Achievement 5")
    if (bit_value & 32) != 0:
        if (bit_read & 32) != 0:
            achievements.append("- Achievement 6 (NEW)")
        else:
            achievements.append("- Achievement 6")
    if (bit_value & 64) != 0:
        if (bit_read & 64) != 0:
            achievements.append("- Achievement 7 (NEW)")
        else:
            achievements.append("- Achievement 7")
    if (bit_value & 128) != 0:
        if (bit_read & 128) != 0:
            achievements.append("- Achievement 8 (NEW)")
        else:
            achievements.append("- Achievement 8")
    if (bit_value & 256) != 0:
        if (bit_read & 256) != 0:
            achievements.append("- Achievement 9 (NEW)")
        else:
            achievements.append("- Achievement 9")
    if (bit_value & 512) != 0:
        if (bit_read & 512) != 0:
            achievements.append("- Achievement 10 (NEW)")
        else:
            achievements.append("- Achievement 10")
    if (bit_value & 1024) != 0:
        if (bit_read & 1024) != 0:
            achievements.append("- Achievement 11 (NEW)")
        else:
            achievements.append("- Achievement 11")
    if (bit_value & 2048) != 0:
        if (bit_read & 2048) != 0:
            achievements.append("- Achievement 12 (NEW)")
        else:
            achievements.append("- Achievement 12")
    return achievements
