from random import randint
import os
import time
import sys

player = {}
game_map = []
fog = []
original_map = []  # Store original map for replenishment

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)


def load_map(map_struct):
    global MAP_WIDTH
    global MAP_HEIGHT
    
    map_f = open("Assignment\\level1.txt", 'r')
    map_struct.clear()
    

    for line in map_f:

        line = line.rstrip('\n')
        if line or len(map_struct) == 0:
            if len(line) < 30:
                line = line + ' ' * (30 - len(line)) #add spaces to make width = 30
            elif len(line) > 30:
                line = line[:30] #excatly 30 chars
                
            row = list(line)
            map_struct.append(row)
    
    if map_struct:
        MAP_WIDTH = 30
        MAP_HEIGHT = len(map_struct)

def replenish_ore():
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if original_map[y][x] in ['C', 'S', 'G'] and game_map[y][x] == ' ':
                if randint(1, 100) <= 20:  # 20% chance
                    game_map[y][x] = original_map[y][x]

#clears fog around player
def clear_fog(fog, player):
    px, py = player['x'], player['y']
    
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx, ny = px + dx, py + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                fog[ny][nx] = False

def initialize_game(game_map, fog, player):

    load_map(game_map)
    
    # Store original map for replenishment
    original_map.clear()
    for row in game_map:
        original_map.append(row[:])
    
    #sets up fog
    fog.clear()
    for y in range(MAP_HEIGHT):
        fog.append([True] * MAP_WIDTH)
    
    #sets up player for new game
    player.clear()
    player['name'] = ''
    player['x'] = 0
    player['y'] = 0
    player['portal_x'] = 0
    player['portal_y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 1
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY
    player['backpack_capacity'] = 10
    player['pickaxe_level'] = 1
    
    clear_fog(fog, player)
    
#draws map with fog included
def draw_map(game_map, fog, player):
    print("+------------------------------+")
    for y in range(MAP_HEIGHT):
        print("|", end="")
        for x in range(MAP_WIDTH):
            if x == player['x'] and y == player['y']:
                print("M", end="")
            elif x == player['portal_x'] and y == player['portal_y'] and (x != 0 or y != 0):
                print("P", end="")
            elif fog[y][x]:
                print("?", end="")
            else:
                print(game_map[y][x], end="")
        print("|")
    print("+------------------------------+")

#3x3 player view
def draw_view(game_map, fog, player):
    px, py = player['x'], player['y']
    
    print("+---+")
    for dy in range(-1, 2):
        print("|", end="")
        for dx in range(-1, 2):
            nx, ny = px + dx, py + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                if dx == 0 and dy == 0:
                    print("M", end="")
                elif nx == 0 and ny == 0:
                    print("T", end="")
                else:
                    cell = game_map[ny][nx]
                    print(cell if cell != 'T' else ' ', end="")
            else:
                print("#", end="")
        print("|")
    print("+---+")

#display player info
def show_information(player):
    print("----- Player Information -----")
    print(f"Name: {player['name']}")
    if not player.get('in_town', False):
        print(f"Current position: ({player['x']}, {player['y']})")
    else:
        print(f"Portal position: ({player['portal_x']}, {player['portal_y']})")
    
    pickaxe_type = ['copper', 'silver', 'gold'][min(player['pickaxe_level'] - 1, 2)]
    print(f"Pickaxe level: {player['pickaxe_level']} ({pickaxe_type})")
    
    if not player.get('in_town', False):
        print(f"Gold: {player['gold']}")
        print(f"Silver: {player['silver']}")
        print(f"Copper: {player['copper']}")
    
    print("------------------------------")
    total_load = player['copper'] + player['silver'] + player['gold']
    print(f"Load: {total_load} / {player['backpack_capacity']}")
    print("------------------------------")
    print(f"GP: {player['GP']}")
    print(f"Steps taken: {player['steps']}")
    print("------------------------------")

def save_top_score(player):
    scores = load_top_scores()
        
    
    new_score = {
        'name': player['name'],
        'days': player['day'],
        'steps': player['steps'],
        'gp': player['GP']
    } #add current player score
    scores.append(new_score)

    scores.sort(key=lambda x: (x['days'], x['steps'], -x['gp']))#sort score based on quality of score
        
    scores = scores[:5] #only top 5 kept
        

    with open("top_scores.txt", 'w') as f:  
        for score in scores:
            f.write(f"{score['name']},{score['days']},{score['steps']},{score['gp']}\n")
        
    print(f"\nCongratulations! Your score has been saved to the leaderboard!")

def load_top_scores():
    scores = []

    with open("top_scores.txt", 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                if len(parts) >= 4:
                    scores.append({
                        'name': parts[0],
                        'days': int(parts[1]),
                        'steps': int(parts[2]),
                        'gp': int(parts[3])
                    }) #standard reading and outputting
    
    return scores

def show_top_scores():
    scores = load_top_scores()
    
    print()
    print("=" * 60)
    print("                      TOP SCORES  ")
    print("=" * 60)
    
    if not scores:
        print("                 No scores recorded yet!")
    else:
        print("Rank | Player Name      | Days | Steps | GP   ")
        print("-" * 60)
        
        for i, score in enumerate(scores, 1):
            name = score['name']
            print(f" {i:2d}  | {name:<15} | {score['days']:4d} | {score['steps']:5d} | {score['gp']:4d}")
    
    print("=" * 60)
    print()

def save_game(game_map, fog, player):
    try:
        with open("game.txt", 'w') as f:
            #save player data on file
            f.write(f"{player['name']}\n")
            f.write(f"{player['x']},{player['y']}\n")
            f.write(f"{player['portal_x']},{player['portal_y']}\n")
            f.write(f"{player['copper']},{player['silver']},{player['gold']}\n")
            f.write(f"{player['GP']}\n")
            f.write(f"{player['day']}\n")
            f.write(f"{player['steps']}\n")
            f.write(f"{player['turns']}\n")
            f.write(f"{player['backpack_capacity']}\n")
            f.write(f"{player['pickaxe_level']}\n")
            
            #save fog data
            for row in fog:
                f.write(','.join('1' if cell else '0' for cell in row) + '\n')
            
            #save current map state
            for row in game_map:
                f.write(','.join(row) + '\n')
        
        print("Game saved.")
    except:
        print("Error saving game.")
        
#load game
def load_game(game_map, fog, player):
    try:
        with open("game.txt", 'r') as f:
            lines = f.readlines()
            
            #load player data
            player['name'] = lines[0].strip()
            x, y = map(int, lines[1].strip().split(','))
            player['x'], player['y'] = x, y
            px, py = map(int, lines[2].strip().split(','))
            player['portal_x'], player['portal_y'] = px, py
            copper, silver, gold = map(int, lines[3].strip().split(','))
            player['copper'], player['silver'], player['gold'] = copper, silver, gold
            player['GP'] = int(lines[4].strip())
            player['day'] = int(lines[5].strip())
            player['steps'] = int(lines[6].strip())
            player['turns'] = int(lines[7].strip())
            player['backpack_capacity'] = int(lines[8].strip())
            player['pickaxe_level'] = int(lines[9].strip())
            
            #load fog data
            fog.clear()
            for i in range(10, 10 + MAP_HEIGHT):
                if i < len(lines):
                    row = [cell == '1' for cell in lines[i].strip().split(',')]
                    fog.append(row)
                else:
                    fog.append([True] * MAP_WIDTH)
            
            #load current map state
            game_map.clear()
            for i in range(10 + MAP_HEIGHT, 10 + MAP_HEIGHT * 2):
                if i < len(lines):
                    row = lines[i].strip().split(',')
                    game_map.append(row)
        
        return True
    except:
        print("No saved game found.")
        return False

def show_main_menu():
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    print("(T)op scores")
    print("(Q)uit")
    print("------------------")

def show_town_menu(player):
    print()
    print(f"DAY {player['day']}")
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")

def show_shop_menu(player):
    os.system('cls')
    print("----------------------- Shop Menu -------------------------")
    
    #pick upgrade
    if player['pickaxe_level'] < 3:
        level = player['pickaxe_level'] + 1
        mineral_type = ['silver', 'gold'][player['pickaxe_level'] - 1]
        price = pickaxe_price[player['pickaxe_level'] - 1]
        print(f"(P)ickaxe upgrade to Level {level} to mine {mineral_type} ore for {price} GP")
    
    #bp upgrade
    capacity = player['backpack_capacity']
    upgrade_price = capacity * 2
    new_capacity = capacity + 2
    print(f"(B)ackpack upgrade to carry {new_capacity} items for {upgrade_price} GP")
    
    print("(L)eave shop")
    print("-----------------------------------------------------------")
    print(f"GP: {player['GP']}")
    print("-----------------------------------------------------------")

def sell_ore(player):
    total_gp = 0
    sales_messages = []
    
    for mineral in ['copper', 'silver', 'gold']:
        amount = player[mineral]
        if amount > 0:
            min_price, max_price = prices[mineral]
            price_per_piece = randint(min_price, max_price)
            total_earned = amount * price_per_piece
            total_gp += total_earned
            sales_messages.append(f"You sell {amount} {mineral} ore for {total_earned} GP.")
            player[mineral] = 0
    
    player['GP'] += total_gp
    
    if sales_messages:
        for msg in sales_messages:
            print(msg)
        print(f"You now have {player['GP']} GP!")
    
    # Replenish ore when returning to town
    replenish_ore()
    
    return total_gp > 0

def mine_ore(player, mineral_type):
    if mineral_type == 'C':
        pieces = randint(1, 5)
        mineral = 'copper'
    elif mineral_type == 'S':
        pieces = randint(1, 3)
        mineral = 'silver'
    elif mineral_type == 'G':
        pieces = randint(1, 2)
        mineral = 'gold'
    else:
        return False
    
    current_load = player['copper'] + player['silver'] + player['gold']
    can_carry = player['backpack_capacity'] - current_load
    
    if can_carry <= 0:
        return False
    
    actual_pieces = min(pieces, can_carry)
    player[mineral] += actual_pieces
    
    print(f"You mined {actual_pieces} piece(s) of {mineral}.")
    if actual_pieces < pieces:
        print(f"...but you can only carry {actual_pieces} more piece(s)!")
    
    return True

def can_mine_mineral(player, mineral_type):
    if mineral_type == 'C':
        return True
    elif mineral_type == 'S':
        return player['pickaxe_level'] >= 2
    elif mineral_type == 'G':
        return player['pickaxe_level'] >= 3
    return False

def move_player(player, game_map, fog, direction):
    x, y = player['x'], player['y']
    
    if direction.upper() == 'W':
        new_y = y - 1
        new_x = x
    elif direction.upper() == 'S':
        new_y = y + 1
        new_x = x
    elif direction.upper() == 'A':
        new_x = x - 1
        new_y = y
    elif direction.upper() == 'D':
        new_x = x + 1
        new_y = y
    else:
        return False
    
    #check if position exist and if still in map range
    if new_x < 0 or new_x >= MAP_WIDTH or new_y < 0 or new_y >= MAP_HEIGHT:
        print("You can't go that way.")
        return False
    
    #check if returning to town
    if new_x == 0 and new_y == 0:
        player['x'] = new_x
        player['y'] = new_y
        player['steps'] += 1
        return "town"
    
    #check whats at the new pos
    cell = game_map[new_y][new_x]
    
    #check load, then check pickaxe
    if cell in ['C', 'S', 'G']:
        current_load = player['copper'] + player['silver'] + player['gold']
        
        if current_load >= player['backpack_capacity']:
            print("You can't carry any more, so you can't go that way.")
            return False
        
        if not can_mine_mineral(player, cell):
            print("Your pickaxe isn't strong enough to mine that.")
            return False
        
        #mine
        if mine_ore(player, cell):
            game_map[new_y][new_x] = ' '  # Remove ore after mining
            player['x'] = new_x
            player['y'] = new_y
            player['steps'] += 1
            clear_fog(fog, player)
            return True
    else:
        #movement
        player['x'] = new_x
        player['y'] = new_y
        player['steps'] += 1
        clear_fog(fog, player)
        return True
    
    return False

def check_win_condition(player):
    return player['GP'] >= WIN_GP

#main game loop
def main():
    game_state = 'main'
    
    message = '---------------- Welcome to Sundrop Caves! ----------------\nYou spent all your money to get the deed to a mine, a small\nbackpack, a simple pickaxe and a magical portal stone.\nHow quickly can you get the 500 GP you need to retire\nand live happily ever after?\n-----------------------------------------------------------\n\n'
    
    for characters in message:
        sys.stdout.write(characters)
        sys.stdout.flush()
        time.sleep(0.025)
    
    input("Press Enter to continue")
    os.system('cls')

    while True:
        if game_state == 'main':
            show_main_menu()
            choice = input("Your choice? ").strip().lower()
            
            if choice == 'n':
                initialize_game(game_map, fog, player)
                os.system('cls')

                greet_m = 'Greetings, miner! What is your name?\n'

                for characters in greet_m:
                    sys.stdout.write(characters)
                    sys.stdout.flush()
                    time.sleep(0.025)

                name = input("> ").strip()
                player['name'] = name

                os.system('cls')
                print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")
                input("Press Enter to continue.")
                player['in_town'] = True
                game_state = 'town'
                
            elif choice == 'l':
                initialize_game(game_map, fog, player)
                if load_game(game_map, fog, player):
                    player['in_town'] = True
                    game_state = 'town'
                else:
                    continue

            elif choice == 't':
                os.system('cls')
                show_top_scores()
                input("Press Enter to continue...")
                os.system('cls')
                    
            elif choice == 'q':
                break
                
        elif game_state == 'town':
            show_town_menu(player)
            choice = input("Your choice? ").strip().lower()
            os.system('cls')
            
            if choice == 'b':
                # Shop
                while True:
                    show_shop_menu(player)
                    shop_choice = input("Your choice? ").strip().lower()
                    os.system('cls')
                    
                    if shop_choice == 'p' and player['pickaxe_level'] < 3:
                        price = pickaxe_price[player['pickaxe_level'] - 1]
                        if player['GP'] >= price:
                            player['GP'] -= price
                            player['pickaxe_level'] += 1
                            mineral_type = ['silver', 'gold'][player['pickaxe_level'] - 2]
                            print(f"Congratulations! You can now mine {mineral_type}!")
                        else:
                            print("You don't have enough GP!")
                            
                    elif shop_choice == 'b':
                        price = player['backpack_capacity'] * 2
                        if player['GP'] >= price:
                            player['GP'] -= price
                            player['backpack_capacity'] += 2
                            print(f"Congratulations! You can now carry {player['backpack_capacity']} items!")
                        else:
                            print("You don't have enough GP!")
                            
                    elif shop_choice == 'l':
                        break
                        
                    input("Press Enter to continue...")
                        
            elif choice == 'i':
                show_information(player)
                input("Press Enter to continue...")
                
            elif choice == 'm':
                draw_map(game_map, fog, player)
                input("Press Enter to continue...")
                
            elif choice == 'e':
                player['in_town'] = False
                player['x'] = player['portal_x']
                player['y'] = player['portal_y']
                player['turns'] = TURNS_PER_DAY
                game_state = 'mine'
                
            elif choice == 'v':
                save_game(game_map, fog, player)
                input("Press Enter to continue...")
                
            elif choice == 'q':
                game_state = 'main'
                
        elif game_state == 'mine':
            print("---------------------------------------------------")
            print(f"DAY {player['day']}")
            print("---------------------------------------------------")
            draw_view(game_map, fog, player)
            
            current_load = player['copper'] + player['silver'] + player['gold']
            print(f"Turns left: {player['turns']}     Load: {current_load} / {player['backpack_capacity']}     Steps: {player['steps']}")
            print("(WASD) to move")
            print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu")
            
            action = input("Action? ").strip().lower()
            os.system('cls')
            
            if action in ['w', 'a', 's', 'd']:
                result = move_player(player, game_map, fog, action)
                player['turns'] -= 1
                
                if result == "town":
                    # Returned to town
                    sell_ore(player)
                    player['day'] += 1
                    player['in_town'] = True
                    
                    if check_win_condition(player):
                        print("-------------------------------------------------------------")
                        print(f"Woo-hoo! Well done, {player['name']}, you have {player['GP']} GP!")
                        print("You now have enough to retire and play video games every day.")
                        print(f"And it only took you {player['day']} days and {player['steps']} steps! You win!")
                        print("-------------------------------------------------------------\n")

                        save_top_score(player)
                        input("Press Enter to continue...")
                        game_state = 'main'
                        continue
                    
                    game_state = 'town'
                    continue
                
                # Check if out of turns
                if player['turns'] <= 0:
                    print("You are exhausted.")
                    print("You place your portal stone here and zap back to town.")
                    player['portal_x'] = player['x']
                    player['portal_y'] = player['y']
                    sell_ore(player)
                    player['day'] += 1
                    player['in_town'] = True
                    
                    if check_win_condition(player):
                        os.system('cls')
                        congrats_m = f'-------------------------------------------------------------\nWoo-hoo! Well done, {player['name']}, you have {player['GP']} GP!\nYou now have enough to retire and play video games every day.\nAnd it only took you {player['day']} days and {player['steps']} steps! You win!\n-------------------------------------------------------------'

                        for char in congrats_m:
                            sys.stdout.write(char)
                            sys.stdout.flush()
                            time.sleep(0.025)

                        input("Press Enter to continue...")
                        game_state = 'main'
                        continue
                    
                    game_state = 'town'
                    
            elif action == 'm':
                draw_map(game_map, fog, player)
                input("Press Enter to continue...")
                
            elif action == 'i':
                show_information(player)
                input("Press Enter to continue...")
                
            elif action == 'p':
                print("------------------------------------------------------")
                print("You place your portal stone here and zap back to town.")
                player['portal_x'] = player['x']
                player['portal_y'] = player['y']
                sell_ore(player)
                player['day'] += 1
                player['in_town'] = True
                
                if check_win_condition(player):
                    os.system('cls')
                    congrats_m = f'-------------------------------------------------------------\nWoo-hoo! Well done, {player['name']}, you have {player['GP']} GP!\nYou now have enough to retire and play video games every day.\nAnd it only took you {player['day']} days and {player['steps']} steps! You win!\n-------------------------------------------------------------'

                    for char in congrats_m:
                        sys.stdout.write(char)
                        sys.stdout.flush()
                        time.sleep(0.025)

                    input("Press Enter to continue...")
                    game_state = 'main'
                    continue
                
                game_state = 'town'
                
            elif action == 'q':
                game_state = 'main'


main()
