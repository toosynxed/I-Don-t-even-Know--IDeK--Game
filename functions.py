import random
import os
import time
import csv

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def body_text(name, space, type):
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
                time.sleep(0.05)
                clear_screen()
        elif type == 4:
            iteration = 1
            for i in range(0,15):
                space = f"Loading{iteration * '.'}"
                iteration = iteration + 1
                time.sleep(timing)
                if iteration > 3:
                    iteration = 0

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

    except:
        print("Type not valid")



def action_csv(input, name, file_name, type):
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
            with open(filename, mode="w", newline="", encoding="utf-8") as f:
                data.append({"name": name, "pass": input})
                writer = csv.DictWriter(f, fieldnames=["name", "pass"])
                writer.writeheader()
                writer.writerows(data)
        