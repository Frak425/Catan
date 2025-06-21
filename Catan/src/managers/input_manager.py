import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from graphics_manager import GraphicsManager
    from helper_manager import HelperManager

from src.ui.button import Button
from src.entities.node import Node
from src.ui.menu import Menu

class InputManager:
    def __init__(self):
        #All of these have to be defined after initialization
        self.game_manager: "GameManager" = None
        self.graphics_manager: "GraphicsManager" = None
        self.helper_manager:"HelperManager" = None
        
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

        ## --- VARIABLES --- ##

    def handle_input(self, x, y) -> None:
        state = self.game_manager.game_state
        if self.graphics_manager.menu_open:
            button_clicked = self.helper_manager.check_button_list_clicked(self.buttons["menu"][self.menu.active_tab], (x, y), 50, 50)
            if not button_clicked:
                button_clicked = self.helper_manager.check_button_list_clicked(self.buttons["menu"]["tabs"], (x, y), 50, 50)
                print(self.buttons["menu"]["tabs"])
        else:
            button_clicked = self.helper_manager.check_button_list_clicked(self.buttons[state], (x, y))
        if button_clicked:
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
        self.menu.open_menu()
        self.graphics_manager.menu_open = True

    def close_menu(self):
        self.menu.close_menu()
        self.graphics_manager.menu_open = False

    def set_game_state(self, state: str):
        self.game_manager.game_state = state

    def quit(self):
        self.game_manager.running = False

    ## --- ON INIT --- ##

    def create_menu(self) -> Menu:
        menu_margins = (50, 50) #top, bottom
        menu_size = (self.game_manager.screen_w - 2 * menu_margins[0], self.game_manager.screen_h - 2 * menu_margins[1])
        init_location = (self.game_manager.screen_w + menu_margins[0], menu_margins[1]) #of top left corner
        final_location = menu_margins #of top left corner
        background_color = (100, 100, 100)
        menu = Menu(self.game_manager.screen, self.game_manager.game_font, "static", self.buttons['menu'], menu_size, init_location, final_location, bckg_color=background_color)
        return menu

    def set_game_manager(self, game_manager: 'GameManager') -> None:
        self.game_manager = game_manager
        self.sob_size = self.game_manager.screen_w / 12 / 1.5
        self.sob_offset = self.game_manager.screen_h / 24 / 1.5
        self.buttons = self.create_buttons()
        self.menu = self.create_menu()

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager') -> None:
        self.graphics_manager = graphics_manager

    def set_helper_manager(self, helper_manager: 'HelperManager') -> None:
        self.helper_manager = helper_manager

    def create_buttons(self) -> object:
        return {
            "main_menu": self.create_title_buttons(),
            "setup": self.create_setup_buttons(),
            "game": self.create_game_buttons(),
            "menu": self.create_menu_buttons()
        }

    def create_title_buttons(self) -> list[Button]:
        #create title screen
        play_b_w = 200
        play_b_h = 75
        play_button = Button("main_menu", (0, 100, 0), "PLAY", pygame.rect.Rect(self.game_manager.screen_w / 2 - play_b_w / 2, self.game_manager.screen_h / 2 - play_b_h / 1.75, play_b_w, play_b_h), "play", self.game_manager.screen, self.game_manager.game_font, (0, 0), lambda: self.set_game_state("setup"))
        quit_button = Button("main_menu", (100, 0, 0), "QUIT", pygame.rect.Rect(self.game_manager.screen_w / 2 - play_b_w / 2, self.game_manager.screen_h / 2 + play_b_h / 1.75, play_b_w, play_b_h), "quit", self.game_manager.screen, self.game_manager.game_font, (0, 0), lambda: self.quit)
        return [play_button, quit_button]

    def create_setup_buttons(self) -> list[Button]:
        #create game setup buttons
        play_b_w = 200
        play_b_h = 75
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
        settings_menu_button = Button("game_setup", (100, 0, 0), "image", [self.game_manager.screen_w - self.sob_offset - self.sob_size, self.sob_offset, self.sob_size, self.sob_size], "settings_menu", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        return [player_num_increase_button, player_num_decrease_button, difficulty_level_easy_button, difficulty_level_medium_button, difficulty_level_hard_button, settings_menu_button, player_choose_color_cycle_button, game_start_button, game_setup_back_button]

    def create_game_buttons(self) -> list[Button]:
        #create board buttons
        board_buy_settlement_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_settlement", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_city_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_city", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_road_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_road", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_buy_development_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_development", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        board_roll_dice_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_roll_dice", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        settings_menu_button = Button("game_setup", (100, 0, 0), "image", [self.game_manager.screen_w - self.sob_offset - self.sob_size, self.sob_offset, self.sob_size, self.sob_size], "settings_menu", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        return [board_buy_settlement_button, board_buy_city_button, board_buy_road_button, board_buy_development_button, board_roll_dice_button, settings_menu_button]
        
    def create_menu_buttons(self) -> list[Button]:    
        """
        Tabs:
        -Input
        -Accessibility
        -Graphics
        -Audio
        -Gameplay
        """

        #TODO: fill with buttons
        tabs = [
            Button("menu", (100, 0, 0), "Input", pygame.rect.Rect(50, 10, 40, 20), "input", self.game_manager.screen, self.game_manager.game_font, (0, 0), lambda: self.menu.change_tab("input")),
            Button("menu", (100, 0, 0), "Accessibility", pygame.rect.Rect(100, 10, 100, 20), "accessibility", self.game_manager.screen, self.game_manager.game_font, (0, 0), lambda: self.menu.change_tab("accessibility")),
            Button("menu", (100, 0, 0), "Gameplay", pygame.rect.Rect(150, 10, 60, 20), "gameplay", self.game_manager.screen, self.game_manager.game_font, (0, 0), lambda: self.menu.change_tab("gameplay")),
            Button("menu", (100, 0, 0), "Audio", pygame.rect.Rect(200, 10, 40, 20), "audio", self.game_manager.screen, self.game_manager.game_font, (0, 0), lambda: self.menu.change_tab("audio")),
            Button("menu", (100, 0, 0), "Graphics", pygame.rect.Rect(250, 10, 70, 20), "graphics", self.game_manager.screen, self.game_manager.game_font, (0, 0), lambda: self.menu.change_tab("graphics"))
        ] 

        """
        Input (keyboard and controller):
        -Controller vibration (toggle)
        -Deadzone adjustment (slider)
        -Invert Y and X axes (toggles)
        -Key remapping (list TBD: something similar to minecraft w/ keyboard and controller inputs listed?)
        -Sensitivities (sliders TBD)
        """
        #TODO: fill with buttons
        input_buttons = [
            Button("menu", (200, 50, 100), "test1", pygame.rect.Rect(200, 100, 100, 50), "test1", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        ] 

    
        """
        accessability:
        -Colorblind mode: deuteranopia, protanopia, and tritanopia (multi-choice select box)
        -Font Size: small, medium, large (multi-choice select box)
        -High contrast mode (toggle)
        -TTS: Hesitant to implement because limited usage and maximal time to produce
        """
        #TODO: fill with buttons
        accessability_buttons = [
            Button("menu", (200, 50, 100), "test2", pygame.rect.Rect(200, 100, 100, 50), "test2", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        ] 

    
        """
        Graphics:
        -AA (toggle)
        -Brightness (slider)
        -Windowed/fullscreen (toggle)
        -Particle effects (toggle)
        -Resolution (multi-choice select box)
        -Shadows (toggle)
        -Texture quality (multi-choice select box)
        -V-sync (toggle)
        """
        #TODO: fill with buttons
        graphics_buttons = [
            Button("menu", (200, 50, 100), "test3", pygame.rect.Rect(200, 100, 100, 50), "test3", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        ] 

    
        """
        Audio:
        -Master (slider)
        -Music (slider)
        -SFX (toggle)
        """
        #TODO: fill with buttons
        audio_buttons = [
            Button("menu", (200, 50, 100), "test4", pygame.rect.Rect(200, 100, 100, 50), "test4", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        ] 

    
        """
        Gameplay:
        -HUD (ask ChatGPT)
        -Language (multi-choice select box)
        """ 
        #TODO: fill with buttons
        gameplay_buttons = [
            Button("menu", (200, 50, 100), "test5", pygame.rect.Rect(200, 100, 100, 50), "test5", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        ] 
        
        return {
            "tabs": tabs,
            "gameplay": gameplay_buttons,
            "audio": audio_buttons,
            "graphics": graphics_buttons,
            "accessability": accessability_buttons,
            "input": input_buttons
        }
