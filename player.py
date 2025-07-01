from city import City
from commands import MoveCommand, TreatDiseaseCommand, BuildCenterCommand, FindCureCommand

class Player:
    def __init__(self, name: str, city: City):
        self.name = name
        self.city: City = city
        self.command_history = []
        self.hand = []
    
    def move(self, new_city: City) -> bool:
        command = MoveCommand(self, new_city)
        success = command.execute()
        if success:
            self.command_history.append(command)
        return success

    def find_cure(self, board=None) -> bool:
        if self.city.disease.has_cure:
            if board:
                board.show_message(f"A cure for {self.city.disease.color} disease already exists!")
            return False
        if not self.city.has_center:
            if board:
                board.show_message("You must be in a city with a research center to find a cure!")
            return False
            
        disease_color = self.city.disease.color
        matching_cards = [
            card for card in self.hand 
            if hasattr(card, 'city') and hasattr(card.city, 'disease') 
            and card.city.disease.color == disease_color
        ]
        
        if len(matching_cards) < 5:
            if board:
                board.show_message(f"You need 5 {disease_color} cards to find a cure! You have {len(matching_cards)}.")
            return False
        command = FindCureCommand(self)
        success = command.execute()
        if success:
            self.command_history.append(command)
            if board:
                board.show_message(f"Success! A cure for {disease_color} disease has been discovered!")
        return success

    def build_center(self) -> bool:
        command = BuildCenterCommand(self)
        success = command.execute()
        if success:
            self.command_history.append(command)
        else:
            return False
        return success

    def treat_disease(self, board) -> bool:
        if self.city.disease_quantity == 0:
            board.show_message(f"No disease to treat in {self.city.name}.")
            return False
            
        command = TreatDiseaseCommand(self)
        success = command.execute()
        
        if success:
            self.command_history.append(command)
            board.show_message(f"Treated disease in {self.city.name}. Used a {self.city.disease.color} card.")
        else:
            board.show_message(f"Cannot treat disease: No {self.city.disease.color} card in hand.")
            
        return success

    def undo_last_action(self) -> None:
        if self.command_history:
            last_command = self.command_history.pop()
            last_command.undo()

    def play(self, action, *args):
        if action == 'move':
            if args and isinstance(args[0], City):
                target_city = args[0]
                self.move(target_city)
            else:
                print("No valid city specified for move action.")
        elif action == 'find_cure':
            self.find_cure()
        elif action == 'build_center':
            self.build_center()
        elif action == 'treat_disease':
            self.treat_disease()
