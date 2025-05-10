import pygame

class InputField:
    def __init__(self, x, y, width, height, font, text_color=(255, 255, 255), bg_color=(50, 50, 50), active_color=(80, 80, 80), max_length=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = bg_color
        self.color_active = active_color
        self.color = self.color_inactive
        self.text = ''
        self.font = font
        self.text_color = text_color
        self.txt_surface = font.render(self.text, True, self.text_color)
        self.active = False
        self.max_length = max_length

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable
                self.active = not self.active
            else:
                self.active = False
            # Change the current color
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Add character if not exceeding max length
                    if len(self.text) < self.max_length and event.unicode.isalnum():
                        self.text += event.unicode
                # Re-render the text
                self.txt_surface = self.font.render(self.text, True, self.text_color)
        return None

    def update(self):
        # Resize the box if the text is too long
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Draw the input box
        pygame.draw.rect(screen, self.color, self.rect, 0)
        pygame.draw.rect(screen, self.text_color, self.rect, 2)  # Border
        
        # Draw the text
        text_x = self.rect.x + 5
        text_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2
        screen.blit(self.txt_surface, (text_x, text_y))
