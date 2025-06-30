from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from city import City

if TYPE_CHECKING:
    from player import Player

class Command(ABC):
    
    @abstractmethod
    def execute(self) -> bool:
        pass
    
    @abstractmethod
    def undo(self) -> None:
        pass

class MoveCommand(Command):
    def __init__(self, player: 'Player', new_city: City):
        self.player = player
        self.new_city = new_city
        self.previous_city: Optional[City] = None
    
    def execute(self) -> bool:
        if self.new_city in self.player.city.neighbors or self.new_city.has_center:
            self.previous_city = self.player.city
            self.player.city = self.new_city
            return True
        return False
    
    def undo(self) -> None:
        if self.previous_city:
            self.player.city = self.previous_city

class TreatDiseaseCommand(Command):
    def __init__(self, player: 'Player'):
        self.player = player
        self.treated = False
        self.used_card = None
    
    def _has_matching_card(self) -> bool:
        current_city = self.player.city
        for i, card in enumerate(self.player.hand):
            if hasattr(card, 'city') and hasattr(card.city, 'disease') and card.city.disease.color == current_city.disease.color:
                self.used_card = i
                return True
        return False
    
    def execute(self) -> bool:
        if self.player.city.disease_quantity > 0 and self._has_matching_card():
            self.player.city.disease_quantity -= 1
            self.treated = True
            
            if self.used_card is not None:
                self.player.hand.pop(self.used_card)
            return True
        return False
    
    def undo(self) -> None:
        if self.treated:
            self.player.city.disease_quantity += 1
            

class BuildCenterCommand(Command):    
    def __init__(self, player: 'Player'):
        self.player = player
        self.was_built = False
    
    def execute(self) -> bool:
        if self.player.city.has_center:
            return False
        self.player.city.has_center = True
        self.was_built = True
        return True
    
    def undo(self) -> None:
        if self.was_built:
            self.player.city.has_center = False

class FindCureCommand(Command):
    def __init__(self, player: 'Player'):
        self.player = player
        self.had_cure = False
        self.used_cards = []
    
    def _has_enough_cards(self) -> bool:
        if not hasattr(self.player, 'hand') or not self.player.hand:
            return False
            
        current_disease_color = self.player.city.disease.color
        matching_cards = [
            card for card in self.player.hand 
            if hasattr(card, 'city') and hasattr(card.city, 'disease') 
            and card.city.disease.color == current_disease_color
        ]
        return len(matching_cards) >= 5
    
    def execute(self) -> bool:
        if self.player.city.disease.has_cure:
            return False
            
        if not self.player.city.has_center:
            return False
            
        if not self._has_enough_cards():
            return False
            
        current_disease_color = self.player.city.disease.color
        cards_removed = 0
        
        for i in range(len(self.player.hand) - 1, -1, -1):
            card = self.player.hand[i]
            if (hasattr(card, 'city') and hasattr(card.city, 'disease') 
                and card.city.disease.color == current_disease_color):
                self.used_cards.append(self.player.hand.pop(i))
                cards_removed += 1
                if cards_removed == 5:
                    break
        
        self.had_cure = self.player.city.disease.has_cure
        self.player.city.disease.has_cure = True
        return True
    
    def undo(self) -> None:
        if not self.had_cure and hasattr(self, 'used_cards'):
            self.player.hand.extend(self.used_cards)
            self.player.city.disease.has_cure = False
