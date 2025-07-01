from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from city import City
    from disease import Disease
    from game import Game

class CityCard: 
    def __init__(self, city: 'City'):
        self.city = city

class InfectionCard(CityCard):
    def increase_city_disease_quantity(self) -> None:
        self.city.disease_quantity += 1
        self.city.disease.cubes += 1
        print(f"Infection in {self.city.name} increased to {self.city.disease_quantity}. {self.city.disease.color} cubes: {self.city.disease.cubes}")

class PlayerCard():
    "classe base pra player cards"

class CityPlayerCard(CityCard, PlayerCard):
    "classe base pra city player cards"
    

class EpidemicPlayerCard(PlayerCard):
    def increase_infection_level(self, game: 'Game') -> None:
        game.infectionLevel += 1
        print(f"Epidemic! Infection level increased to {game.infectionLevel}")
    

