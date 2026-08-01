from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.graphics.board.vertex import Vertex
    from src.managers.graphics.board.tile import Tile

class Edge:
    def __init__(self, id: str, center: tuple, tile1: "Tile"):
        self.id = id
        self.center = center
        self.adj_tiles: list[Tile] = [tile1]
        self.adj_verts: list[Vertex] = []
        self.adj_edges: list[Edge] = []

    def add_tile(self, tile):
        self.adj_tiles.append(tile)

    def add_edge(self, edge):
        self.adj_edges.append(edge)

    def add_vertex(self, vertex):
        self.adj_verts.append(vertex)

    def __str__(self) -> str:
        return f"Edge(id={self.id}, num_adj_tiles={len(self.adj_tiles)}, num_adj_verts={len(self.adj_verts)}, num_adj_edges={len(self.adj_edges)})"
