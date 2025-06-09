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
        self.in_outbreak = False  # Flag to prevent infinite loops
    
    def setNeighbors(self, neighbors: list['City']):
        self.neighbors = neighbors
    
    def setCenter(self):
        self.has_center = True
        
    def outbreak(self, game):
        if self.in_outbreak:
            return  
            
        self.in_outbreak = True
        game.board.show_message(f"Outbreak in {self.name}")
        
        neighbors_to_infect = list(self.neighbors)
        for neighbor in neighbors_to_infect:
            neighbor.infect(game)
            
        game.outbreaks += 1
        self.in_outbreak = False
        
    def infect(self, game):
        if self.disease_quantity >= 3 and not self.in_outbreak:
            self.outbreak(game)
            return
        elif self.disease_quantity < 3:
            self.disease_quantity += 1
            self.disease.cubes += 1
