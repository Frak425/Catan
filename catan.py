import pygame
import random
import math
#initialize game
pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((screen_w, screen_h))

#set caption and icon
"""pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('Downloads/ufo.png')
pygame.display.set_icon(icon)"""

class Piece:
    def __init__(self, type: str, color: tuple[int], location: tuple[int], points: list[tuple[int]], rotation: int) -> None:
        self.type = type
        self.color = color
        self.location = location
        self.points = points
        self.rotation = rotation

        self.surface = pygame.Surface(100, 100)
        pygame.draw.polygon(self.surface, self.color, self.points)
        pygame.transform.rotate(self.surface, self.rotation)

    def draw_piece(self):
        screen.blit(self.surface, self.location)

class Button:
    def __init__(self, layer: str, color: tuple[int], text: str, rect: list[int], var_name: str) -> None:
        self.layer = layer # main menu -> game setup -> board -> game over -> main menu
        self.color = color
        self.text = text
        self.rect = rect
        self.var_name = var_name
            
    def draw_button(self) -> None:
        pygame.draw.rect(screen, self.color, self.rect)
        text = game_font.render(self.text, False, (0, 0, 0))
        screen.blit(text, (self.rect[0], self.rect[1]))

    def check_clicked(self, coords: tuple[int]) -> bool:
        return check_point_in_rect(self.rect, coords)

class Node:
    def __init__(self, id: str, location: tuple):
        self.id = id  # unique identifier for the type (road or city)
        self.adjacent = []  # list of adjacent nodes (connected by roads). Not provided on init
        self.tiles = []  # list of adjacent tiles. Only defined if self.id == "city"
        self.location = location #(x, y) coordinates of each node
        self.rect = [self.location[0] - hitbox_w / 2, self.location[1] - hitbox_h / 2, hitbox_w, hitbox_h]

    def add_adjacent(self, nodes):
        self.adjacent = nodes

class Tile:
    def __init__(self, resource_type: str, nodes: list[list[Node]], color: tuple, center: tuple, number: int, points: list[tuple]) -> None:
        self.resource_type = resource_type #"sheep", "brick", etc.
        self.nodes = nodes # list of nodes adjacent to this tile. points can be accessed through nodes (Tile.location[i])
        self.points = points #list of corners in the form (x, y). Different from self.nodes because it's used to draw each polygon
        self.color = color
        self.center = center
        self.number = number

    def draw_tile(self) -> None:
        pygame.draw.polygon(screen, self.color, self.points)

class Player:
    def __init__(self, player_color) -> None:
        self.player_color = player_color
        self.cards = []
        self.development = []
        self.points = 0
        self.cities = 5
        self.settlements = 5
        self.roads = 15
        self.has_longest_road = False
        self.has_biggest_army = False

    def calculate_points(self) -> None:
        pass

    def check_winner(self) -> None:
        pass

    def place_piece(self, type: str, board, location) -> None:
        board.pieces.append([location, self.player_color, type])

    def return_resource_values(self) -> object:
        resources = {
            "sheep": 0,
            "brick": 0, 
            "stone": 0,
            "wheat": 0,
            "wood": 0
        }

        for i in range(len(self.cards)):
            resources[self.cards[i]] += 1

        return resources

    def buy(self, item) -> bool:
        resources = self.return_resource_values()
        if item == "city":
            if resources["stone"] >= 3 and resources["wheat"] >= 2:
                for i in range(3):
                    self.cards.remove("stone")
                for i in range(2):
                    self.cards.remove("wheat")
                return True
        elif item == "settlement":
            if resources["sheep"] >= 1 and resources["wheat"] >= 1 and resources["brick"] >= 1 and resources["wood"] >= 1:
                self.cards.remove("wheat")
                self.cards.remove("sheep")
                self.cards.remove("brick")
                self.cards.remove("wood")
                return True
        elif item == "road":
            if resources["brick"] >= 1 and resources["wood"] >= 1:
                self.cards.remove("brick")
                self.cards.remove("wood")
                return True
        elif item == "dev":
            if resources["sheep"] >= 1 and resources["wheat"] >= 1 and resources["stone"] >= 1:
                self.cards.remove("sheep")
                self.cards.remove("wheat")
                self.cards.remove("stone")
                return True
        else:
            return False

