from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from city import City

if TYPE_CHECKING:
    from player import Player

class Command(ABC):
    """Abstract command interface for game actions."""
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command. Returns True if successful, False otherwise."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass

class MoveCommand(Command):
    """Command to move a player to a new city."""
    
    def __init__(self, player: 'Player', new_city: City):
        self.player = player
        self.new_city = new_city
        self.previous_city: Optional[City] = None
    
    def execute(self) -> bool:
        self.previous_city = self.player.city
        self.player.city = self.new_city
        return True
    
    def undo(self) -> None:
        if self.previous_city:
            self.player.city = self.previous_city

class TreatDiseaseCommand(Command):
    """Command to treat disease in the player's current city."""
    
    def __init__(self, player: 'Player'):
        self.player = player
        self.treated = False
    
    def execute(self) -> bool:
        if self.player.city.disease_quantity > 0:
            self.player.city.disease_quantity -= 1
            self.treated = True
            return True
        return False
    
    def undo(self) -> None:
        if self.treated:
            self.player.city.disease_quantity += 1

class BuildCenterCommand(Command):
    """Command to build a research center in the player's current city."""
    
    def __init__(self, player: 'Player'):
        self.player = player
        self.was_built = False
    
    def execute(self) -> bool:
        if not self.player.city.has_center:
            self.player.city.has_center = True
            self.was_built = True
            return True
        return False
    
    def undo(self) -> None:
        if self.was_built:
            self.player.city.has_center = False

class FindCureCommand(Command):
    """Command to find a cure for the disease in the player's current city."""
    
    def __init__(self, player: 'Player'):
        self.player = player
        self.had_cure = False
    
    def execute(self) -> bool:
        self.had_cure = self.player.city.disease.has_cure
        self.player.city.disease.has_cure = True
        return True
    
    def undo(self) -> None:
        if not self.had_cure:
            self.player.city.disease.has_cure = False
