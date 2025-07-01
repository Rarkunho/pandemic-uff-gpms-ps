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
        
    def outbreak(self, game):
        if self.name in game.infected_cities_this_turn:
            print(f"DEBUG: City {self.name} already infected this turn - skipping outbreak")
            return
        
        print(f"DEBUG: Outbreak in {self.name} - current outbreak count: {game.outbreaks}")
        game.board.show_message(f"Outbreak in {self.name}")
        
        game.infected_cities_this_turn.add(self.name)
        
        print(f"DEBUG: {self.name} has {len(self.neighbors)} neighbors")
        neighbors_to_infect = list(self.neighbors)
        for neighbor in neighbors_to_infect:
            print(f"DEBUG: Attempting to infect neighbor: {neighbor.name}")
            neighbor.infect(game)
            
        game.outbreaks += 1
        print(f"DEBUG: Total outbreaks after this outbreak: {game.outbreaks}")
        
    def infect(self, game):
        print(f"DEBUG: Infection attempt in {self.name} - current quantity: {self.disease_quantity}")
        
        if self.disease_quantity >= 3:
            print(f"DEBUG: {self.name} has 3 cubes - triggering outbreak")
            self.outbreak(game)
            return
        elif self.disease_quantity < 3:
            self.disease_quantity += 1
            self.disease.cubes += 1
            print(f"DEBUG: {self.name} infected - new quantity: {self.disease_quantity}")
