from __future__ import annotations

import math
import pygame


screen_x = 1000
screen_y = 1000
global_radius = 100

vert_id_counter = 0
edge_id_counter = 0

directions = [(+1, -1, 0),
              (+1, 0, -1),
              (0, +1, -1),
              (-1, +1, 0),
              (-1, 0, +1),
              (0, -1, +1)]

tiles: list[Tile] = []
verts: list[Vertex] = []
edges: list[Edge] = []

def main():
    pygame.init()
    screen_info = pygame.display.Info()

    screen_w = min(screen_info.current_w, screen_x)
    screen_h = min(screen_info.current_h, screen_y)

    center = (screen_w // 2, screen_h // 2)

    seed_tile = Tile(0, center, global_radius, 0, "test", 0, 0, 0)
    tiles.append(seed_tile)


    seed_tile.create_verts()
    seed_tile.create_edges()

    create_tiles(seed_tile)
    print_items(tiles, edges, verts)
    visualize_graph(screen_w, screen_h)


def create_tiles(center_tile: Tile):
    #first ring

    create_ring_tiles(center_tile)

    #second ring
    """first_ring: list[Tile] = tiles[1:7]
    for tile in first_ring:
        create_ring_tiles(tile)"""


    #populate edge, vertex, and tile neighbors after all initialized
    for tile in tiles:
        tile.populate_edge_to_edge_neighbors()
        tile.populate_vert_to_vert_neighbors()
        tile.populate_edge_to_vert_neighbors()
        tile.populate_vert_to_edge_neighbors()
        tile.populate_edge_to_tile_neighbors()
        tile.populate_vert_to_tile_neighbors()
        
def create_ring_tiles(center_tile: Tile):
    for direction in directions:
        #if tile already exists
        for tile in tiles:
            if (direction[0] + center_tile.p, direction[1] + center_tile.q, direction[2] + center_tile.s) == (tile.p, tile.q, tile.s):
                break
        else: # else create new tile in that direction
            new_center_x = center_tile.center[0] + global_radius * math.sqrt(3) * (center_tile.p + direction[0] + (center_tile.q + direction[2]) / 2)
            new_center_y = center_tile.center[1] + global_radius * 3/2 * (center_tile.p + direction[2])
            new_tile = Tile(len(tiles), (new_center_x, new_center_y), global_radius, len(tiles), "test", center_tile.p + direction[0], center_tile.q + direction[1], center_tile.s + direction[2])
            
            tiles.append(new_tile)
            new_tile.create_verts()
            new_tile.create_edges()


def visualize_graph(screen_w: int, screen_h: int):
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Catan Graph")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill((20, 20, 20))

        for tile in tiles:
            pygame.draw.circle(screen, (255, 255, 255), (int(tile.center[0]), int(tile.center[1])), 2)

        for edge in edges:
            pygame.draw.circle(screen, (0, 255, 120), (int(edge.center[0]), int(edge.center[1])), 3)

        for vertex in verts:
            pygame.draw.circle(screen, (0, 120, 255), (int(vertex.center[0]), int(vertex.center[1])), 4)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def print_items(tiles_list: list[Tile], edges_list: list[Edge], verts_list: list[Vertex]):
    """for tile in tiles_list:
        print(tile.__str__())"""
    
    for edge in edges_list:
        print(edge.__str__())

    for vertex in verts_list:
        print(vertex.__str__())

# --- CLASSES --- #
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

    def create_edges(self):
        for i in range(6):
            edge_x = self.center[0] + math.cos(math.pi / 3 * (-i+2)) * self.radius
            edge_y = self.center[1] + math.sin(math.pi / 3 * (-i+2)) * self.radius
            edge_center = (edge_x, edge_y)

            id = f"({math.floor(edge_x)},{math.floor(edge_y)})"

            if len(edges) == 0:
                new_edge = Edge(id, edge_center, self)
                self.adj_edges.append(new_edge)
                edges.append(new_edge)
                
            else:
                for edge in edges:
                    if edge.id == id:
                        self.adj_edges.append(edge)
                        break
                else:
                    new_edge = Edge(id, edge_center, self)
                    self.adj_edges.append(new_edge)
                    edges.append(new_edge)

    def create_verts(self):
        for i in range(6):
            vert_x = self.center[0] + math.cos(math.pi / 3 * (-i+2)) * self.radius
            vert_y = self.center[1] + math.sin(math.pi / 3 * (-i+2)) * self.radius
            vert_center = (vert_x, vert_y)

            id = f"({math.floor(vert_x)},{math.floor(vert_y)})"

            for vertex in verts:
                if vertex.id == id:
                    self.adj_verts.append(vertex)
                    break
            else:
                new_vertex = Vertex(id, vert_center, self)
                self.adj_verts.append(new_vertex)
                verts.append(new_vertex)

    def add_edge(self, edge):
        self.adj_edges.append(edge)

    def add_vertex(self, vertex):
        self.adj_verts.append(vertex)

    def add_neighbor(self, neighbor):
        self.adj_tiles.append(neighbor)

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
                edge.adj_tiles.append(self)

    def populate_vert_to_tile_neighbors(self):
        for vertex in self.adj_verts:
            if self not in vertex.adj_tiles:
                vertex.adj_tiles.append(self)


    def __str__(self) -> str:
        return f"Tile(id={self.id}, pos=({self.p}, {self.q}, {self.s}), num_tiles={len(self.adj_tiles)})"

class Edge:
    def __init__(self, id: str, center: tuple, tile1: Tile):
        self.id = id
        self.center = center
        self.adj_tiles = [tile1]
        self.adj_verts = []
        self.adj_edges = []

    def add_tile(self, tile):
        self.adj_tiles.append(tile)

    def add_edge(self, edge):
        self.adj_edges.append(edge)

    def add_vertex(self, vertex):
        self.adj_verts.append(vertex)

    def __str__(self) -> str:
        return f"Edge(id={self.id}, num_adj_tiles={len(self.adj_tiles)}, num_adj_verts={len(self.adj_verts)}, num_adj_edges={len(self.adj_edges)}"

class Vertex:
    def __init__(self, id: str, center: tuple, tile: Tile) -> None:
        self.id = id
        self.center = center
        self.tile = tile
        self.adj_tiles = [tile]
        self.adj_verts = []
        self.adj_edges = []

    def add_tile(self, tile):
        self.adj_tiles.append(tile)

    def add_edge(self, edge):
        self.adj_edges.append(edge)

    def add_vertex(self, vertex):
        self.adj_verts.append(vertex)

    def __str__(self) -> str:
        return f"Vertex(id={self.id}, num_adj_tiles={len(self.adj_tiles)}, num_adj_verts={len(self.adj_verts)}, num_adj_edges={len(self.adj_edges)}"


if __name__ == "__main__":
    main()