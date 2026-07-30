from __future__ import annotations

from dataclasses import dataclass, field, fields

from src.managers.helper.constants import Constants


@dataclass
class Player:
    """Represents a single player and their core game state."""

    def __init__(self, player_id: int, player_config: PlayerInfo):
        field_names = {f.name for f in fields(PlayerInfo)}
        self.config = PlayerInfo(**{k: v for k, v in player_config.__dict__.items() if k in field_names})

    def has_resources(self, cost: dict[str, int]) -> bool:
        """Return True when player can afford every resource in `cost`."""
        for resource, amount in cost.items():
            if self.config.resources.get(resource, 0) < int(amount):
                return False
        return True

    def add_resource(self, resource: str, amount: int = 1) -> None:
        """Add resource amount (clamped to non-negative input)."""
        amount = max(0, int(amount))
        self.config.resources[resource] = self.config.resources.get(resource, 0) + amount

    def remove_resource(self, resource: str, amount: int = 1) -> bool:
        """Attempt to remove resource amount. Returns False if insufficient."""
        amount = max(0, int(amount))
        current = self.config.resources.get(resource, 0)
        if current < amount:
            return False
        self.config.resources[resource] = current - amount
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
            player_id=self.config.player_id,
            name=self.config.name,
            color=self.config.color,
            resources=dict(self.config.resources),
            victory_points=self.config.victory_points,
            roads_built=self.config.roads_built,
            settlements_built=self.config.settlements_built,
            cities_built=self.config.cities_built,
            development_cards=self.config.development_cards,
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
    development_cards: list[str]