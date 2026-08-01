from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.managers.graphics.board.edge import Edge
from src.managers.graphics.board.vertex import Vertex

if TYPE_CHECKING:
    pass


class Tile:
    def __init__(self, id: int, center: tuple, radius: float, number: int, resource: str, p, q, s):
        self.id = id
        self.center = center
        self.p = p
        self.q = q
        self.s = s
        self.radius = radius
        self.number = number
        self.resource = resource
        self.adj_tiles: list[Tile] = []
        self.adj_edges: list[Edge] = []
        self.adj_verts: list[Vertex] = []

    def create_edges(self, global_edges: list[Edge]):
        for i in range(6):
            edge_center = self._edge_center(i)

            id = f"({round(edge_center[0], 6)},{round(edge_center[1], 6)})"

            for edge in global_edges:
                if edge.id == id:
                    if self not in edge.adj_tiles:
                        edge.add_tile(self)
                    self.adj_edges.append(edge)
                    break
            else:
                new_edge = Edge(id, edge_center, self) # type: ignore
                self.adj_edges.append(new_edge)
                global_edges.append(new_edge)

    def create_verts(self, global_verts: list[Vertex]):
        for i in range(6):
            vert_center = self._vertex_position(i)

            id = f"({round(vert_center[0], 6)},{round(vert_center[1], 6)})"

            for vertex in global_verts:
                if vertex.id == id:
                    self.adj_verts.append(vertex)
                    break
            else:
                new_vertex = Vertex(id, vert_center, self) # type: ignore
                self.adj_verts.append(new_vertex)
                global_verts.append(new_vertex)

    def add_edge(self, edge):
        self.adj_edges.append(edge)

    def add_vertex(self, vertex):
        self.adj_verts.append(vertex)

    def add_neighbor(self, neighbor):
        self.adj_tiles.append(neighbor)

    def _vertex_position(self, idx: int) -> tuple[float, float]:
        angle = math.pi / 3 * idx - math.pi / 2
        return (
            self.center[0] + math.cos(angle) * self.radius,
            self.center[1] + math.sin(angle) * self.radius,
        )

    def _edge_center(self, idx: int) -> tuple[float, float]:
        v1 = self._vertex_position(idx)
        v2 = self._vertex_position((idx + 1) % 6)

        return (
            (v1[0] + v2[0]) / 2.0,
            (v1[1] + v2[1]) / 2.0,
        )

    def populate_edge_to_edge_neighbors(self):
        for i in range(6):
            right_neighbor = self.adj_edges[(i + 1) % 6]
            if right_neighbor not in self.adj_edges[i].adj_edges:
                self.adj_edges[i].add_edge(right_neighbor)

            left_neighbor = self.adj_edges[(i - 1) % 6]
            if left_neighbor not in self.adj_edges[i].adj_edges:
                self.adj_edges[i].add_edge(left_neighbor)

    def populate_vert_to_vert_neighbors(self):
        for i in range(6):
            right_neighbor = self.adj_verts[(i + 1) % 6]
            if right_neighbor not in self.adj_verts[i].adj_verts:
                self.adj_verts[i].add_vertex(right_neighbor)

            left_neighbor = self.adj_verts[(i - 1) % 6]
            if left_neighbor not in self.adj_verts[i].adj_verts:
                self.adj_verts[i].add_vertex(left_neighbor)

    def populate_vert_to_edge_neighbors(self):
        for i in range(6):
            right_edge_neighbor = self.adj_edges[i]
            if right_edge_neighbor not in self.adj_verts[i].adj_edges:
                self.adj_verts[i].add_edge(right_edge_neighbor)
            
            left_edge_neighbor = self.adj_edges[(i - 1) % 6]
            if left_edge_neighbor not in self.adj_verts[i].adj_edges:
                self.adj_verts[i].add_edge(left_edge_neighbor)

    def populate_edge_to_vert_neighbors(self):
        for i in range(6):
            right_vertex_neighbor = self.adj_verts[(i+1) % 6]
            if right_vertex_neighbor not in self.adj_edges[i].adj_verts:
                self.adj_edges[i].add_vertex(right_vertex_neighbor)

            left_vertex_neighbor = self.adj_verts[i]
            if left_vertex_neighbor not in self.adj_edges[i].adj_verts:
                self.adj_edges[i].add_vertex(left_vertex_neighbor)

    def populate_edge_to_tile_neighbors(self):
        for edge in self.adj_edges:
            if self not in edge.adj_tiles:
                edge.adj_tiles.append(self) #type: ignore

            for tile in edge.adj_tiles:
                if tile is not self and tile not in self.adj_tiles:
                    self.adj_tiles.append(tile) #type: ignore

    def populate_vert_to_tile_neighbors(self):
        for vertex in self.adj_verts:
            if self not in vertex.adj_tiles:
                vertex.adj_tiles.append(self) #type: ignore


    def __str__(self) -> str:
        return f"Tile(id={self.id}, pos=({self.p}, {self.q}, {self.s}), num_tiles={len(self.adj_tiles)})"
