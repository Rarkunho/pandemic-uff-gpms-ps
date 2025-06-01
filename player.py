from city import City
from commands import MoveCommand, TreatDiseaseCommand, BuildCenterCommand, FindCureCommand

class Player:
    def __init__(self, name: str, city: City):
        self.name = name
        self.city: City = city
        self.command_history = []
    
    def move(self, new_city: City) -> bool:
        """Move to a new city using the command pattern."""
        command = MoveCommand(self, new_city)
        success = command.execute()
        if success:
            self.command_history.append(command)
        return success

    def find_cure(self) -> bool:
        """Find a cure for the disease in the current city using the command pattern."""
        command = FindCureCommand(self)
        success = command.execute()
        if success:
            self.command_history.append(command)
        return success

    def build_center(self) -> bool:
        """Build a research center in the current city using the command pattern."""
        command = BuildCenterCommand(self)
        success = command.execute()
        if success:
            self.command_history.append(command)
        return success

    def treat_disease(self) -> bool:
        """Treat disease in the current city using the command pattern."""
        command = TreatDiseaseCommand(self)
        success = command.execute()
        if success:
            self.command_history.append(command)
        return success

    def undo_last_action(self) -> None:
        """Undo the last action performed by the player."""
        if self.command_history:
            last_command = self.command_history.pop()
            last_command.undo()

    def play(self, action, *args):
        """
        Perform the specified action. For 'move', expects a city argument and only allows movement to a neighboring city.
        """
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
