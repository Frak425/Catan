from src.managers.base_manager import BaseManager
from src.managers.player.player import Player

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
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
        
    def init(self, player_list: list):
        self.players: list[Player] = []
        for idx, maybe_player in enumerate(player_list):
            if isinstance(maybe_player, Player):
                self.players.append(maybe_player)
            elif isinstance(maybe_player, dict):
                self.players.append(
                    Player(
                        player_id=maybe_player.get("player_id", idx + 1),
                        name=maybe_player.get("name", f"Player {idx + 1}"),
                        color=maybe_player.get("color", "red"),
                        resources=maybe_player.get("resources", {}),
                        victory_points=int(maybe_player.get("victory_points", maybe_player.get("points", 0))),
                    )
                )
        self.current_turn = 0
        self.new_game_settings: dict[str, Any] = {}

    def create_players(self, count: int | None = None, colors: list[str] | None = None, names: list[str] | None = None) -> list[Player]:
        """Create a fresh player list from setup values or provided overrides."""
        if count is None:
            count = int(getattr(self.game_manager, 'players_num', 2))
        count = max(1, int(count))

        if colors is None:
            colors = list(getattr(self.game_manager, 'player_colors', ["red", "blue", "green", "yellow"]))

        if names is None:
            names = [f"Player {i + 1}" for i in range(count)]

        players: list[Player] = []
        for i in range(count):
            color = colors[i % len(colors)]
            name = names[i] if i < len(names) else f"Player {i + 1}"
            players.append(
                Player(
                    player_id=i + 1,
                    name=name,
                    color=color,
                )
            )

        self.players = players
        self.current_turn = 0
        return self.players

    def configure_new_game(self, setup_settings: dict[str, Any] | None = None) -> dict[str, Any]:
        """Capture and normalize setup settings for a new game."""
        if setup_settings is None:
            collector = getattr(self.game_manager, 'collect_setup_game_settings', None)
            candidate = collector() if callable(collector) else {}
            if isinstance(candidate, dict):
                setup_settings = candidate
            else:
                setup_settings = {}

        settings: dict[str, Any] = {}
        for key, value in setup_settings.items():
            settings[str(key)] = value
        settings.setdefault('players_num', int(getattr(self.game_manager, 'players_num', 2)))
        settings.setdefault('difficulty', getattr(self.game_manager, 'game_difficulty', 'easy'))
        settings.setdefault('points_to_win', int(getattr(self.game_manager, 'points_to_win', 10)))
        settings.setdefault('turn_order', int(getattr(self.game_manager, 'turn_order', 1)))

        self.new_game_settings = settings
        return settings

    def begin_new_game(self, setup_settings: dict[str, Any] | None = None) -> list[Player]:
        """Configure settings, create players, and position current turn."""
        settings = self.configure_new_game(setup_settings)

        # Keep game_manager values in sync with collected setup values.
        self.game_manager.players_num = int(settings.get('players_num', self.game_manager.players_num))
        self.game_manager.game_difficulty = str(settings.get('difficulty', self.game_manager.game_difficulty))
        self.game_manager.points_to_win = int(settings.get('points_to_win', self.game_manager.points_to_win))
        self.game_manager.turn_order = int(settings.get('turn_order', self.game_manager.turn_order))

        players = self.create_players(count=int(settings.get('players_num', self.game_manager.players_num)))

        # Turn order is 1-based in setup UI.
        if players:
            self.current_turn = (self.game_manager.turn_order - 1) % len(players)
        else:
            self.current_turn = 0

        return players

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
            if player.name == player_name:
                return player
        return None

    def get_player_resources(self, player_name: str) -> object:
        """Returns the specified player's resources"""
        player = self.get_player(player_name)
        return dict(player.resources) if player else None

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
            player.points = player.points + amount

        elif action == 'set_points':
            value = int(args[1]) if len(args) > 1 else player.points
            player.points = value

    def check_winner(self):
        points_to_win = int(getattr(self.game_manager, 'points_to_win', 10))
        for player in self.players:
            if player.points >= points_to_win:
                return player

        return None