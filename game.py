from city import City
from disease import Disease
from player import Player
import random

class Game:
    def __init__(self):
        self.cities: list[City] = []
        self.diseases: list[Disease] = []
        self.players: list[Player] = []
        self.infectionLevel = 2
        self.outbreaks = 0
        self.current_player_index = 0
        self.turn_actions_remaining = 1  # Changed from 4 to 1 for one action per turn 

    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.turn_actions_remaining = 1  # Changed from 4 to 1 for one action per turn

    def perform_action(self, action, *args, **kwargs):
        if self.turn_actions_remaining > 0:
            player = self.get_current_player()
            player.play(action, *args, **kwargs)
            self.turn_actions_remaining -= 1
            if self.turn_actions_remaining == 0:
                self.next_turn()

    def set_game_initial_state(self):
        blueDisease = Disease("Blue")
        yellowDisease = Disease("Yellow")
        redDisease = Disease("Red")
        blackDisease = Disease("Black")
        
        self.diseases.append(blueDisease)
        self.diseases.append(yellowDisease)
        self.diseases.append(redDisease)
        self.diseases.append(blackDisease)

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

        # Red disease cities (Asia and Australia)
        beijing = City("Beijing", (3418, 1177), redDisease)
        seoul = City("Seoul", (3631, 1131), redDisease)
        shangai = City("Shanghai", (3499, 1306), redDisease)
        tokyo = City("Tokyo", (3750, 1210), redDisease)
        osaka = City("Osaka", (3705, 1250), redDisease)
        taipei = City("Taipei", (3631, 1460), redDisease)
        hongKong = City("Hong Kong", (3537, 1548), redDisease)
        bangkok = City("Bangkok", (3321, 1629), redDisease)
        manila = City("Manila", (3705, 1604), redDisease)
        hoChiMinhCity = City("Ho Chi Minh City", (3449, 1701), redDisease)
        jakarta = City("Jakarta", (3499, 1879), redDisease)
        sydney = City("Sydney", (3930, 2178), redDisease)

        # Black disease cities (South and Center Asia, Middle East)
        algiers = City("Algiers", (2027, 1287), blackDisease)
        instanbul = City("Istanbul", (2274, 1169), blackDisease)
        moscow = City("Moscow", (2574, 859), blackDisease)
        cairo = City("Cairo", (2313, 1372), blackDisease)
        baghdad = City("Baghdad", (2482, 1247), blackDisease)
        tehran = City("Tehran", (2659, 1209), blackDisease)
        delhi = City("Delhi", (2797, 1372), blackDisease)
        karachi = City("Karachi", (2715, 1458), blackDisease)
        mumbai = City("Mumbai", (2755, 1495), blackDisease)
        riyadh = City("Riyadh", (2482, 1458), blackDisease)
        chennai = City("Chennai", (2853, 1629), blackDisease)
        kolkata = City("Kolkata", (2904, 1460), blackDisease)

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

        
        # Choose 4 random cities
        startingCities = random.sample(self.cities, 4)

        # Initialize players
        self.players = [
            Player("Fernando", startingCities[0]),
            Player("Rafael", startingCities[1]),
            Player("Oliver", startingCities[2]),
            Player("Patricia", startingCities[3])
        ]
    
    def check_ending_conditions(self):
        return self.outbreaks < 8

    def start_game(self):
        self.current_player_index = 0
        self.turn_actions_remaining = 1  # Changed from 4 to 1 for one action per turn

    