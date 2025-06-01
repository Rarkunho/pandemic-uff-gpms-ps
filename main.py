import pygame
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

def main():
    """Main game loop"""
    clock = pygame.time.Clock()
    from board import WIDTH, HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Pandemic")
    game = Game()
    game.set_game_initial_state()
    board = Board(game)
    game.start_game() 

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            board.handle_event(event)

        screen.fill(WHITE)
        board.draw()

        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()