## Hi! Welcome to the I Don't Even Know Game!

Tbh, originally I wasn't even sure what I wanted to do with this, but I guess this is what I have gone off to do now!

### What Is There?
- Pretty much just a game (Or the framework at least - More actual content to come!)

### How to play?
- Double-click the ```IDeK``` executable (it opens in Terminal), or run ```python3 main_terminal.py```.
- The executable creates its save files (```user_pass.csv```, ```user_wallets.csv```, etc.) in the same folder as itself.
- Next, enter your username, and select a speed (1 - Very fast for animations, 10 - Much slower speed).
- If the username already exists, you will be prompted to log-in with your password, or to create an account if not.

### Menu Options:
1. Market:
This opens an interactive mini-game which will perform "ticks" everytime you press enter without entering anything into the terminal (actual buy/sell features to come!)
2. Inventory:
This is a placeholder (but works) for future content, utilising Bit-wise values for extremely low data usage

3. Achievements:
Also mainly a placeholder for future content, but does feature one achievement on account creation, and also features a "read receipt" function that updates alongside the Bit-wise values.

4. Leaderboard:
A functional leaderboard for your account Networth (from market), however, even though this works, as the market features are not quite ready yet, you will not be able to change your networth unless you edit you stats in ```user_wallets.csv```.


### Building the executable:
```
python3 -m venv .venv-build
.venv-build/bin/pip install pyinstaller
.venv-build/bin/pyinstaller -y IDeK.spec
```
The executable is written to ```dist/IDeK```.


## What Each File Is:

- ```main_terminal.py```

This is the intial file that players interact with when they start the game, handling the intial log-in/account creation graphics and logic.

- ```functions_terminal.py```

This file is the main handler for all the common features and functions across the game, from which all the other files call functions from.
This file utilises alot of re-usability features to allow for a wide range of use cases across different areas of the game.

- ```menu_terminal.py```

This file is responsibile for the GUI after players either sign in or create their accounts, handling navigation and display for each of the four different menu options.

- ```market_terminal.py```

This file is about 50/50 AI to my own code, with AI generating the actual price changes based off the planning and logic I created.

- ```gen_pass_terminal.py```

This file is also AI generated and just handles the random generation of ```pass_list.csv``` from which player "passwords" are selected from.

