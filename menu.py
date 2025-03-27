import pygame
import sys

class Menu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.options = ["Spiel starten", "Spiel speichern", "Spiel laden", "Spiel beenden"]
        self.selected_index = 0

    def draw(self):
        self.screen.fill((0, 0, 0))  # Schwarzer Hintergrund
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected_index else (150, 150, 150)
            text_surface = self.font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 300 + i * 50))
            self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected_index]  # Gibt die gewählte Option zurück
        return None