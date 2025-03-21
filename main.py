import pygame
import random
import math

from helperFunctions import *

from src.entities.piece import Piece
from src.ui.button import Button
from src.entities.node import Node
from src.entities.player import Player
from src.entities.board import Board
from src.ui.menu import Menu

#initialize game
pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((screen_w, screen_h))

#set caption and icon
pygame.display.set_caption("Catan")
"""icon = pygame.image.load('')
pygame.display.set_icon(icon)"""

clock = pygame.time.Clock()

#global variables
game_state = "main_menu" # main menu -> game setup -> init -> game ongoing -> game over -> main menu
player_state = "roll" # roll -> trade -> buy -> place
settings_open = False

points_to_win = 10
players_num = 2
players_list = []
players_list_index = 0
player_colors = ["yellow", "blue", "green", "red"]
player_color_chosen_index = 0

game_difficulty = "easy"

font_size = 20
game_font = pygame.font.SysFont('Comic Sans', font_size)

framerates = [30, 60, 120, 240]
framerate_index = 0

num_tiles = 19


def create_buttons() -> object:
    #create title screen
    play_b_w = 200
    play_b_h = 75
    play_button = Button("main_menu", (0, 100, 0), "PLAY", [screen_w / 2 - play_b_w / 2, screen_h / 2 - play_b_h / 1.75, play_b_w, play_b_h], "play", screen, game_font, (0, 0))
    quit_button = Button("main_menu", (100, 0, 0), "QUIT", [screen_w / 2 - play_b_w / 2, screen_h / 2 + play_b_h / 1.75, play_b_w, play_b_h], "quit", screen, game_font, (0, 0))
    title_screen_buttons = [play_button, quit_button]


    #create game setup buttons
    game_setup_back_button = Button("game_setup", (100, 0, 0), "Back", [screen_w / 4 - play_b_w / 2, screen_h / 2, 200, 100], "game_setup_back", screen, game_font, (0, 0))
    gsb_w = 150
    gsb_h = 50
    game_start_button = Button("game_setup", (100, 0, 0), "Start", [screen_w / 4 * 3 - gsb_w / 2, screen_h / 8 * 6, gsb_w, gsb_h], "game_start", screen, game_font, (0, 0))
    pnidb_size = screen_h / 20
    player_num_increase_button = Button("game_setup", (0, 100, 0), "+", [screen_w / 4 - pnidb_size / 2 + 100, screen_h / 4 * 2.5, pnidb_size, pnidb_size], "player_num_increase", screen, game_font, (0, 0))
    player_num_decrease_button = Button("game_setup", (0, 100, 0), "-", [screen_w / 4 - pnidb_size / 2 - 100, screen_h / 4 * 2.5, pnidb_size, pnidb_size], "player_num_decrease", screen, game_font, (0, 0))
    player_choose_color_cycle_button = Button("game_setup", (0, 0, 0), "->", [10, 10, 10, 10], "player_choose_color_cycle", screen, game_font, (0, 0))
    difficulty_level_easy_button = Button("game_setup", (0, 0, 0), "easy", [10, 10, 10, 10], "difficulty_level_easy", screen, game_font, (0, 0))
    difficulty_level_medium_button = Button("game_setup", (0, 0, 0), "medium", [10, 10, 10, 10], "difficulty_level_medium", screen, game_font, (0, 0))
    difficulty_level_hard_button = Button("game_setup", (0, 0, 0), "hard", [10, 10, 10, 10], "difficulty_level_hard", screen, game_font, (0, 0))
    sob_size = screen_w / 12 / 1.5
    sob_offset = screen_h / 24 / 1.5
    settings_menu_button = Button("game_setup", (100, 0, 0), "image", [screen_w - sob_offset - sob_size, sob_offset, sob_size, sob_size], "settings_menu", screen, game_font, (0, 0))
    game_setup_buttons = [player_num_increase_button, player_num_decrease_button, difficulty_level_easy_button, difficulty_level_medium_button, difficulty_level_hard_button, settings_menu_button, player_choose_color_cycle_button, game_start_button, game_setup_back_button]


    #create settings buttons
    


    #create board buttons
    board_buy_settlement_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_settlement", screen, game_font, (0, 0))
    board_buy_city_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_city", screen, game_font, (0, 0))
    board_buy_road_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_road", screen, game_font, (0, 0))
    board_buy_development_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_development", screen, game_font, (0, 0))
    board_roll_dice_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_roll_dice", screen, game_font, (0, 0))
    settings_menu_button = Button("game_setup", (100, 0, 0), "image", [screen_w - sob_offset - sob_size, sob_offset, sob_size, sob_size], "settings_menu", screen, game_font, (0, 0))
    board_buttons = [board_buy_settlement_button, board_buy_city_button, board_buy_road_button, board_buy_development_button, board_roll_dice_button, settings_menu_button]

    #add buttons to global list
    buttons = {
        "title_screen": title_screen_buttons,
        "setup": game_setup_buttons,
        "board": board_buttons,
    }

    return buttons

def create_menu() -> Menu:
    menu_margins = (50, 50) #top, bottom
    menu_size = (screen_w - 2 * menu_margins[0], screen_h - 2 * menu_margins[1])
    init_location = (screen_w + menu_margins[0], menu_margins[1]) #of top left corner
    final_location = menu_margins #of top left corner
    background_color = (100, 100, 100)
    menu = Menu(screen, game_font, "static", menu_size, init_location, final_location, bckg_color=background_color)
    return menu

