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
board_center: tuple[float, float] = (0.0, 0.0)

def main():
    global board_center
    pygame.init()
    screen_info = pygame.display.Info()

    screen_w = min(screen_info.current_w, screen_x)
    screen_h = min(screen_info.current_h, screen_y)

    center = (screen_w // 2, screen_h // 2)
    board_center = center

    seed_tile = Tile(0, center, global_radius, 0, "test", 0, 0, 0)
    tiles.append(seed_tile)


    seed_tile.create_verts()
    seed_tile.create_edges()

    create_tiles(seed_tile)
    print_items(tiles, edges, verts)
    print(f"len(tiles): {len(tiles)}, len(edges): {len(edges)}, len(verts): {len(verts)}")
    visualize_graph(screen_w, screen_h)

def create_tiles(center_tile: Tile):
    #first ring

    create_ring_tiles(center_tile)

    #second ring
    first_ring: list[Tile] = tiles[1:7]
    for tile in first_ring:
        create_ring_tiles(tile)


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
            new_p = center_tile.p + direction[0]
            new_q = center_tile.q + direction[1]
            new_s = center_tile.s + direction[2]

            new_center_x = board_center[0] + global_radius * math.sqrt(3) * (new_p + new_s / 2)
            new_center_y = board_center[1] + global_radius * 3 / 2 * new_s

            new_tile = Tile(len(tiles), (new_center_x, new_center_y), global_radius, len(tiles), "test", new_p, new_q, new_s)
            
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
            polygon_points = [tile._vertex_position(i) for i in range(6)]
            pygame.draw.polygon(screen, (50, 50, 50), polygon_points)
            pygame.draw.polygon(screen, (110, 110, 110), polygon_points, 1)

            for i in range(6):
                edge_start = tile._vertex_position(i)
                edge_end = tile._vertex_position((i + 1) % 6)
                pygame.draw.aaline(screen, (80, 80, 80), edge_start, edge_end)

        for edge in edges:
            pygame.draw.circle(screen, (0, 255, 120), (int(edge.center[0]), int(edge.center[1])), 4)

        for vertex in verts:
            pygame.draw.circle(screen, (0, 120, 255), (int(vertex.center[0]), int(vertex.center[1])), 5)

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
            edge_center = self._edge_center(i)

            id = f"({round(edge_center[0], 6)},{round(edge_center[1], 6)})"

            for edge in edges:
                if edge.id == id:
                    if self not in edge.adj_tiles:
                        edge.add_tile(self)
                    self.adj_edges.append(edge)
                    break
            else:
                new_edge = Edge(id, edge_center, self)
                self.adj_edges.append(new_edge)
                edges.append(new_edge)

    def create_verts(self):
        for i in range(6):
            vert_center = self._vertex_position(i)

            id = f"({round(vert_center[0], 6)},{round(vert_center[1], 6)})"

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
                edge.adj_tiles.append(self)

            for tile in edge.adj_tiles:
                if tile is not self and tile not in self.adj_tiles:
                    self.adj_tiles.append(tile)

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
        return f"Edge(id={self.id}, num_adj_tiles={len(self.adj_tiles)}, num_adj_verts={len(self.adj_verts)}, num_adj_edges={len(self.adj_edges)})"

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
        return f"Vertex(id={self.id}, num_adj_tiles={len(self.adj_tiles)}, num_adj_verts={len(self.adj_verts)}, num_adj_edges={len(self.adj_edges)})"


if __name__ == "__main__":
    main()