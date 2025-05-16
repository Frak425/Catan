import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from graphics_manager import GraphicsManager
    from helper_manager import HelperManager

from src.ui.button import Button
from src.entities.node import Node

class InputManager:
    def __init__(self):
        self.game_manager = None
        self.graphics_manager = None
        self.helper_manager = None
        self.buttons = self.create_buttons()

    def set_game_manager(self, game_manager: 'GameManager'):
        self.game_manager = game_manager

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager'):
        self.graphics_manager = graphics_manager

    def set_helper_manager(self, helper_manager: 'HelperManager'):
        self.helper_manager = helper_manager

    def create_buttons(self) -> object:
        #create title screen
        play_b_w = 200
        play_b_h = 75
        play_button = Button("main_menu", (0, 100, 0), "PLAY", pygame.rect.Rect(self.game_manager.screen_w / 2 - play_b_w / 2, self.game_manager.screen_h / 2 - play_b_h / 1.75, play_b_w, play_b_h), "play", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager.update_state)
        quit_button = Button("main_menu", (100, 0, 0), "QUIT", pygame.rect.Rect(self.game_manager.screen_w / 2 - play_b_w / 2, self.game_manager.screen_h / 2 + play_b_h / 1.75, play_b_w, play_b_h), "quit", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager.quit)
        title_screen_buttons = [play_button, quit_button]


        #create game setup buttons
        game_setup_back_button = Button("game_setup", (100, 0, 0), "Back", [self.game_manager.screen_w / 4 - play_b_w / 2, self.game_manager.screen_h / 2, 200, 100], "game_setup_back", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        gsb_w = 150
        gsb_h = 50
        game_start_button = Button("game_setup", (100, 0, 0), "Start", [self.game_manager.screen_w / 4 * 3 - gsb_w / 2, self.game_manager.screen_h / 8 * 6, gsb_w, gsb_h], "game_start", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        pnidb_size = self.game_manager.screen_h / 20
        player_num_increase_button = Button("game_setup", (0, 100, 0), "+", [self.game_manager.screen_w / 4 - pnidb_size / 2 + 100, self.game_manager.screen_h / 4 * 2.5, pnidb_size, pnidb_size], "player_num_increase", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        player_num_decrease_button = Button("game_setup", (0, 100, 0), "-", [self.game_manager.screen_w / 4 - pnidb_size / 2 - 100, self.game_manager.screen_h / 4 * 2.5, pnidb_size, pnidb_size], "player_num_decrease", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        player_choose_color_cycle_button = Button("game_setup", (0, 0, 0), "->", [10, 10, 10, 10], "player_choose_color_cycle", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        difficulty_level_easy_button = Button("game_setup", (0, 0, 0), "easy", [10, 10, 10, 10], "difficulty_level_easy", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        difficulty_level_medium_button = Button("game_setup", (0, 0, 0), "medium", [10, 10, 10, 10], "difficulty_level_medium", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        difficulty_level_hard_button = Button("game_setup", (0, 0, 0), "hard", [10, 10, 10, 10], "difficulty_level_hard", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        sob_size = self.game_manager.screen_w / 12 / 1.5
        sob_offset = self.game_manager.screen_h / 24 / 1.5
        settings_menu_button = Button("game_setup", (100, 0, 0), "image", [self.game_manager.screen_w - sob_offset - sob_size, sob_offset, sob_size, sob_size], "settings_menu", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        game_setup_buttons = [player_num_increase_button, player_num_decrease_button, difficulty_level_easy_button, difficulty_level_medium_button, difficulty_level_hard_button, settings_menu_button, player_choose_color_cycle_button, game_start_button, game_setup_back_button]


        #create settings buttons
        


        #create board buttons
        board_buy_settlement_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_settlement", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_city_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_city", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_road_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_road", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_development_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_development", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_roll_dice_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_roll_dice", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        settings_menu_button = Button("game_setup", (100, 0, 0), "image", [self.game_manager.screen_w - sob_offset - sob_size, sob_offset, sob_size, sob_size], "settings_menu", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buttons = [board_buy_settlement_button, board_buy_city_button, board_buy_road_button, board_buy_development_button, board_roll_dice_button, settings_menu_button]

        #add buttons to global list
        buttons = {
            "title_screen": title_screen_buttons,
            "setup": game_setup_buttons,
            "board": board_buttons,
        }

        return buttons

    def handle_main_menu(self, x, y):
        button_clicked = self.helper_manager.check_button_list_clicked(self.buttons["title_screen"], (x, y))
        if (type(button_clicked) != bool): #if a button is clicked, find which one and act accordingly
            button_name = button_clicked.button_name
            if (button_name == "play"):
                self.game_manager.game_state = "game_setup"
            
            elif (button_name == "quit"):
                running = False

    def handle_setup(self, x, y):
        button_clicked = self.helper_manager.check_button_list_clicked(self.buttons["setup"], (x, y)) #returns the button clicked or false if nothing is clicked
                
        #handle events for each button in setup buttons
        if (type(button_clicked) != bool): #if a button is clicked, find which one and act accordingly
            button_name = button_clicked.button_name
            print(button_name)
            if (self.button_name == "player_num_increase"):
                    if (self.game_manager.players_num < 4):
                        self.game_manager.players_num += 1

            elif (self.button_name == "player_num_decrease"):
                if (self.game_manager.players_num > 2):
                    self.game_manager.players_num -= 1

            elif (self.button_name == "player_choose_color_cycle"): #cycles through the list of different colors
                player_color_chosen_index += 1
                player_color_chosen_index %= len(self.game_manager.player_colors)

            elif (self.button_name == "difficulty_level_easy"):
                if (game_difficulty != "easy"):
                    game_difficulty = "easy"

            elif (self.button_name == "difficulty_level_medium"):
                if (game_difficulty != "medium"):
                    game_difficulty = "medium"

            elif (self.button_name == "difficulty_level_hard"):
                if (game_difficulty != "hard"):
                    game_difficulty = "hard"

            elif (self.button_name == "game_start"):
                self.game_manager.game_state = "init"

            elif (self.button_name == "settings_menu"): 
                self.graphics_manager.menu_open = True
            
            elif (self.button_name == "game_setup_back"):
                self.game_manager.game_state = "main_menu"

    def handle_menu(self, x, y):
        button_clicked = self.helper_manager.check_button_list_clicked(self.game_manager.menu.buttons, (x, y))

        if (type(button_clicked) != bool): #if a button is clicked, find which one and act accordingly
            button_name = button_clicked.button_name
            if (button_name == "settings_close"):
                self.game_manager.menu.close_menu()
            
            elif (button_name == "quit"):
                pass
    
    def handle_game(self, x, y):
        button_clicked = self.helper_manager.check_button_list_clicked(self.buttons["board"], (x, y))

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
                self.game_manager.menu.open_menu()
            else:
                print("Error: game_ongoing button name not found")

        selected_node: Node
        for i in range(len(self.game_manager.board.tiles)):
            for j in range(len(self.game_manager.board.tiles[i].nodes[0])):
                #tiles[i].nodes[0] returns cities and tiles[i].nodes[1] return roads
                mouse_at_city = self.helper_manager.check_point_in_rect(self.game_manager.board.tiles[i].nodes[0][j].rect, (x, y))
                mouse_at_road = self.helper_manager.check_point_in_rect(self.game_manager.board.tiles[i].nodes[1][j].rect, (x, y))
                if (mouse_at_city):
                    selected_node = self.game_manager.board.tiles[i].nodes[0][j]
                elif (mouse_at_road):
                    selected_node = self.game_manager.board.tiles[i].nodes[1][j]