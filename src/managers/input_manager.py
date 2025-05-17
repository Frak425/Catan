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
        #All of these have to be defined after initialization
        self.game_manager = None
        self.graphics_manager = None
        self.helper_manager = None
        #depends on game manager
        self.buttons = None

        #Handlers abstract the effects of all buttons
        #EX. "button_name_here": self.function_defined_below,
        self.main_menu_handlers = {
            "play": lambda: self.set_game_state("setup"),
            "quit": self.quit
        }
        self.setup_handlers = {
            "player_num_increase": self.player_num_increase,
            "player_num_decrease": self.player_num_decrease,
            "player_choose_color_cycle": self.choose_player_color_cycle,
            "difficulty_level_easy": self.set_diff_level_easy,
            "difficulty_level_medium": self.set_diff_level_medium,
            "difficulty_level_hard": self.set_diff_level_hard,
            "game_start": self.start_game,
            "settings_menu": self.open_menu,
            "game_setup_back": lambda: self.set_game_state("main_menu"),
        }
        self.game_handlers = {
            "settings_menu": self.open_menu
        }
        self.menu_handlers = {
            "settings_close": self.close_menu
        }
        self.game_over_handlers = {}
        self.handlers_by_state: dict[str, dict] = {
            "main_menu": self.main_menu_handlers,
            "setup": self.setup_handlers,
            "game": self.game_handlers,
            "game_over": self.game_over_handlers,
            "menu": self.menu_handlers
        }

    def set_game_manager(self, game_manager: 'GameManager') -> None:
        self.game_manager = game_manager

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager') -> None:
        self.graphics_manager = graphics_manager

    def set_helper_manager(self, helper_manager: 'HelperManager') -> None:
        self.helper_manager = helper_manager

    def create_buttons(self) -> object:
        #create title screen
        play_b_w = 200
        play_b_h = 75
        play_button = Button("main_menu", (0, 100, 0), "PLAY", pygame.rect.Rect(self.game_manager.screen_w / 2 - play_b_w / 2, self.game_manager.screen_h / 2 - play_b_h / 1.75, play_b_w, play_b_h), "play", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager.update_state)
        quit_button = Button("main_menu", (100, 0, 0), "QUIT", pygame.rect.Rect(self.game_manager.screen_w / 2 - play_b_w / 2, self.game_manager.screen_h / 2 + play_b_h / 1.75, play_b_w, play_b_h), "quit", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager.quit)
        main_menu_buttons = [play_button, quit_button]


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
        setup_buttons = [player_num_increase_button, player_num_decrease_button, difficulty_level_easy_button, difficulty_level_medium_button, difficulty_level_hard_button, settings_menu_button, player_choose_color_cycle_button, game_start_button, game_setup_back_button]


        #create settings buttons
        


        #create board buttons
        board_buy_settlement_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_settlement", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_city_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_city", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_road_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_road", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_development_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_development", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_roll_dice_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_roll_dice", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        settings_menu_button = Button("game_setup", (100, 0, 0), "image", [self.game_manager.screen_w - sob_offset - sob_size, sob_offset, sob_size, sob_size], "settings_menu", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        game_buttons = [board_buy_settlement_button, board_buy_city_button, board_buy_road_button, board_buy_development_button, board_roll_dice_button, settings_menu_button]

        #add buttons to global list
        buttons = {
            "main_menu": main_menu_buttons,
            "setup": setup_buttons,
            "game": game_buttons,
        }

        self.buttons = buttons

    def handle_input(self, x, y) -> None:
        state = self.game_manager.game_state
        if self.graphics_manager.menu_open:
            #TODO: Fix menu button creation handling. Right now, they are created in the menu class, but they should not be there
            button_clicked = self.helper_manager.check_button_list_clicked(self.buttons["menu"], (x, y))
        else:
            button_clicked = self.helper_manager.check_button_list_clicked(self.buttons[state], (x, y))
        button_name = button_clicked.button_name

        handler = self.handlers_by_state[state].get(button_name)
        if handler:
            handler()

    ## --- EVENT FUNCTIONS --- ##

    def player_num_increase(self):
        if (self.game_manager.players_num < 4):
            self.game_manager.players_num += 1

    def player_num_decrease(self):
        if (self.game_manager.players_num > 2):
            self.game_manager.players_num -= 1

    def choose_player_color_cycle(self):
        player_color_chosen_index += 1
        player_color_chosen_index %= len(self.game_manager.player_colors)

    def set_diff_level_easy(self):
        if (game_difficulty != "easy"):
            game_difficulty = "easy"

    def set_diff_level_medium(self):
        if (game_difficulty != "medium"):
            game_difficulty = "medium"

    def set_diff_level_hard(self):
        if (game_difficulty != "hard"):
            game_difficulty = "hard"

    def start_game(self):
        self.game_manager.game_state = "init"

    def open_menu(self):
        self.game_manager.menu.open_menu()
        self.graphics_manager.menu_open = True

    def close_menu(self):
        self.game_manager.menu.close_menu()
        self.graphics_manager.menu_open = False

    def set_game_state(self, state: str):
        self.game_manager.game_state = state

    def quit(self):
        self.game_manager.running = False