from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Player:
    """Represents a single player and their core game state."""

    def __init__(self, player_id: int, player_config: PlayerInfo):
        field_names = {f.name for f in fields(PlayerInfo)}
        self.layout = PlayerInfo(**{k: v for k, v in layout.items() if k in field_names})

    def __post_init__(self) -> None:
        #TODO: Does this need to be here?
        default_resources = {
            "wood": 0,
            "brick": 0,
            "sheep": 0,
            "wheat": 0,
            "ore": 0,
        }

        merged_resources = default_resources.copy()
        merged_resources.update(self.resources)
        self.resources = merged_resources

    @property
    def points(self) -> int:
        """Backward-compatible alias for existing code paths using `player.points`."""
        return self.victory_points

    @points.setter
    def points(self, value: int) -> None:
        self.victory_points = int(value)

    def has_resources(self, cost: dict[str, int]) -> bool:
        """Return True when player can afford every resource in `cost`."""
        for resource, amount in cost.items():
            if self.resources.get(resource, 0) < int(amount):
                return False
        return True

    def add_resource(self, resource: str, amount: int = 1) -> None:
        """Add resource amount (clamped to non-negative input)."""
        amount = max(0, int(amount))
        self.resources[resource] = self.resources.get(resource, 0) + amount

    def remove_resource(self, resource: str, amount: int = 1) -> bool:
        """Attempt to remove resource amount. Returns False if insufficient."""
        amount = max(0, int(amount))
        current = self.resources.get(resource, 0)
        if current < amount:
            return False
        self.resources[resource] = current - amount
        return True

    def spend_resources(self, cost: dict[str, int]) -> bool:
        """Spend multiple resources atomically. Returns False if unaffordable."""
        if not self.has_resources(cost):
            return False
        for resource, amount in cost.items():
            self.remove_resource(resource, int(amount))
        return True

    def grant_resources(self, payload: dict[str, int]) -> None:
        """Grant multiple resources."""
        for resource, amount in payload.items():
            self.add_resource(resource, int(amount))

    def to_dict(self) -> PlayerInfo:
        """Serialize to plain dictionary."""
        return PlayerInfo(
            player_id=self.player_id,
            name=self.player_config.name,
            color=self.player_config.color,
            resources=dict(self.resources),
            victory_points=self.victory_points,
            roads_built=self.roads_built,
            settlements_built=self.settlements_built,
            cities_built=self.cities_built,
            development_cards=self.development_cards,
        )


@dataclass
class PlayerInfo:
    player_id: int
    name: str
    color: str
    resources: dict[str, int]
    victory_points: int
    roads_built: int
    settlements_built: int
    cities_built: int
    development_cards: int