class Board:
    def __init__(self, hex_r_side: int) -> None:

        self.tiles_names = [] #arr len 19 filled with self.types randomly. Assigned in self.assign_tiles
        self.tile_tops = [] #each index is the top point on a hexagon
        self.tiles = []
        self.pieces = [] #list of all pieces on the board

        self.number_indicies = [1, 2, 3, 12, 13, 14, 4, 11, 18, 19, 15, 5, 10, 17, 16, 6, 9, 8, 7]
        self.numbers = ["5", "2", "6", "3", "8", "10", "9", "12", "11", "4", "8", "10", "9", "4", "5", "6", "3", "11"]
        
        self.types = ["sheep", "brick", "rock", "wheat", "wood", "desert"]

        self.radius = hex_r_side # distance from center to a corner
        self.radius_corner = self.radius / math.sqrt(3) # distance from center to the midpoint of a side

        self.init_assets()

    def init_assets(self) -> None:
        road_width = 5
        road_length = 35
        
        city_width = 20
        city_length = 10

        road_points = [(0, 0), (road_width, 0), (road_width, road_length), (0, road_length)]
        city_points = [(0, 0), (city_width / 2, city_length / -2), (city_width, 0), (city_width, city_length), (0, city_length)]

        self.road_red = pygame.Surface((100,100))
        self.road_blue = pygame.Surface((100,100))
        self.road_green = pygame.Surface((100,100))
        self.road_yellow = pygame.Surface((100,100))

        self.city_red = pygame.Surface((100, 100))
        self.city_blue = pygame.Surface((100, 100))
        self.city_green = pygame.Surface((100, 100))
        self.city_yellow = pygame.Surface((100, 100))

        pygame.draw.polygon(self.road_red, (255, 0, 0), road_points)
        pygame.draw.polygon(self.road_blue, (0, 0, 255), road_points)
        pygame.draw.polygon(self.road_green, (0, 255, 0), road_points)
        pygame.draw.polygon(self.road_yellow, (200, 200, 0), road_points)
        
        pygame.draw.polygon(self.city_red, (255, 0, 0), city_points)
        pygame.draw.polygon(self.city_blue, (0, 0, 255), city_points)
        pygame.draw.polygon(self.city_green, (0, 255, 0), city_points)
        pygame.draw.polygon(self.city_yellow, (200, 200, 0), city_points)

    def assign_tile_locations(self) -> None:
        lens = [3, 4, 5, 4, 3]
        for i in range(len(lens)):
            for j in range(lens[i]):
                x_offset = (screen_w - lens[i] * 2 * self.radius) / 2 + j * self.radius * 2 + self.radius
                y_offset = (screen_h - self.radius_corner * 16) / 2  + self.radius_corner * 3 * i
                self.tile_tops.append((x_offset, y_offset))

    def assign_tiles(self) -> None:
        # Create the list with the exact number of each tile type
        self.tiles_names = ['brick'] * 4 + ['wood'] * 4 + ['wheat'] * 4 + ['sheep'] * 3 + ['rock'] * 3 + ['desert'] * 1
        
        # Shuffle the list to ensure randomness
        random.shuffle(self.tiles_names)

    def assign_tile_classes(self) -> None:
        idx = self.tiles_names.index("desert")
        self.numbers.insert(self.number_indicies[idx] - 1, "")
        for i in range(num_tiles):

            top = self.tile_tops[i]

            points = [(top[0], top[1]), 
                  (top[0] + self.radius, top[1] + self.radius_corner), 
                  (top[0] + self.radius, top[1] + self.radius_corner * 3), 
                  (top[0], top[1] + self.radius_corner * 4), 
                  (top[0] - self.radius, top[1] + self.radius_corner * 3), 
                  (top[0] - self.radius, top[1] + self.radius_corner)]
            
            city1 = Node("city", points[0])
            city2 = Node("city", points[1])
            city3 = Node("city", points[2])
            city4 = Node("city", points[3])
            city5 = Node("city", points[4])
            city6 = Node("city", points[5])

            road1 = Node("road", midpoint(points[0], points[1]))
            road2 = Node("road", midpoint(points[1], points[2]))
            road3 = Node("road", midpoint(points[2], points[3]))
            road4 = Node("road", midpoint(points[3], points[4]))
            road5 = Node("road", midpoint(points[4], points[5]))
            road6 = Node("road", midpoint(points[5], points[0]))

            nodes_on_hex = [[city1, city2, city3, city4, city5, city6], [road1, road1, road2, road3, road4, road5, road6]]

            #Find the color of each tile
            if self.tiles_names[i] == "sheep":
                color = (100, 200, 100)
            elif self.tiles_names[i] == "brick":
                color = (200, 100, 50)
            elif self.tiles_names[i] == "rock":
                color = (100, 100, 100)
            elif self.tiles_names[i] == "wheat":
                color = (200, 200, 0)
            elif self.tiles_names[i] == "wood":
                color = (50, 200, 50)
            elif self.tiles_names[i] == "desert":
                color = (100, 100, 0)

            #Find the center of each tile
            center = (top[0], top[1] + self.radius_corner)
            self.tiles.append(Tile(self.tiles_names[i], nodes_on_hex, color, center, self.numbers[self.number_indicies[i] - 1], points))

    """def flatten_nodes(self) -> None:
        i = 0
        while i < len(self.nodes) - 1:
            curr = self.nodes[i].location
            next = self.nodes[i + 1].location

            if curr[0] == next[0] and curr[1] == next[1]:
                # Remove the duplicate node
                self.nodes.pop(i + 1)
            else:
                i += 1  # Only increment if no removal, to avoid skipping"""

    def draw_tiles(self) -> None:
        for i in range(len(self.tiles)):

            self.tiles[i].draw_tile()

            center_x = self.tiles[i].center[0]
            center_y = self.tiles[i].center[1]

            if (self.tiles[i].resource_type != "desert"):
                pygame.draw.circle(screen, (230, 230, 200), (center_x, center_y + self.radius_corner), 20)

            text_surf = game_font.render(self.tiles[i].number, (0, 0), (0, 0, 0))
            screen.blit(text_surf, (center_x - font_size / 2, center_y + font_size / 2))

    #implement rotation and drawing to the screen
    def draw_pieces(self) -> None:
        for i in range(len(self.pieces)):
            if self.pieces[1] == "road":
                if self.pieces[2] == "red":
                    pass
                elif self.pieces[2] == "blue":
                    pass
                elif self.pieces[2] == "yellow":
                    pass
                elif self.pieces[2] == "green":
                    pass
                else:
                    pass
                
            if self.pieces[1] == "city":
                if self.pieces[2] == "red":
                    pass
                elif self.pieces[2] == "blue":
                    pass
                elif self.pieces[2] == "yellow":
                    pass
                elif self.pieces[2] == "green":
                    pass
                else:
                    pass

    def draw_board(self) -> None:
        self.draw_tiles()
        self.draw_pieces()

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
hitbox_w = 10
hitbox_h = 10

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
    play_button = Button("main_menu", (0, 100, 0), "PLAY", [screen_w / 2 - play_b_w / 2, screen_h / 2 - play_b_h / 1.75, play_b_w, play_b_h], "play_button")
    quit_button = Button("main_menu", (100, 0, 0), "QUIT", [screen_w / 2 - play_b_w / 2, screen_h / 2 + play_b_h / 1.75, play_b_w, play_b_h], "quit_button")

    #create game setup buttons

    game_setup_back_button = Button("game_setup", (100, 0, 0), "Back", [screen_w / 4 - play_b_w / 2, screen_h / 2, 200, 100], "game_setup_back_button")

    gsb_w = 150
    gsb_h = 50
    game_start_button = Button("game_setup", (100, 0, 0), "Start", [screen_w / 4 * 3 - gsb_w / 2, screen_h / 8 * 6, gsb_w, gsb_h], "game_start")


    pnidb_size = screen_h / 20
    player_num_increase_button = Button("game_setup", (0, 100, 0), "+", [screen_w / 4 - pnidb_size / 2 + 100, screen_h / 4 * 2.5, pnidb_size, pnidb_size], "player_num_increase_button")
    player_num_decrease_button = Button("game_setup", (0, 100, 0), "-", [screen_w / 4 - pnidb_size / 2 - 100, screen_h / 4 * 2.5, pnidb_size, pnidb_size], "player_num_decrease_button")

    player_choose_color_cycle_button = Button("game_setup", (0, 0, 0), "->", [10, 10, 10, 10], "player_choose_color_cycle_button")

    difficulty_level_easy_button = Button("game_setup", (0, 0, 0), "easy", [10, 10, 10, 10], "difficulty_level_easy_button")
    difficulty_level_medium_button = Button("game_setup", (0, 0, 0), "medium", [10, 10, 10, 10], "difficulty_level_medium_button")
    difficulty_level_hard_button = Button("game_setup", (0, 0, 0), "hard", [10, 10, 10, 10], "difficulty_level_hard_button")

    
    sob_size = screen_w / 12 / 1.5
    sob_offset = screen_h / 24 / 1.5
    settings_menu_button = Button("game_setup", (100, 0, 0), "image", [screen_w - sob_offset - sob_size, sob_offset, sob_size, sob_size], "settings_menu_button")

    #create settings buttons
    settings_frame_rate_increase_button = Button("settings", (0, 0, 0), "->", [10, 10, 10, 10], "settings_frame_rate_increase_button")
    settings_frame_rate_decrease_button = Button("settings", (0, 0, 0), "<-", [10, 10, 10, 10], "settings_frame_rate_decrease_button")
    settings_audio_on_off_button = Button("settings", (0, 0, 0), "on", [10, 10, 10, 10], "settings_audio_on_off_button")

    settings_close_buttons = Button("settings", (100, 0, 0), "X", [], "settings_menu_close_button")

    #create board buttons
    board_buy_settlement_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_settlement_button")
    board_buy_city_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_city_button")
    board_buy_road_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_road_button")
    board_buy_development_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_buy_development_button")
    board_roll_dice_button = Button("board", (0, 0, 0), "image", [10, 10, 10, 10], "board_roll_dice_button")


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
    board = Board(screen_w / 27.32)
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