def init() -> None:
    for i in range(players_num):
        players_list.append(Player(player_colors, points_to_win))

    global board
    board = Board(screen_w / 27.32, screen_h, screen_w, num_tiles, screen, game_font, font_size)
    board.assign_tile_locations()
    board.assign_tiles()
    board.assign_tile_classes()

def check_game_over() -> bool:
    for i in range(len(players_list)):
        if players_list[i].score >= points_to_win:
            return True
    return False

#object that contains all of the game's buttons. Can be accessed through the following keys: "title_screen", "setup", "board", and "settings". Settings isn't a game state, rather, it contains all buttons for the settings menu
buttons = create_buttons()
menu = create_menu()

running = True
while running:

    clock.tick(framerates[framerate_index])
    screen.fill((30, 80, 150))

    #determine what to draw on the screen based on the game's state
    if (game_state == "main_menu"):
        for button in buttons["title_screen"]:
            button.draw_button()

    elif (game_state == "game_setup"):       
        for button in buttons["setup"]:
            button.draw_button()

    elif (game_state == "init"):
        init()
        game_state = "game_ongoing"
        continue

    elif (game_state == "game_ongoing"):
        board.draw_board()
        for button in buttons["board"]:
            button.draw_button()

    else:
        print("wrong game state")
        running = False
        
    if (menu.open):
        menu.draw_menu(clock.get_time())

    #handles events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #on a mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            #click in main menu
            if (game_state == "main_menu"):
                button_clicked = check_button_list_clicked(buttons["title_screen"], (x, y))

                if (type(button_clicked) != bool): #if a button is clicked, find which one and act accordingly
                    button_name = button_clicked.button_name
                    if (button_name == "play"):
                        game_state = "game_setup"
                    
                    elif (button_name == "quit"):
                        running = False
            
            #click in menu, comes before others because menu clicks are mutually exclusive to the other layers
            elif (menu.open):
                button_clicked = check_button_list_clicked(menu.buttons, (x, y))

                if (type(button_clicked) != bool): #if a button is clicked, find which one and act accordingly
                    button_name = button_clicked.button_name
                    if (button_name == "settings_close"):
                        menu.close_menu()
                    
                    elif (button_name == "quit"):
                        pass
                    
            #click in setup
            elif (game_state == "game_setup"):
                button_clicked = check_button_list_clicked(buttons["setup"], (x, y)) #returns the button clicked or false if nothing is clicked
                
                #handle events for each button in setup buttons
                if (type(button_clicked) != bool): #if a button is clicked, find which one and act accordingly
                    button_name = button_clicked.button_name
                    print(button_name)

                    if (button_name == "player_num_increase"): #increases the number of player in the game
                        if (players_num < 4):
                            players_num += 1

                    elif (button_name == "player_num_decrease"): #decreases the number of players in the game
                        if (players_num > 2):
                            players_num -= 1

                    elif (button_name == "player_choose_color_cycle"): #cycles through the list of different colors
                        player_color_chosen_index += 1
                        player_color_chosen_index %= len(player_colors)

                    elif (button_name == "difficulty_level_easy"): #set diff levels
                        if (game_difficulty != "easy"):
                            game_difficulty = "easy"
                            button_clicked.color = (0, 0, 0)

                    elif (button_name == "difficulty_level_medium"):
                        if (game_difficulty != "medium"):
                            game_difficulty = "medium"
                            button_clicked.color = (0, 0, 0)

                    elif (button_name == "difficulty_level_hard"):
                        if (game_difficulty != "hard"):
                            game_difficulty = "hard"
                            button_clicked.color = (0, 0, 0)

                    elif (button_name == "game_start"):
                        game_state = "init"

                    elif (button_name == "settings_menu"): 
                        menu.open_menu()
                    
                    elif (button_name == "game_setup_back"):
                        game_state = "main_menu"

            #click in game
            elif (game_state == "game_ongoing"):
                button_clicked = check_button_list_clicked(buttons["board"], (x, y))

                if (type(button_clicked) != bool):
                    button_name = button_clicked.button_name
                    if (button_name == "board_roll_dice"):
                        pass
                    elif (button_name == "board_buy_city"):
                        pass
                    elif (button_name == "board_buy_settlement"):
                        pass
                    elif (button_name == "board_buy_road"):
                        pass
                    elif (button_name == "board_buy_development"):
                        pass
                    elif (button_name == "settings_menu"):
                        menu.open_menu()
                    else:
                        print("Error: game_ongoing button name not found")

                selected_node: Node
                for i in range(len(board.tiles)):
                    for j in range(len(board.tiles[i].nodes[0])):
                        #tiles[i].nodes[0] returns cities and tiles[i].nodes[1] return roads
                        mouse_at_city = check_point_in_rect(board.tiles[i].nodes[0][j].rect, (x, y))
                        mouse_at_road = check_point_in_rect(board.tiles[i].nodes[1][j].rect, (x, y))
                        if (mouse_at_city):
                            selected_node = board.tiles[i].nodes[0][j]
                        elif (mouse_at_road):
                            selected_node = board.tiles[i].nodes[1][j]

            

    pygame.display.update()