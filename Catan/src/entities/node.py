import pygame
import math
import random

class Node:
    def __init__(self, id: str, location: tuple):
        hitbox_w = 10
        hitbox_h = 10
        self.id = id  # unique identifier for the type (road or city)
        self.adjacent = []  # list of adjacent nodes (connected by roads). Not provided on init
        self.tiles = []  # list of adjacent tiles. Only defined if self.id == "city"
        self.location = location #(x, y) coordinates of each node
        self.rect = [self.location[0] - hitbox_w / 2, self.location[1] - hitbox_h / 2, hitbox_w, hitbox_h]

    def add_adjacent(self, nodes):
        self.adjacent = nodes