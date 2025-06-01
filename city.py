from disease import Disease
from typing import Tuple

class City:
    def __init__(self, name: str, coordinates: Tuple[int, int], disease: Disease):
        self.name = name
        self.coordinates = coordinates
        self.disease = disease
        self.disease_quantity = 0
        self.neighbors: list['City'] = []
        self.has_center = False
    
    def setNeighbors(self, neighbors: list['City']):
        self.neighbors = neighbors
    
    def setCenter(self):
        self.has_center = True