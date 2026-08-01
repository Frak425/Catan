from __future__ import annotations

import random

from src.managers.base_manager import BaseManager
from src.managers.player.player import Player, PlayerInfo

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from src.managers.game.game_manager import GameConfig
    from src.managers.game.game_manager import GameManager
    from src.managers.input.input_manager import InputManager
    from src.managers.helper.helper_manager import HelperManager
    from src.managers.audio.audio_manager import AudioManager
    from src.managers.graphics.graphics_manager import GraphicsManager

class PlayerManager(BaseManager):
    def __init__(self):
        super().__init__()
        
    def import_dependencies(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.game_manager = self.get_dependency('game_manager')
        self.input_manager = self.get_dependency('input_manager')
        self.helper_manager = self.get_dependency('helper_manager')
        self.audio_manager = self.get_dependency('audio_manager')
        self.graphics_manager = self.get_dependency('graphics_manager')

    def create_players(self, player_configs: list[PlayerInfo]) -> list[Player]:
        """Create a fresh player list from setup values or provided overrides."""
        players: list[Player] = []
        for i in range(len(player_configs)):
            players.append(
                Player(
                    player_id=i + 1,
                    player_config=player_configs[i]
                )
            )

        self.players = players
        self.current_turn = 0
        return self.players

    def create_random_names(self, num_players: int) -> list[str]:
        ADJECTIVES = [
    "Able", "Agile", "Amber", "Ancient", "Ardent",
    "Balanced", "Bold", "Brave", "Bright", "Brisk",
    "Calm", "Careful", "Cheerful", "Clever", "Coastal",
    "Cordial", "Crafty", "Curious", "Daring", "Deep",
    "Diligent", "Durable", "Earnest", "Easygoing", "Elegant",
    "Emerald", "Faithful", "Fearless", "Festive", "Fierce",
    "Friendly", "Gentle", "Golden", "Graceful", "Grand",
    "Green", "Hardy", "Helpful", "Honest", "Hopeful",
    "Humble", "Independent", "Ingenious", "Jolly", "Joyful",
    "Kind", "Lively", "Loyal", "Lucky", "Majestic",
    "Merry", "Mighty", "Misty", "Nimble", "Noble",
    "Patient", "Peaceful", "Playful", "Pleasant", "Polished",
    "Prosperous", "Prudent", "Quick", "Quiet", "Radiant",
    "Reliable", "Resolute", "Resourceful", "Robust", "Rustic",
    "Sandy", "Serene", "Sharp", "Shining", "Silent",
    "Silver", "Skilled", "Solid", "Speedy", "Spry",
    "Steady", "Stout", "Sturdy", "Sunny", "Swift",
    "Thoughtful", "Thriving", "Timber", "Tranquil", "True",
    "Valiant", "Vast", "Vibrant", "Vigorous", "Warm",
    "Watchful", "Wholesome", "Wild", "Wise", "Zealous"
]
        ANIMALS = [
    "Badger", "Bear", "Beaver", "Bison", "Boar",
    "Buck", "Buffalo", "Cougar", "Crane", "Crow",
    "Deer", "Dove", "Duck", "Eagle", "Falcon",
    "Finch", "Fox", "Goat", "Goose", "Hare",
    "Hawk", "Heron", "Horse", "Lark", "Lynx",
    "Moose", "Otter", "Owl", "Pheasant", "Puma",
    "Quail", "Rabbit", "Raven", "Robin", "Salmon",
    "Seal", "Sheep", "Sparrow", "Squirrel", "Stag",
    "Swan", "Thrush", "Trout", "Turtle", "Weasel",
    "Whale", "Wildcat", "Wolf", "Wren", "Yak"
]
        PROFESSIONS = [
    "Artisan", "Baker", "Blacksmith", "Builder", "Carpenter",
    "Cartographer", "Craftsman", "Farmer", "Fisher",
    "Forester", "Gardener", "Harbormaster", "Hunter",
    "Innkeeper", "Mason", "Merchant", "Miller",
    "Miner", "Navigator", "Pioneer", "Potter",
    "Sailor", "Scout", "Settler", "Shepherd",
    "Stonecutter", "Trader", "Wagoner", "Weaver",
    "Woodworker"
]
        COLORS = [
    "Amber", "Auburn", "Azure", "Beige", "Black",
    "Blue", "Bronze", "Brown", "Burgundy", "Charcoal",
    "Copper", "Coral", "Crimson", "Cream", "Emerald",
    "Forest", "Gold", "Golden", "Gray", "Green",
    "Honey", "Indigo", "Ivory", "Jade", "Lavender",
    "Lilac", "Lime", "Mahogany", "Maroon", "Moss",
    "Navy", "Oak", "Ochre", "Olive", "Pearl",
    "Pine", "Plum", "Rose", "Ruby", "Rust",
    "Saffron", "Sage", "Sand", "Scarlet", "Silver",
    "Slate", "Snow", "Teal", "Umber", "Violet"
]
        PLANTS = [
    "Ash", "Aspen", "Barley", "Beech", "Birch",
    "Cedar", "Cherry", "Chestnut", "Clover", "Cypress",
    "Daisy", "Elm", "Fern", "Fir", "Flax",
    "Heather", "Hazel", "Holly", "Ivy", "Juniper",
    "Laurel", "Lavender", "Lily", "Maple", "Moss",
    "Oak", "Olive", "Orchid", "Pine", "Poppy",
    "Reed", "Rose", "Rowan", "Rye", "Sage",
    "Spruce", "Sunflower", "Sycamore", "Thistle", "Tulip",
    "Violet", "Walnut", "Wheat", "Willow", "Yarrow",
    "Yew", "Cattail", "Alder", "Bamboo", "Hemlock"
]

        names = []
        #3 different name formats
        name_format_1 = (ADJECTIVES, ANIMALS)
        name_format_2 = (ADJECTIVES, PROFESSIONS)
        name_format_3 = (COLORS, PLANTS)

        for _ in range(num_players):
            format = random.choice([name_format_1, name_format_2, name_format_3])
            name = f"{random.choice(format[0])} {random.choice(format[1])}"
            if name not in names:
                names.append(name)

        return names

    def get_available_colors(self, player_color: str) -> list[str]:
        all_colors = ["red", "blue", "green", "yellow"]  # Example colors, replace with actual available colors
        return [color for color in all_colors if color not in player_color]

    def next_turn(self) -> None:
        """Moves turn to the next player"""
        if not self.players:
            self.current_turn = 0
            return
        self.current_turn = (self.current_turn + 1) % len(self.players)

    def current_player(self):
        """Return a reference to the current player"""
        if not self.players:
            return None
        return self.players[self.current_turn]

    def get_player(self, player_name: str) -> Player | None:
        """Get a player by exact name."""
        for player in self.players:
            if player.config.name == player_name:
                return player
        return None

    def get_player_resources(self, player_name: str) -> object:
        """Returns the specified player's resources"""
        player = self.get_player(player_name)
        return dict(player.config.resources) if player else None

    def perform_action(self, action: str, *args) -> None:
        """Perform a basic player mutation action.

        Supported actions:
        - gain_resource(player_name, resource, amount=1)
        - spend_resource(player_name, resource, amount=1)
        - gain_resources(player_name, {resource: amount, ...})
        - spend_resources(player_name, {resource: amount, ...})
        - add_points(player_name, amount=1)
        - set_points(player_name, value)
        """
        if not args:
            return

        player_name = args[0]
        player = self.get_player(player_name)
        if player is None:
            return

        if action == 'gain_resource':
            resource = str(args[1])
            amount = int(args[2]) if len(args) > 2 else 1
            player.add_resource(resource, amount)

        elif action == 'spend_resource':
            resource = str(args[1])
            amount = int(args[2]) if len(args) > 2 else 1
            player.remove_resource(resource, amount)

        elif action == 'gain_resources':
            payload = args[1] if len(args) > 1 and isinstance(args[1], dict) else {}
            player.grant_resources(payload)

        elif action == 'spend_resources':
            payload = args[1] if len(args) > 1 and isinstance(args[1], dict) else {}
            player.spend_resources(payload)

        elif action == 'add_points':
            amount = int(args[1]) if len(args) > 1 else 1
            player.config.victory_points = player.config.victory_points + amount

        elif action == 'set_points':
            value = int(args[1]) if len(args) > 1 else player.config.victory_points
            player.config.victory_points = value
    
    def check_winner(self):
        points_to_win = int(getattr(self.game_manager, 'points_to_win', 10))
        for player in self.players:
            if player.config.victory_points >= points_to_win:
                return player

        return None
    