from attr import dataclass


@dataclass
class GameConfig:
    players_num: int = 4
    player_color: str = ""
    difficulty: str = ""
    points_to_win: int = 10
    dice_mode: str = ""
    robber_mode: str = "friendly"
    turn_order: int = 1
    time_limit_enabled: bool = False
    time_limit_seconds: int = 60

@dataclass
class PlayerConfig:
    name: str
    color: str