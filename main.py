import pygame
import random
import math

from classes.piece import Piece
from classes.button import Button
from classes.node import Node
from classes.player import Player
from classes.board import Board

#initialize game
pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((screen_w, screen_h))

#set caption and icon
pygame.display.set_caption("Catan")
icon = pygame.image.load('')
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

#global variables
game_state = "main_menu" # main menu -> game setup -> init -> game ongoing -> game over -> main menu
player_state = "roll" # roll -> trade -> buy -> place
settings_open = False

players_num = 2
players_list = []
players_list_index = 0
player_colors = ["yellow", "blue", "green", "red"]
player_color_chosen_index = 0

game_difficulty = "easy"

#includes play button and game setup buttons
menu_buttons = []

board_buttons = []

settings_buttons = []

font_size = 20
game_font = pygame.font.SysFont('Comic Sans', font_size)

framerates = [30, 60, 120, 240]
framerate_index = 0

num_tiles = 19

settings_open = False


#global functions
def midpoint(point1: tuple[int], point2: tuple[int]) -> tuple:
    return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)

def check_point_in_rect(rect: list[int], point: tuple[int]) -> bool:
    x, y, w, h = rect
    px, py = point
    if (px > x and px < (x + w)) and \
       (py > y and py < (y + h)):
        return True
    else:
        return False

