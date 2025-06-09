import pygame

import math
from typing import List, Tuple
from city import City
from game import Game
import platform
import ctypes

# Initialize Pygame
pygame.init()

# Screen dimensions
if platform.system() == "Windows":
    user32 = ctypes.windll.user32
    WIDTH = user32.GetSystemMetrics(0)
    HEIGHT = user32.GetSystemMetrics(1)
else:
    display_info = pygame.display.Info()
    WIDTH = display_info.current_w
    HEIGHT = display_info.current_h

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pandemic Board Game")

# Colors
WHITE = (255, 255, 255)
PURPLE = (170, 80, 255)
BLUE = (80, 200, 255) 
YELLOW = (255, 220, 90)
PINK = (255, 80, 180)
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
        
        # UI Settings
        self.card_width = 30
        self.card_height = 40
        self.card_margin = 3
        self.disease_colors = {
            'Blue': BLUE,
            'Yellow': YELLOW,
            'Pink': PINK,
            'Purple': PURPLE
        }
        
        # Message display
        self.message_history = []
        self.message_timer = 0
        self.message_duration = 180  # frames (3 seconds at 60 FPS)
        self.max_messages = 3  # Maximum number of messages to keep in history
        
    def show_message(self, message: str):
        """Display a message on the screen for a short duration.
        
        Args:
            message: The message to display. Will be added to the message history.
        """
        # Add new message to history
        self.message_history.insert(0, message)
        # Keep only the most recent messages
        self.message_history = self.message_history[:self.max_messages]
        # Reset timer for all messages
        self.message_timer = self.message_duration
        
    def show_blocking_message(self, message: str):
        """Display a prominent, centered message that blocks the UI until the user closes it.
        
        Args:
            message: The message to display (can be multiple lines separated by '\n')
        """
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Set up fonts
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        text_font = pygame.font.SysFont('Arial', 24)
        
        # Calculate message box dimensions
        lines = message.split('\n')
        line_heights = [title_font.size(line)[1] if i == 0 else text_font.size(line)[1] 
                       for i, line in enumerate(lines)]
        total_height = sum(line_heights) + 60  # Add padding
        max_width = max(title_font.size(line)[0] if i == 0 else text_font.size(line)[0] 
                       for i, line in enumerate(lines))
        
        # Draw message box
        box_rect = pygame.Rect(
            (WIDTH - max_width - 40) // 2,
            (HEIGHT - total_height) // 2,
            max_width + 40,
            total_height + 40
        )
        
        # Main game loop for the blocking message
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            
            # Draw the current game state
            self.draw()
            
            # Draw the overlay and message box
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, (50, 50, 50), box_rect)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)
            
            # Draw each line of text
            y_offset = box_rect.y + 20
            for i, line in enumerate(lines):
                if i == 0:  # First line is the title
                    text_surface = title_font.render(line, True, (255, 255, 255))
                else:
                    text_surface = text_font.render(line, True, (255, 255, 255))
                text_rect = text_surface.get_rect(centerx=box_rect.centerx, y=y_offset)
                screen.blit(text_surface, text_rect)
                y_offset += line_heights[i] + 10
                
            # Draw instruction to continue
            continue_text = text_font.render("Press any key or click to continue...", True, (200, 200, 200))
            continue_rect = continue_text.get_rect(centerx=box_rect.centerx, 
                                                 y=box_rect.bottom - 30)
            screen.blit(continue_text, continue_rect)
            
            pygame.display.flip()
            pygame.time.delay(30)  # Cap at ~33 FPS to reduce CPU usage
    
    def update(self):
        """Update board state, called once per frame."""
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message_history = []  # Clear all messages when timer expires
    
    def draw_disease_cubes(self):
        """Display the current disease cube counts on the screen."""
        # Position in top right corner
        start_x = WIDTH - 150
        start_y = 20
        cube_size = 20
        margin = 10
        
        # Draw title
        title = self.font.render("Disease Cubes:", True, (255, 255, 255))
        screen.blit(title, (start_x, start_y))
        
        # Draw each disease cube count
        for i, (color_name, color) in enumerate(self.disease_colors.items()):
            # Count cubes of this color across all cities
            cube_count = sum(city.disease_quantity for city in self.game.cities 
                           if hasattr(city, 'disease') and city.disease.color == color_name)
            
            # Draw colored rectangle for the disease
            y_pos = start_y + 30 + i * (cube_size + margin)
            pygame.draw.rect(screen, color, (start_x, y_pos, cube_size, cube_size))
            pygame.draw.rect(screen, (255, 255, 255), (start_x, y_pos, cube_size, cube_size), 1)
            
            # Draw cube count
            count_text = self.small_font.render(f"{color_name}: {cube_count}", True, (255, 255, 255))
            screen.blit(count_text, (start_x + cube_size + 10, y_pos + 5))
    
    def draw_player_hand(self):
        """Draw the current player's hand in the bottom right corner."""
        player = self.game.get_current_player()
        if not player or not hasattr(player, 'hand') or not player.hand:
            return
            
        # Calculate starting position (bottom right corner)
        start_x = WIDTH - 20
        y = HEIGHT - 60
        
        # Filter out non-city cards (like Epidemic cards which are removed when drawn)
        city_cards = [card for card in player.hand if hasattr(card, 'city')]
        
        # Draw hand label with actual number of city cards
        hand_text = self.small_font.render(f"{player.name}'s Hand ({len(city_cards)}/7):", True, (255, 255, 255))
        screen.blit(hand_text, (start_x - 100, y - 15))
        
        # Draw cards from right to left
        for i, card in enumerate(reversed(city_cards)):
            x = start_x - ((i + 1) * (self.card_width + self.card_margin))
            
            # Get card color from city's disease
            color = self.disease_colors.get(card.city.disease.color, (150, 150, 150))
            
            # Draw card as a simple colored rectangle
            pygame.draw.rect(screen, color, (x, y, self.card_width, self.card_height))
            pygame.draw.rect(screen, (255, 255, 255), (x, y, self.card_width, self.card_height), 1)
    
    def draw_messages(self):
        """Draw all active messages on the screen."""
        if not self.message_history or self.message_timer <= 0:
            return
            
        # Starting y-position for the first message
        y_offset = 30
        message_spacing = 5
        
        # Draw each message in history
        for i, message in enumerate(self.message_history):
            if i >= self.max_messages:
                break
                
            # Calculate message position (centered at top of screen, stacked vertically)
            message_surface = self.font.render(message, True, (255, 255, 255))
            message_rect = message_surface.get_rect(center=(WIDTH // 2, y_offset + i * (message_surface.get_height() + message_spacing)))
            
            # Draw semi-transparent background for better readability
            bg_rect = message_rect.inflate(20, 10)
            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            # Make older messages more transparent
            alpha = max(100, 180 - (i * 40))  # Decrease alpha for older messages
            s.fill((0, 0, 0, alpha))
            screen.blit(s, bg_rect)
            
            # Draw message text
            screen.blit(message_surface, message_rect)



    def _get_city_color(self, city):
        """Get the color based on the city's disease color"""
        return self.disease_colors.get(city.disease.color, GRAY)


    def draw(self):
        """Draw the game board"""
        # Update board state
        self.update()
        
        # Clear the screen
        # Retro 80s arcade style background with nebula, vignette, and starfield
        import time, math, random
        t = time.time()
        screen.fill((0, 0, 0))
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = screen.get_width(), screen.get_height()
        
        # Draw messages on top of everything
        self.draw_messages()
        
        # Draw disease cubes counter
        self.draw_disease_cubes()
        
        # Draw player hand
        self.draw_player_hand()

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
            
            # Display infection level and outbreaks in the left menu
            infection_text = self.font.render(f"Infection Level: {self.game.infectionLevel}", True, (255, 100, 100))
            screen.blit(infection_text, (20, y + 10))
            
            # Display outbreaks counter (turns red when >= 5)
            outbreak_color = (255, 100, 100) if self.game.outbreaks >= 5 else (255, 255, 255)
            outbreak_text = self.font.render(f"Outbreaks: {self.game.outbreaks}/8", True, outbreak_color)
            screen.blit(outbreak_text, (20, y + 30))
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

        # Removed first iteration of drawing cities
        # Show current player info
        player = self.game.get_current_player() if self.game.players else None
        if player:
            # Draw current player info
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
                        neon_base = self._get_city_color(city)
                        shadow = tuple(max(0, c - 40) for c in neon_base)  # Darker version for shadow
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
            
            # If move mode and this city is a neighbor, highlight it with a green circle
            if self.move_mode and city in self.highlighted_cities:
                pygame.draw.circle(screen, (0,255,0), (city_x, city_y), 20, 4)  # Green highlight
            
            # Draw pixelated shadow under city
            pygame.draw.circle(screen, (40,40,40), (city_x, city_y+6), 13)
            # Animate city pulse (smaller, faster)
            city_idx = self.game.cities.index(city)
            node_pulse = 0.85 + 0.15 * math.sin(t*5 + city_idx)
            
            # Get base color and apply pulse effect
            base_color = (0, 255, 0) if city.disease.has_cure else self._get_city_color(city)
            neon = tuple(min(255, int(c * node_pulse)) for c in base_color)
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
            # Draw disease cube indicators (small circles below the city)
            if city.disease_quantity > 0:
                cube_color = self.disease_colors.get(city.disease.color, (100, 100, 100))
                
                # Position the cube indicators in a small arc below the city
                for i in range(city.disease_quantity):
                    # Calculate position in a small arc (3 cubes max per row)
                    row = i // 3
                    col = i % 3 - 1  # -1, 0, 1 for positioning
                    cube_x = city_x + col * 6
                    cube_y = city_y + 15 + row * 6
                    
                    # Draw a small circle for each disease cube
                    pygame.draw.circle(screen, cube_color, (cube_x, cube_y), 3)
                    pygame.draw.circle(screen, (255, 255, 255), (cube_x, cube_y), 3, 1)  # White outline
            
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
                        elif action in ['treat_disease', 'find_cure']:
                            # Pass the board reference for these actions to show messages
                            self.game.perform_action(action, board=self)
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