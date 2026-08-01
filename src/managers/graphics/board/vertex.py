from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.graphics.board.edge import Edge
    from src.managers.graphics.board.tile import Tile

class Vertex:
    def __init__(self, id: str, center: tuple, tile: Tile) -> None:
        self.id = id
        self.center = center
        self.tile = tile
        self.adj_tiles: list[Tile] = [tile]
        self.adj_verts: list[Vertex] = []
        self.adj_edges: list[Edge] = []

    def add_tile(self, tile):
        self.adj_tiles.append(tile)

    def add_edge(self, edge):
        self.adj_edges.append(edge)

    def add_vertex(self, vertex):
        self.adj_verts.append(vertex)

    def __str__(self) -> str:
        return f"Vertex(id={self.id}, num_adj_tiles={len(self.adj_tiles)}, num_adj_verts={len(self.adj_verts)}, num_adj_edges={len(self.adj_edges)})"
