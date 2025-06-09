from city import City
from disease import Disease
from player import Player
from cards import CityPlayerCard, EpidemicPlayerCard, InfectionCard
import random
from typing import List, Union

class Game:
    def __init__(self):
        self.cities: list[City] = []
        self.diseases: list[Disease] = []
        self.players: list[Player] = []
        self.infectionLevel = 2
        self.outbreaks = 0
        self.current_player_index = 0
        self.turn_actions_remaining = 1  
        self.player_deck: List[Union[CityPlayerCard, EpidemicPlayerCard]] = []
        self.infection_deck: List[InfectionCard] = []
        self.infection_discard: List[InfectionCard] = []  
        self.board = None
        
    def get_current_player(self):
        return self.players[self.current_player_index]

    def check_ending_conditions(self):
        """Check for win/lose conditions.
        
        Returns:
            tuple: (game_over, message) where game_over is a boolean and message is a string
                  describing the result (win/lose message or None if game continues)
        """
        # Check win condition: all diseases have cures
        all_cured = all(disease.has_cure for disease in self.diseases)
        if all_cured:
            return True, "Congratulations! You've cured all diseases and won the game!"
            
        # Check lose conditions
        # 1. No more infection cards to draw
        if not self.infection_deck:
            return True, "Game Over! No more infection cards to draw."
            
        # 2. Any disease has 24 or more cubes on the board
        for disease in self.diseases:
            cube_count = sum(city.disease_quantity for city in self.cities 
                          if hasattr(city, 'disease') and city.disease == disease)
            if cube_count >= 24:
                return True, f"Game Over! Too many {disease.color} disease cubes on the board."
                
        # 3. 8 or more outbreaks
        if self.outbreaks >= 8:
            return True, "Game Over! Too many outbreaks have occurred (8 or more)."
            
        # If none of the above, game continues
        return False, None
    
    def handle_epidemic(self):
        """
        Handle an epidemic event with the following effects:
        1. Increase the infection level by 1
        2. Draw and intensify the bottom card of the infection deck
        3. Shuffle the infection discard pile and place it on top of the infection deck
        """
        # 1. Increase infection level
        self.infectionLevel = min(self.infectionLevel + 1, 6)
        self.board.show_message(f"Epidemic! Infection level increased to {self.infectionLevel}")
        
        # 2. Intensify - draw and resolve bottom card of infection deck
        if self.infection_deck:
            card = self.infection_deck.pop(0)
            for _ in range(3):
                card.city.infect(self)
            self.infection_discard.append(card)
        
        # 3. Reshuffle discard pile and place on top of infection deck
        if self.infection_discard:
            random.shuffle(self.infection_discard)
            self.infection_deck = self.infection_discard + self.infection_deck
            self.infection_discard = []
            
        self.board.show_message("Infection cards have been reshuffled!")

    def next_turn(self):
        # Draw cards for the current player
        self.draw_end_of_turn_cards()
        
        # Check game state after card drawing
        game_over, message = self.check_ending_conditions()
        if game_over:
            self.board.show_blocking_message(message)
            return False
        
        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.turn_actions_remaining = 1  
        
        return True
        
    def draw_end_of_turn_cards(self):
        """
        Draw cards at the end of the turn.
        Draws 2 player cards and draws infection cards equal to the current infection level.
        """
        current_player = self.get_current_player()
        
        # Draw 2 player cards
        for _ in range(2):
            if not self.player_deck:
                self.board.show_message("No more player cards to draw!")
                break
                
            card = self.draw_player_card()
            
            # Handle Epidemic card
            if isinstance(card, EpidemicPlayerCard):
                self.handle_epidemic()
                self.board.show_message(f"{current_player.name} triggered an EPIDEMIC!")
                
            # Add city cards to the player's hand
            if isinstance(card, CityPlayerCard):
                current_player.hand.append(card)
            
            # Check if player has too many cards
            if len(current_player.hand) > 7:
                self.board.show_message(f"{current_player.name} has too many cards! Must discard down to 7.")
                # For now, just keep the first 7 cards
                current_player.hand = current_player.hand[:7]
        
        # Draw infection cards based on current infection level
        for _ in range(self.infectionLevel):
            if not self.infection_deck:
                break
                
            infection_card = self.draw_infection_card()
            if infection_card is not None:
                infection_card.city.infect(self)

        return True  # Turn completed successfully
    

    def perform_action(self, action, *args, board=None, **kwargs):
        if self.turn_actions_remaining > 0:
            player = self.get_current_player()
            
            # For actions that need the board reference and special handling
            if action in ['treat_disease', 'find_cure']:
                if board is None:
                    print(f"Error: Board reference is required for {action} action")
                    return False
                    
                # Call the appropriate method with board reference
                if action == 'treat_disease':
                    success = player.treat_disease(board)
                else:  # find_cure
                    success = player.find_cure(board)
                
                # Only consume action if successful
                if success:
                    self.turn_actions_remaining -= 1
                    if self.turn_actions_remaining == 0:
                        self.next_turn()
                return success
            else:
                # For other actions, proceed as normal
                player.play(action, *args, **kwargs)
                self.turn_actions_remaining -= 1
                if self.turn_actions_remaining == 0:
                    self.next_turn()
                return True
   
    def set_game_initial_state(self):
        blueDisease, yellowDisease, pinkDisease, purpleDisease = self.set_diseases()
        initialCity = self.set_cities_graph(blueDisease, yellowDisease, pinkDisease, purpleDisease)
        self.set_players(initialCity)
        initialCity.has_center = True
        self.set_player_deck()
        self.set_infection_deck()
        self.set_initial_infection()
    
    def set_diseases(self):
        blueDisease = Disease("Blue")
        yellowDisease = Disease("Yellow")
        pinkDisease = Disease("Pink")
        purpleDisease = Disease("Purple")
        
        self.diseases.append(blueDisease)
        self.diseases.append(yellowDisease)
        self.diseases.append(pinkDisease)
        self.diseases.append(purpleDisease)
        return blueDisease, yellowDisease, pinkDisease, purpleDisease
    
    def set_cities_graph(self, blueDisease, yellowDisease, pinkDisease, purpleDisease):   
        
        sanFrancisco = City("San Francisco", (858, 1170), blueDisease)
        chicago = City("Chicago", (1287, 1170), blueDisease)
        atlanta = City("Atlanta", (1372, 1287), blueDisease)
        montreal = City("Montreal", (1580, 943), blueDisease)
        washington = City("Washington", (1495, 1209), blueDisease)
        newYork = City("New York", (1629, 1117), blueDisease)
        london = City("London", (1925, 859), blueDisease)
        madrid = City("Madrid", (1849, 1209), blueDisease)
        paris = City("Paris", (1897, 1037), blueDisease)
        essen = City("Essen", (2027, 943), blueDisease)
        milan = City("Milan", (2071, 1170), blueDisease)
        stPetersburg = City("St. Petersburg", (2240, 842), blueDisease)

        # Yellow disease cities (Africa and America)
        losAngeles = City("Los Angeles", (791, 1287), yellowDisease)
        mexicoCity = City("Mexico City", (1095, 1458), yellowDisease)
        miami = City("Miami", (1287, 1372), yellowDisease)
        bogota = City("Bogota", (1247, 1716), yellowDisease)
        lima = City("Lima", (1287, 1925), yellowDisease)
        santiago = City("Santiago", (1287, 2356), yellowDisease)
        buenosAires = City("Buenos Aires", (1495, 2356), yellowDisease)
        saoPaulo = City("Sao Paulo", (1629, 2064), yellowDisease)
        lagos = City("Lagos", (2145, 1629), yellowDisease)
        khartoum = City("Khartoum", (2356, 1495), yellowDisease)
        kinshasa = City("Kinshasa", (2274, 1798), yellowDisease)
        johannesburg = City("Johannesburg", (2313, 2240), yellowDisease)

        # Pink disease cities (Asia and Australia)
        beijing = City("Beijing", (3418, 1177), pinkDisease)
        seoul = City("Seoul", (3631, 1131), pinkDisease)
        shangai = City("Shanghai", (3499, 1306), pinkDisease)
        tokyo = City("Tokyo", (3750, 1210), pinkDisease)
        osaka = City("Osaka", (3705, 1250), pinkDisease)
        taipei = City("Taipei", (3631, 1460), pinkDisease)
        hongKong = City("Hong Kong", (3537, 1548), pinkDisease)
        bangkok = City("Bangkok", (3321, 1629), pinkDisease)
        manila = City("Manila", (3705, 1604), pinkDisease)
        hoChiMinhCity = City("Ho Chi Minh City", (3449, 1701), pinkDisease)
        jakarta = City("Jakarta", (3499, 1879), pinkDisease)
        sydney = City("Sydney", (3930, 2178), pinkDisease)

        # Purple disease cities (South and Center Asia, Middle East)
        algiers = City("Algiers", (2027, 1287), purpleDisease)
        instanbul = City("Istanbul", (2274, 1169), purpleDisease)
        moscow = City("Moscow", (2574, 859), purpleDisease)
        cairo = City("Cairo", (2313, 1372), purpleDisease)
        baghdad = City("Baghdad", (2482, 1247), purpleDisease)
        tehran = City("Tehran", (2659, 1209), purpleDisease)
        delhi = City("Delhi", (2797, 1372), purpleDisease)
        karachi = City("Karachi", (2715, 1458), purpleDisease)
        mumbai = City("Mumbai", (2755, 1495), purpleDisease)
        riyadh = City("Riyadh", (2482, 1458), purpleDisease)
        chennai = City("Chennai", (2853, 1629), purpleDisease)
        kolkata = City("Kolkata", (2904, 1460), purpleDisease)

        sanFrancisco.setNeighbors([tokyo, manila, losAngeles, chicago])
        chicago.setNeighbors([sanFrancisco, losAngeles, mexicoCity, atlanta, montreal])
        atlanta.setNeighbors([chicago, washington, miami])
        montreal.setNeighbors([chicago, washington, newYork])
        washington.setNeighbors([atlanta, montreal, newYork, miami])
        newYork.setNeighbors([montreal, washington, madrid, london])
        london.setNeighbors([newYork, madrid, essen, paris])
        madrid.setNeighbors([newYork, london, paris, algiers, saoPaulo])
        paris.setNeighbors([madrid, london, essen, milan, algiers])
        essen.setNeighbors([london, paris, milan, stPetersburg])
        milan.setNeighbors([essen, paris, instanbul])
        stPetersburg.setNeighbors([essen, instanbul, moscow])

        losAngeles.setNeighbors([sanFrancisco, chicago, mexicoCity, sydney])
        mexicoCity.setNeighbors([losAngeles, chicago, miami, bogota, lima])
        miami.setNeighbors([atlanta, washington, mexicoCity, bogota])
        bogota.setNeighbors([mexicoCity, miami, lima, saoPaulo, buenosAires])
        lima.setNeighbors([mexicoCity, bogota, santiago])
        santiago.setNeighbors([lima])
        buenosAires.setNeighbors([bogota, saoPaulo])
        saoPaulo.setNeighbors([bogota, buenosAires, madrid, lagos])
        lagos.setNeighbors([saoPaulo, khartoum, kinshasa])
        khartoum.setNeighbors([lagos, kinshasa, johannesburg, cairo])
        kinshasa.setNeighbors([lagos, khartoum, johannesburg])
        johannesburg.setNeighbors([kinshasa, khartoum])

        beijing.setNeighbors([shangai, seoul])
        seoul.setNeighbors([beijing, shangai, tokyo])
        shangai.setNeighbors([beijing, seoul, tokyo, hongKong, taipei])
        tokyo.setNeighbors([seoul, shangai, osaka, sanFrancisco])
        osaka.setNeighbors([tokyo, taipei])
        taipei.setNeighbors([shangai, osaka, hongKong, manila])
        hongKong.setNeighbors([shangai, taipei, manila, bangkok, hoChiMinhCity, kolkata])
        bangkok.setNeighbors([hongKong, hoChiMinhCity, jakarta, kolkata])
        manila.setNeighbors([hongKong, taipei, sanFrancisco, hoChiMinhCity, sydney])
        hoChiMinhCity.setNeighbors([bangkok, manila, jakarta])
        jakarta.setNeighbors([bangkok, hoChiMinhCity, sydney])
        sydney.setNeighbors([jakarta, manila, losAngeles])

        algiers.setNeighbors([madrid, paris, instanbul, cairo])
        instanbul.setNeighbors([milan, stPetersburg, moscow, baghdad, cairo, algiers])
        moscow.setNeighbors([stPetersburg, instanbul, tehran])
        cairo.setNeighbors([algiers, instanbul, baghdad, khartoum, riyadh])
        baghdad.setNeighbors([instanbul, cairo, riyadh, tehran, karachi])
        tehran.setNeighbors([moscow, baghdad, karachi, delhi])
        delhi.setNeighbors([tehran, karachi, mumbai, chennai, kolkata])
        karachi.setNeighbors([baghdad, tehran, delhi, mumbai, riyadh])
        mumbai.setNeighbors([karachi, delhi, chennai])
        riyadh.setNeighbors([cairo, baghdad, karachi])
        chennai.setNeighbors([mumbai, delhi, kolkata, bangkok])
        kolkata.setNeighbors([delhi, chennai, bangkok, hongKong])

        self.cities.append(sanFrancisco)
        self.cities.append(chicago)
        self.cities.append(atlanta)
        self.cities.append(montreal)
        self.cities.append(washington)
        self.cities.append(newYork)
        self.cities.append(london)
        self.cities.append(madrid)
        self.cities.append(paris)
        self.cities.append(essen)
        self.cities.append(milan)
        self.cities.append(stPetersburg)
        self.cities.append(losAngeles)
        self.cities.append(mexicoCity)
        self.cities.append(miami)
        self.cities.append(bogota)
        self.cities.append(lima)
        self.cities.append(santiago)
        self.cities.append(buenosAires)
        self.cities.append(saoPaulo)
        self.cities.append(lagos)
        self.cities.append(khartoum)
        self.cities.append(kinshasa)
        self.cities.append(johannesburg)
        self.cities.append(beijing)
        self.cities.append(seoul)
        self.cities.append(shangai)
        self.cities.append(tokyo)
        self.cities.append(osaka)
        self.cities.append(taipei)
        self.cities.append(hongKong)
        self.cities.append(bangkok)
        self.cities.append(manila)
        self.cities.append(hoChiMinhCity)
        self.cities.append(jakarta)
        self.cities.append(sydney)
        self.cities.append(algiers)
        self.cities.append(instanbul)
        self.cities.append(moscow)
        self.cities.append(cairo)
        self.cities.append(baghdad)
        self.cities.append(tehran)
        self.cities.append(delhi)
        self.cities.append(karachi)
        self.cities.append(mumbai)
        self.cities.append(riyadh)
        self.cities.append(chennai)
        self.cities.append(kolkata)

        return atlanta
    
    def set_players(self, initialCity):
        self.players = [
            Player("Fernando", initialCity),
            Player("Rafael", initialCity),
            Player("Oliver", initialCity),
            Player("Patricia", initialCity)
        ]

    def set_player_deck(self) -> None:
        self.player_deck = []
        
        for city in self.cities:
            self.player_deck.append(CityPlayerCard(city))

        random.shuffle(self.player_deck)
        
        self.set_players_initial_hand()

        for _ in range(6):
            self.player_deck.append(EpidemicPlayerCard())
        
        random.shuffle(self.player_deck)

    def set_infection_deck(self) -> None:
        self.infection_deck = []
        self.infection_discard = []  
        
        for city in self.cities:
            self.infection_deck.append(InfectionCard(city))
        
        random.shuffle(self.infection_deck)
    
    def draw_player_card(self) -> Union[CityPlayerCard, EpidemicPlayerCard]:
        if not self.player_deck:
            self.board.show_message("No more player cards available")
            return None
        return self.player_deck.pop()
    
    def draw_infection_card(self) -> InfectionCard:
        """Draw a card from the infection deck and move it to the discard pile."""
        if not self.infection_deck:
            return None
        card = self.infection_deck.pop()
        self.infection_discard.append(card)  # Add to discard when drawn
        return card
    
    def set_players_initial_hand(self) -> None:
        for player in self.players:
            for _ in range(2):
                card = self.draw_player_card()
                player.hand.append(card)

    def set_initial_infection(self):
        for _ in range(3):
            card = self.draw_infection_card()
            for _ in range(3):
                card.increase_city_disease_quantity()
        for _ in range(3):
            card = self.draw_infection_card()
            for _ in range(2):
                card.increase_city_disease_quantity()
        for _ in range(3):
            card = self.draw_infection_card()
            card.increase_city_disease_quantity()

    def get_current_player(self):
        if not self.players:
            return None
        return self.players[self.current_player_index]
        

    