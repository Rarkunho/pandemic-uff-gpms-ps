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
    """Command to treat disease in the player's current city using a matching card."""
    
    def __init__(self, player: 'Player'):
        self.player = player
        self.treated = False
        self.used_card = None
    
    def _has_matching_card(self) -> bool:
        """Check if player has a card matching the current city's disease color."""
        current_city = self.player.city
        for i, card in enumerate(self.player.hand):
            if hasattr(card, 'city') and hasattr(card.city, 'disease') and card.city.disease.color == current_city.disease.color:
                self.used_card = i
                return True
        return False
    
    def execute(self) -> bool:
        # Check if city has disease to treat and player has a matching card
        if self.player.city.disease_quantity > 0 and self._has_matching_card():
            # Remove one disease cube
            self.player.city.disease_quantity -= 1
            self.treated = True
            
            # Remove the used card from player's hand
            if self.used_card is not None:
                self.player.hand.pop(self.used_card)
            return True
        return False
    
    def undo(self) -> None:
        if self.treated:
            # Add back the disease cube
            self.player.city.disease_quantity += 1
            
            # Note: We don't automatically add the card back to hand here
            # as it would be complex to track its exact position

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
    """Command to find a cure for the disease in the player's current city.
    
    Requirements:
    - Player must be in a city with a research center
    - Player must have 5 cards of the disease color
    """
    
    def __init__(self, player: 'Player'):
        self.player = player
        self.had_cure = False
        self.used_cards = []
    
    def _has_enough_cards(self) -> bool:
        """Check if player has 5 cards of the current city's disease color."""
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
        # Check if already cured
        if self.player.city.disease.has_cure:
            return False
            
        # Check if in a city with research center
        if not self.player.city.has_center:
            return False
            
        # Check if has enough cards of the disease color
        if not self._has_enough_cards():
            return False
            
        # Remove 5 cards of the disease color
        current_disease_color = self.player.city.disease.color
        cards_removed = 0
        
        # Need to iterate backwards since we're modifying the list
        for i in range(len(self.player.hand) - 1, -1, -1):
            card = self.player.hand[i]
            if (hasattr(card, 'city') and hasattr(card.city, 'disease') 
                and card.city.disease.color == current_disease_color):
                self.used_cards.append(self.player.hand.pop(i))
                cards_removed += 1
                if cards_removed == 5:
                    break
        
        # Mark the disease as cured
        self.had_cure = self.player.city.disease.has_cure
        self.player.city.disease.has_cure = True
        return True
    
    def undo(self) -> None:
        if not self.had_cure and hasattr(self, 'used_cards'):
            # Add the used cards back to the player's hand
            self.player.hand.extend(self.used_cards)
            self.player.city.disease.has_cure = False
