from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from city import City
    from disease import Disease
    from game import Game

class CityCard:
    """Base class for all city-related cards."""
    
    def __init__(self, city: 'City'):
        """Initialize a city card.
        
        Args:
            city: The city this card represents.
        """
        self.city = city

class InfectionCard(CityCard):
    """Infection card that can increase disease quantity in a city."""
    
    def increase_city_disease_quantity(self) -> None:
        """Increase the disease quantity in the specified city by one and add a cube to the disease."""
        self.city.disease_quantity += 1
        self.city.disease.cubes += 1
        print(f"Infection in {self.city.name} increased to {self.city.disease_quantity}. {self.city.disease.color} cubes: {self.city.disease.cubes}")

class PlayerCard():
    """Base class for all player cards."""


class CityPlayerCard(CityCard, PlayerCard):
    """Player card representing a city that can be used for movement or other player actions."""
    

class EpidemicPlayerCard(PlayerCard):
    """Epidemic card that increases the infection level when played."""
    
    def increase_infection_level(self, game: 'Game') -> None:
        """Increase the infection level in the game by one."""
        game.infectionLevel += 1
        print(f"Epidemic! Infection level increased to {game.infectionLevel}")
    