def point_in_polygon(point: tuple[int], polygon: list[tuple[int]]) -> bool:
        num_vertices = len(polygon)
        x, y = point[0], point[1]
        inside = False
    
        # Store the first point in the polygon and initialize the second point
        p1 = polygon[0]
    
        # Loop through each edge in the polygon
        for i in range(1, num_vertices + 1):
            # Get the next point in the polygon
            p2 = polygon[i % num_vertices]
    
            # Check if the point is above the minimum y coordinate of the edge
            if y > min(p1.y, p2.y):
                # Check if the point is below the maximum y coordinate of the edge
                if y <= max(p1.y, p2.y):
                    # Check if the point is to the left of the maximum x coordinate of the edge
                    if x <= max(p1.x, p2.x):
                        # Calculate the x-intersection of the line connecting the point to the edge
                        x_intersection = (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
    
                        # Check if the point is on the same line as the edge or to the left of the x-intersection
                        if p1.x == p2.x or x <= x_intersection:
                            # Flip the inside flag
                            inside = not inside
    
            # Store the current point as the first point for the next iteration
            p1 = p2
    
        # Return the value of the inside flag
        return inside

def create_buttons() -> None:
    #create start menu button
    play_b_w = 200
    play_b_h = 75
    play_button = Button("main_menu", (0, 100, 0), "PLAY", [screen_w / 2 - play_b_w / 2, screen_h / 2 - play_b_h / 1.75, play_b_w, play_b_h], "play_button", screen, game_font)
    quit_button = Button("main_menu", (100, 0, 0), "QUIT", [screen_w / 2 - play_b_w / 2, screen_h / 2 + play_b_h / 1.75, play_b_w, play_b_h], "quit_button", screen, game_font)

    #create game setup buttons

    game_setup_back_button = Button("game_setup", (100, 0, 0), "Back", [screen_w / 4 - play_b_w / 2, screen_h / 2, 200, 100], "game_setup_back_button", screen, game_font)

    gsb_w = 150
    gsb_h = 50
    game_start_button = Button("game_setup", (100, 0, 0), "Start", [screen_w / 4 * 3 - gsb_w / 2, screen_h / 8 * 6, gsb_w, gsb_h], "game_start", screen, game_font)


    pnidb_size = screen_h / 20
    player_num_increase_button = Button("game_setup", (0, 100, 0), "+", [screen_w / 4 - pnidb_size / 2 + 100, screen_h / 4 * 2.5, pnidb_size, pnidb_size], "player_num_increase_button", screen, game_font)
    player_num_decrease_button = Button("game_setup", (0, 100, 0), "-", [screen_w / 4 - pnidb_size / 2 - 100, screen_h / 4 * 2.5, pnidb_size, pnidb_size], "player_num_decrease_button", screen, game_font)

    player_choose_color_cycle_button = Button("game_setup", (0, 0, 0), "->", [10, 10, 10, 10], "player_choose_color_cycle_button", screen, game_font)

    difficulty_level_easy_button = Button("game_setup", (0, 0, 0), "easy", [10, 10, 10, 10], "difficulty_level_easy_button", screen, game_font)
    difficulty_level_medium_button = Button("game_setup", (0, 0, 0), "medium", [10, 10, 10, 10], "difficulty_level_medium_button", screen, game_font)
    difficulty_level_hard_button = Button("game_setup", (0, 0, 0), "hard", [10, 10, 10, 10], "difficulty_level_hard_button", screen, game_font)

    
    sob_size = screen_w / 12 / 1.5
    sob_offset = screen_h / 24 / 1.5
    settings_menu_button = Button("game_setup", (100, 0, 0), "image", [screen_w - sob_offset - sob_size, sob_offset, sob_size, sob_size], "settings_menu_button", screen, game_font)

    #create settings buttons
    settings_frame_rate_increase_button = Button("settings", (0, 0, 0), "->", [10, 10, 10, 10], "settings_frame_rate_increase_button", screen, game_font)
    settings_frame_rate_decrease_button = Button("settings", (0, 0, 0), "<-", [10, 10, 10, 10], "settings_frame_rate_decrease_button", screen, game_font)
    settings_audio_on_off_button = Button("settings", (0, 0, 0), "on", [10, 10, 10, 10], "settings_audio_on_off_button", screen, game_font)

    settings_close_buttons = Button("settings", (100, 0, 0), "X", [], "settings_menu_close_button", screen, game_font)

    #create board buttons
    board_buy_settlement_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_settlement_button", screen, game_font)
    board_buy_city_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_city_button", screen, game_font)
    board_buy_road_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_road_button", screen, game_font)
    board_buy_development_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_development_button", screen, game_font)
    board_roll_dice_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_roll_dice_button", screen, game_font)


    #add buttons to global list
    menu_buttons.append([play_button, quit_button, player_num_increase_button, player_num_decrease_button, difficulty_level_easy_button, difficulty_level_medium_button, difficulty_level_hard_button, settings_menu_button, player_choose_color_cycle_button, game_start_button, game_setup_back_button])
    board_buttons.append([board_buy_settlement_button, board_buy_city_button, board_buy_road_button, board_buy_development_button, board_roll_dice_button])
    settings_buttons.append([settings_frame_rate_increase_button, settings_frame_rate_decrease_button, settings_audio_on_off_button, settings_close_buttons])

def check_button_list_clicked(buttons: list[Button], mouse_location: tuple[int]) -> Button | bool:
    for i in range(len(buttons[0])):
        if (check_point_in_rect(buttons[0][i].rect, mouse_location)):
            return buttons[0][i]
    return False

def init() -> None:
    for i in range(players_num):
        players_list.append(Player(player_colors[i]))

    global board
    board = Board(screen_w / 27.32, screen_h, screen_w, num_tiles, screen, game_font, font_size)
    board.assign_tile_locations()
    board.assign_tiles()
    board.assign_tile_classes()

def check_game_over() -> bool:
    for i in range(len(players_list)):
        if players_list[i].score >= 10:
            return True
    return False

create_buttons()


running = True
#game loop
while running:

    clock.tick(framerates[framerate_index])
    screen.fill((30, 80, 150))

    #determine what to draw on the screen based on the game's state
    if (game_state == "main_menu"):
        menu_buttons[0][0].draw_button()
        menu_buttons[0][1].draw_button()

    elif (game_state == "game_setup"):
        for i in range(2, len(menu_buttons[0]), 1):
            menu_buttons[0][i].draw_button()

    elif (game_state == "init"):
        init()
        game_state = "game_ongoing"
        continue

    elif (game_state == "game_ongoing"):
        board.draw_board()
        for i in range(len(board_buttons)):
            board_buttons[0][i].draw_button()

    else:
        print("wrong game state")
        running = False
        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            if (game_state == "main_menu"):
                button_clicked = check_button_list_clicked(menu_buttons, (x, y)) #returns the button clicked or false if nothing is clicked

                if (type(button_clicked) != bool): #if a button is clicked, find which one and act accordingly
                    var_name = button_clicked.var_name
                    print(var_name)
                    if (var_name == "play_button"):
                        game_state = "game_setup"
                    
                    elif (var_name == "quit_button"):
                        running = False

            elif (game_state == "game_setup"):
                button_clicked = check_button_list_clicked(menu_buttons, (x, y)) #returns the button clicked or false if nothing is clicked

                if (type(button_clicked) != bool): #if a button is clicked, find which one and act accordingly
                    var_name = button_clicked.var_name

                    if (var_name == "player_num_increase_button"): #increases the number of player in the game
                        print(players_num)
                        if (players_num < 4):
                            players_num += 1

                    elif (var_name == "player_num_decrease_button"): #decreases the number of players in the game
                        print(players_num)
                        if (players_num > 2):
                            players_num -= 1

                    elif (var_name == "player_choose_color_cycle_button"): #cycles through the list of different colors
                        player_color_chosen_index += 1
                        player_color_chosen_index %= len(player_colors)

                    elif (var_name == "difficulty_level_easy_button"): #set diff levels
                        if (game_difficulty != "easy"):
                            game_difficulty = "easy"
                            buttons_clicked.color = (0, 0, 0)

                    elif (var_name == "difficulty_level_medium_button"):
                        if (game_difficulty != "medium"):
                            game_difficulty = "medium"
                            buttons_clicked.color = (0, 0, 0)

                    elif (var_name == "difficulty_level_hard_button"):
                        if (game_difficulty != "hard"):
                            game_difficulty = "hard"
                            buttons_clicked.color = (0, 0, 0)

                    elif (var_name == "game_start"):
                        game_state = "init"

                    elif (var_name == "settings_menu_button"): 
                        settings_open = True
                    
                    elif (var_name == "game_setup_back_button"):
                        game_state = "main_menu"

            elif (game_state == "settings"):
                buttons_clicked = check_button_list_clicked(settings_buttons, (x, y))

                if (type(buttons_clicked) != bool):
                    var_name = buttons_clicked.var_name

                    if (var_name == "settings_frame_rate_increase_button"):
                        framerate_index += 1
                        framerate_index %= len(framerates)

                    elif (var_name == "settings_frame_rate_decrease_button"):
                        framerate_index -= 1
                        framerate_index %= len(framerates)

                    elif (var_name == "settings_audio_on_off_button"):
                        pass

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

            elif (game_state == "Player_1" or game_state == "Player_2"):
                buttons_clicked = check_button_list_clicked(menu_buttons, (x, y))

                if (type(buttons_clicked) != bool):
                    var_name = buttons_clicked.var_name

                    if (var_name == "board_buy_settlement_button"):
                        pass

                    elif(var_name == "board_buy_city_button"):
                        pass

                    elif(var_name == "board_buy_road_button"):
                        pass

                    elif(var_name == "board_buy_development_button"):
                        pass

                    elif(var_name == "board_roll_dice_button"):
                        pass


    pygame.display.update()