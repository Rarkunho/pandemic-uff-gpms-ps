import pygame

import math
from typing import List, Tuple
from city import City
from game import Game
import ctypes

# Initialize Pygame
pygame.init()

# Screen dimensions
user32 = ctypes.windll.user32
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pandemic Board Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

class Board:
    def __init__(self, game: Game):
        self.game = game

        self.font = pygame.font.SysFont('Arial', 14)
        self.small_font = pygame.font.SysFont('Arial', 10)
        self.selected_city = None
        self.action_buttons = []
        self.action_names = [
            ('Move', 'move'),
            ('Treat Disease', 'treat_disease'),
            ('Find Cure', 'find_cure'),
            ('Build Center', 'build_center')
        ]
        self.move_mode = False  # True when waiting for player to pick a neighbor city to move
        self.highlighted_cities = []  # Cities currently highlighted for movement



    def _get_city_color(self, city):
        """Get the color based on the city's disease color"""
        if city.disease.color == "Blue":
            return (0, 0, 255)
        elif city.disease.color == "Yellow":
            return (255, 255, 0)
        elif city.disease.color == "Red":
            return (255, 0, 0)
        elif city.disease.color == "Black":
            return (0, 0, 0)
        return GRAY


    def draw(self):
        """Draw the game board"""
        # Clear the screen
        # Retro 80s arcade style background with nebula, vignette, and starfield
        import time, math, random
        t = time.time()
        screen.fill((0, 0, 0))
        WIDTH, HEIGHT = screen.get_width(), screen.get_height()

        # --- Action Menu ---
        menu_height = 70
        button_width = 170
        button_height = 45
        gap = 25
        total_width = len(self.action_names) * button_width + (len(self.action_names)-1)*gap
        start_x = (WIDTH - total_width) // 2
        y = HEIGHT - menu_height
        self.action_buttons = []
        for i, (label, _) in enumerate(self.action_names):
            rect = pygame.Rect(start_x + i * (button_width + gap), y, button_width, button_height)
            self.action_buttons.append(rect)
            color = (40, 180, 255) if i == 0 else (60, 60, 60)
            pygame.draw.rect(screen, (80, 200, 255), rect, border_radius=12)
            if i == 0:
                pygame.draw.rect(screen, (255, 255, 255), rect, 4, border_radius=12)
            text = self.font.render(label, True, (0,0,0))
            screen.blit(text, (rect.x + (rect.width-text.get_width())//2, rect.y + (rect.height-text.get_height())//2))
        # Show current player, actions left, and disease info
        player = self.game.get_current_player() if self.game.players else None
        if player:
            # Get current city and its disease info
            current_city = player.city
            disease_info = f"{current_city.disease_quantity}"
            
            # Create text with player info and disease info
            # Display player name
            player_name_text = self.font.render(f"Current Player: {player.name}", True, (255,255,255))
            screen.blit(player_name_text, (20, y-32))
            
            # Display disease info and cure status
            disease_text = self.font.render(f"{current_city.disease.color} disease quantity: {disease_info}", True, (255,255,255))
            screen.blit(disease_text, (20, y-12))
            
            # Display cure status if disease is cured
            if hasattr(current_city, 'disease') and hasattr(current_city.disease, 'has_cure') and current_city.disease.has_cure:
                cure_text = self.font.render("CURED!", True, (0, 255, 0))
                screen.blit(cure_text, (100, y-12))
        # --- Neon/board drawing code continues as before ---

        # ... (rest of your draw code) ...

        # Compute zoom to fit all cities on screen with a margin
        min_x = min(c.coordinates[0] for c in self.game.cities)
        max_x = max(c.coordinates[0] for c in self.game.cities)
        min_y = min(c.coordinates[1] for c in self.game.cities)
        max_y = max(c.coordinates[1] for c in self.game.cities)
        spread_x = max_x - min_x
        spread_y = max_y - min_y
        margin = 60
        zoom_x = (WIDTH - 2 * margin) / spread_x if spread_x > 0 else 1.0
        zoom_y = (HEIGHT - 2 * margin) / spread_y if spread_y > 0 else 1.0
        zoom = min(zoom_x, zoom_y) * 0.9  
        offset_x = (WIDTH - (spread_x * zoom)) // 2 - int(min_x * zoom)
        offset_y = (HEIGHT - (spread_y * zoom)) // 2 - int(min_y * zoom)

        # Draw cities, highlighting neighbors if in move mode
        for city in self.game.cities:
            city_x, city_y = city.coordinates
            city_x = int(city_x * zoom + offset_x)
            city_y = int(city_y * zoom + offset_y)
            # If move mode and this city is a neighbor, highlight it
            if self.move_mode and city in self.highlighted_cities:
                pygame.draw.circle(screen, (0,255,0), (city_x, city_y), 20, 4)  # Green highlight
            # ... (rest of city drawing as before) ...

                pygame.draw.rect(screen, (255, 255, 255), rect, 4, border_radius=12)
            text = self.font.render(label, True, (0,0,0))
            screen.blit(text, (rect.x + (rect.width-text.get_width())//2, rect.y + (rect.height-text.get_height())//2))
        # Show current player and actions left
        player = self.game.get_current_player() if self.game.players else None
        if player:
            player_text = self.font.render(f"Current Player: {player.name}", True, (255,255,255))
            screen.blit(player_text, (20, y-32))
        # --- Static Neon Mini-Glows ---
        if not hasattr(self, '_neon_dots') or len(self._neon_dots) != 10:
            random.seed(99)
            self._neon_dots = [
                (random.randint(30, WIDTH-30), random.randint(30, HEIGHT-30), random.choice([(80,200,255), (255,80,180), (255,220,90), (170,80,255)]), random.randint(4,8), random.randint(8,22))
                for _ in range(10)
            ]
        neon_dots = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x, y, col, r, alpha in self._neon_dots:
            if r <= 4:
                pygame.draw.circle(neon_dots, col+(alpha,), (x, y), r)
            # else: skip medium/large dots entirely
        screen.blit(neon_dots, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
        # --- Twinkling Neon Starfield ---
        if not hasattr(self, '_starfield'):
            random.seed(42)
            self._starfield = [(random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1), random.choice([(80,200,255), (255,80,180), (255,220,90), (170,80,255)]), random.uniform(0, 2*math.pi)) for _ in range(80)]
        for sx, sy, scol, phase in self._starfield:
            tw = 120 + 80 * math.sin(t*2 + phase)
            pygame.draw.circle(screen, scol+(int(tw),), (sx, sy), 1)
        # --- Neon Vignette ---
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for r in range(int(WIDTH*0.48), int(WIDTH*0.5)+1, 2):
            pygame.draw.ellipse(vignette, (80,200,255,8), vignette.get_rect().inflate(-2*r, -2*r), 2)
        for r in range(int(WIDTH*0.43), int(WIDTH*0.48), 3):
            pygame.draw.ellipse(vignette, (255,80,180,5), vignette.get_rect().inflate(-2*r, -2*r), 2)
        screen.blit(vignette, (0,0), special_flags=pygame.BLEND_RGBA_ADD)


        
        # Compute zoom to fit all cities on screen with a margin
        min_x = min(c.coordinates[0] for c in self.game.cities)
        max_x = max(c.coordinates[0] for c in self.game.cities)
        min_y = min(c.coordinates[1] for c in self.game.cities)
        max_y = max(c.coordinates[1] for c in self.game.cities)
        spread_x = max_x - min_x
        spread_y = max_y - min_y
        margin = 60
        zoom_x = (WIDTH - 2 * margin) / spread_x if spread_x > 0 else 1.0
        zoom_y = (HEIGHT - 2 * margin) / spread_y if spread_y > 0 else 1.0
        zoom = min(zoom_x, zoom_y) * 0.9  
        offset_x = (WIDTH - (spread_x * zoom)) // 2 - int(min_x * zoom)
        offset_y = (HEIGHT - (spread_y * zoom)) // 2 - int(min_y * zoom)

        # Draw subtle rounded border
        border_rect = pygame.Rect(10, 10, WIDTH-20, HEIGHT-20)
        pygame.draw.rect(screen, (180, 180, 220), border_rect, 3, border_radius=24)

        # Draw connections between cities
        for city in self.game.cities:
            city_x, city_y = city.coordinates
            city_x = int(city_x * zoom + offset_x)
            city_y = int(city_y * zoom + offset_y)
            
            for neighbor in city.neighbors:
                if neighbor in self.game.cities:  # Ensure neighbor is in our cities list
                    nx, ny = neighbor.coordinates
                    nx = int(nx * zoom + offset_x)
                    ny = int(ny * zoom + offset_y)
                    
                    # Draw animated neon connection lines
                    dx = abs(city_x - nx)
                    # Use green if disease is cured, otherwise use disease color
                    if city.disease.has_cure:
                        neon_base = (0, 255, 0)  # Bright green for cured diseases
                        shadow = (0, 100, 0)     # Darker green shadow
                    else:
                        neon_base = (80,200,255) if city.disease.color=="Blue" else (255,220,90) if city.disease.color=="Yellow" else (255,80,180) if city.disease.color=="Red" else (170,80,255)
                        shadow = (60,60,60)
                    # Animate pulse along the edge
                    pulse_speed = 2.0
                    phase = t * pulse_speed + (city_x + city_y + nx + ny) * 0.005
                    pulse = 0.5 + 0.5 * math.sin(phase)
                    neon = tuple(min(255, int(c * (0.7 + 0.6 * pulse))) for c in neon_base)
                    if dx > WIDTH // 2:
                        if city_x > nx:
                            pygame.draw.line(screen, shadow, (city_x, city_y+2), (nx+WIDTH, ny+2), 2)
                            pygame.draw.line(screen, neon, (city_x, city_y), (nx+WIDTH, ny), 1)
                        else:
                            pygame.draw.line(screen, shadow, (city_x, city_y+2), (nx-WIDTH, ny+2), 2)
                            pygame.draw.line(screen, neon, (city_x, city_y), (nx-WIDTH, ny), 1)
                    else:
                        pygame.draw.line(screen, shadow, (city_x, city_y+2), (nx, ny+2), 2)
                        pygame.draw.line(screen, neon, (city_x, city_y), (nx, ny), 1)

        
        # Draw cities
        for city in self.game.cities:
            city_x, city_y = city.coordinates
            city_x = int(city_x * zoom + offset_x)
            city_y = int(city_y * zoom + offset_y)
            
            # Draw pixelated shadow under city
            pygame.draw.circle(screen, (40,40,40), (city_x, city_y+6), 13)
            # Animate city pulse (smaller, faster)
            city_idx = self.game.cities.index(city)
            node_pulse = 0.85 + 0.15 * math.sin(t*5 + city_idx)
            
            # Use green if disease is cured, otherwise use disease color
            if city.disease.has_cure:
                neon_base = (0, 255, 0)  # Bright green for cured diseases
            else:
                neon_base = (80,200,255) if city.disease.color=="Blue" else (255,220,90) if city.disease.color=="Yellow" else (255,80,180) if city.disease.color=="Red" else (170,80,255)
            
            neon = tuple(min(255, int(c * node_pulse)) for c in neon_base)
            radius = int(8 * node_pulse + 5)
            pygame.draw.circle(screen, neon, (city_x, city_y), radius)
            pygame.draw.circle(screen, (0,0,0), (city_x, city_y), int(radius*0.75))
            pygame.draw.circle(screen, neon, (city_x, city_y), int(radius*0.65))
            # Draw city name in pixel/arcade font (fallback to bold monospace)
            font = pygame.font.SysFont('Press Start 2P,Consolas,Courier New,Arial', 17, bold=True)
            # Use green text if disease is cured, otherwise use the default cyan color
            text_color = (0, 255, 0) if city.disease.has_cure else (0, 255, 128)
            text = font.render(city.name, True, text_color)
            outline = font.render(city.name, True, (0,0,0))
            screen.blit(outline, (city_x + 13, city_y - 5))
            screen.blit(text, (city_x + 12, city_y - 6))
            # Draw player tokens in this city
            players_here = [p for p in self.game.players if p.city == city]
            player_colors = [(0,255,255), (255,128,0), (0,255,128), (255,0,128), (255,255,0), (128,0,255), (255,0,0), (0,128,255)]
            for idx, player in enumerate(players_here):
                px = city_x + (idx-1.5)*18 if len(players_here) <= 4 else city_x + (idx-len(players_here)/2)*18
                py = city_y - 27
                color = player_colors[idx%len(player_colors)]
                # Highlight current player's token
                if player == self.game.get_current_player():
                    pygame.draw.circle(screen, (255,255,255), (int(px), int(py)), 15)
                pygame.draw.circle(screen, color, (int(px), int(py)), 12)
                # Draw player initials
                initials = ''.join([part[0] for part in player.name.split()]).upper()
                initial_font = pygame.font.SysFont('Arial', 14, bold=True)
                initial_text = initial_font.render(initials, True, (0,0,0))
                screen.blit(initial_text, (int(px)-initial_text.get_width()//2, int(py)-initial_text.get_height()//2))
            # Draw research center if built
            if city.has_center:
                center_size = 15
                pygame.draw.rect(screen, (255, 255, 255), 
                               (city_x - center_size//2, city_y - center_size//2, 
                                center_size, center_size))
                pygame.draw.rect(screen, (0, 0, 0), 
                               (city_x - center_size//2, city_y - center_size//2, 
                                center_size, center_size), 2)
                # Draw a plus sign inside the square
                pygame.draw.line(screen, (0, 0, 0), 
                               (city_x - center_size//4, city_y), 
                               (city_x + center_size//4, city_y), 2)
                pygame.draw.line(screen, (0, 0, 0), 
                               (city_x, city_y - center_size//4), 
                               (city_x, city_y + center_size//4), 2)
            
            # Highlight selected city with rotating dashed neon ring
            if self.selected_city == city:
                import math
                t = time.time()
                for i in range(12):
                    if (i + int(t*6)) % 2 == 0:
                        angle = i * math.pi/6
                        x = int(city_x + 18 * math.cos(angle))
                        y = int(city_y + 18 * math.sin(angle))
                        pygame.draw.circle(screen, neon, (x, y), 3)


    def handle_event(self, event):
        """Handle Pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                # If in move mode, check if a neighbor city was clicked
                if self.move_mode:
                    # Calculate zoom/offset to match draw()
                    min_x = min(c.coordinates[0] for c in self.game.cities)
                    max_x = max(c.coordinates[0] for c in self.game.cities)
                    min_y = min(c.coordinates[1] for c in self.game.cities)
                    max_y = max(c.coordinates[1] for c in self.game.cities)
                    spread_x = max_x - min_x
                    spread_y = max_y - min_y
                    margin = 60
                    zoom_x = (WIDTH - 2 * margin) / spread_x if spread_x > 0 else 1.0
                    zoom_y = (HEIGHT - 2 * margin) / spread_y if spread_y > 0 else 1.0
                    zoom = min(zoom_x, zoom_y) * 0.9
                    offset_x = (WIDTH - (spread_x * zoom)) // 2 - int(min_x * zoom)
                    offset_y = (HEIGHT - (spread_y * zoom)) // 2 - int(min_y * zoom)
                    for city in self.highlighted_cities:
                        city_x, city_y = city.coordinates
                        city_x = int(city_x * zoom + offset_x)
                        city_y = int(city_y * zoom + offset_y)
                        distance = math.sqrt((mouse_x - city_x) ** 2 + (mouse_y - city_y) ** 2)
                        if distance < 20:
                            # Move to this city
                            self.game.perform_action('move', city)
                            self.move_mode = False
                            self.highlighted_cities = []
                            self.selected_city = None
                            return
                    # Clicked elsewhere: do nothing
                    return
                # Not in move mode: check action buttons
                for i, rect in enumerate(self.action_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        action = self.action_names[i][1]
                        if action == 'move':
                            # Enter move mode: highlight neighbors
                            player = self.game.get_current_player()
                            self.move_mode = True
                            self.highlighted_cities = list(player.city.neighbors)
                            return
                        elif action == 'build_center':
                            # Build a research center in the current city
                            player = self.game.get_current_player()
                            if not player.city.has_center:  # Only build if there isn't already a center
                                self.game.perform_action(action)
                                player.city.setCenter()  # Ensure the center is marked as built
                            return
                        else:
                            self.game.perform_action(action)
                            return
                # Otherwise, check if a city was clicked (for selection, not movement)
                for city in self.game.cities:
                    city_x, city_y = city.coordinates
                    min_x = min(c.coordinates[0] for c in self.game.cities)
                    max_x = max(c.coordinates[0] for c in self.game.cities)
                    min_y = min(c.coordinates[1] for c in self.game.cities)
                    max_y = max(c.coordinates[1] for c in self.game.cities)
                    spread_x = max_x - min_x
                    spread_y = max_y - min_y
                    offset_x = (WIDTH - spread_x) // 2 - min_x
                    offset_y = (HEIGHT - spread_y) // 2 - min_y
                    city_x = int(city_x + offset_x)
                    city_y = int(city_y + offset_y)
                    distance = math.sqrt((mouse_x - city_x) ** 2 + (mouse_y - city_y) ** 2)
                    if distance < 10:
                        self.selected_city = city
                        print(f"Selected city: {city.name}")
                        break
                else:
                    self.selected_city = None
