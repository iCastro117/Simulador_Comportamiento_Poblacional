# components.py
import pygame
from config import COLORS

class Button:
    def __init__(self, x, y, width, height, text, color=COLORS["accent"], hover_color=COLORS["accent_hover"]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_active = False

    def draw(self, surface, fonts):
        # Sombra sutil
        pygame.draw.rect(surface, COLORS["shadow"], self.rect.inflate(2, 2), border_radius=8)
        # Botón principal
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=8)
        text_surf = fonts["medium"].render(self.text, True, COLORS["text_dark"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.current_color = self.hover_color if self.rect.collidepoint(pos) else self.color
        return self.rect.collidepoint(pos)

class Slider:
    def __init__(self, x, y, width, height, min_value, max_value, value, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.label = label
        self.dragging = False

    def draw(self, surface, fonts):
        # Barra del slider
        pygame.draw.rect(surface, (200, 200, 210), self.rect, border_radius=5)
        # Relleno de la barra
        fill_width = (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, COLORS["accent"], fill_rect, border_radius=5)
        # Control deslizante
        knob_x = self.rect.x + fill_width
        pygame.draw.circle(surface, COLORS["blue"], (int(knob_x), self.rect.centery), 10)
        # Etiqueta y valor
        if self.label:
            label_surf = fonts["small"].render(f"{self.label}: {self.value:.1f}", True, COLORS["text_dark"])
            surface.blit(label_surf, (self.rect.x, self.rect.y - 20))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
            return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.width))
            self.value = self.min_value + (rel_x / self.rect.width) * (self.max_value - self.min_value)
            return True
        return False

class TextField:
    def __init__(self, x, y, width, height, text="", placeholder="", label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.placeholder = placeholder
        self.label = label
        self.active = False
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.font = pygame.font.Font(None, 32)
        self.max_length = 4  # Máximo 4 dígitos (para números hasta 9999)

    def handle_event(self, event, fonts):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activar/desactivar el campo al hacer clic
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
            return self.active  # Devuelve True si el campo fue activado

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < self.max_length:
                self.text += event.unicode
            return True  # Indica que el evento fue manejado

        return False

    def draw(self, surface, fonts):
        # Dibujar label
        if self.label:
            label_surf = fonts["small"].render(self.label, True, COLORS["text_dark"])
            surface.blit(label_surf, (self.rect.x, self.rect.y - 25))

        # Dibujar el rectángulo del campo
        pygame.draw.rect(surface, self.color, self.rect, 2)

        # Texto a mostrar (texto ingresado o placeholder)
        display_text = self.text if self.text or self.active else self.placeholder
        text_color = COLORS["text_dark"] if (self.text or self.active) else (150, 150, 150)

        # Renderizar texto con recorte si es demasiado largo
        text_surface = fonts["small"].render(display_text, True, text_color)

        # Ajustar posición del texto para que no se salga del campo
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(text_surface, text_rect)

        # Mostrar cursor parpadeante cuando está activo
        if self.active and int(pygame.time.get_ticks() / 300) % 2 == 0:
            cursor_x = text_rect.right + 2
            pygame.draw.line(surface, COLORS["text_dark"],
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.y + self.rect.height - 5), 2)

class DropDown:
    def __init__(self, x, y, width, height, options, selected_index=0, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = selected_index
        self.label = label
        self.expanded = False

    def draw(self, surface, fonts):
        # Fondo principal
        pygame.draw.rect(surface, (230, 230, 240), self.rect, border_radius=5)
        pygame.draw.rect(surface, (200, 200, 210), self.rect, 2, border_radius=5)

        # Texto seleccionado
        text_surf = fonts["small"].render(self.options[self.selected_index][1], True, COLORS["text_dark"])
        surface.blit(text_surf, (self.rect.x + 10, self.rect.centery - text_surf.get_height()//2))

        # Flecha indicadora
        arrow_points = [
            (self.rect.right - 15, self.rect.centery - 3),
            (self.rect.right - 10, self.rect.centery + 2),
            (self.rect.right - 5, self.rect.centery - 3)
        ]
        pygame.draw.polygon(surface, COLORS["text_dark"], arrow_points)

        # Etiqueta
        if self.label:
            label_surf = fonts["small"].render(self.label, True, COLORS["text_dark"])
            surface.blit(label_surf, (self.rect.x, self.rect.y - 20))

        # Opciones desplegables
        if self.expanded:
            for i, (key, option) in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(surface, (240, 240, 250), option_rect)
                pygame.draw.rect(surface, (200, 200, 210), option_rect, 1)
                option_text = fonts["small"].render(option, True, COLORS["text_dark"])
                surface.blit(option_text, (option_rect.x + 10, option_rect.centery - option_text.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True
            if self.expanded:
                for i, (key, _) in enumerate(self.options):
                    option_rect = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.height, self.rect.width, self.rect.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.expanded = False
                        return True
                self.expanded = False
        return False

    def get_selected_value(self):
        return self.options[self.selected_index][0]

class Checkbox:
    def __init__(self, x, y, width, height, text, checked=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.checked = checked

    def draw(self, surface, fonts):
        # Fondo del checkbox
        pygame.draw.rect(surface, (230, 230, 240), self.rect, border_radius=4)
        pygame.draw.rect(surface, (200, 200, 210), self.rect, 2, border_radius=4)

        # Marca de verificación
        if self.checked:
            check_rect = self.rect.inflate(-8, -8)
            pygame.draw.rect(surface, COLORS["green"], check_rect, border_radius=2)

        # Texto
        text_surf = fonts["small"].render(self.text, True, COLORS["text_dark"])
        surface.blit(text_surf, (self.rect.right + 10, self.rect.centery - text_surf.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.checked = not self.checked
            return True
        return False

class Tooltip:
    def __init__(self, text):
        self.text = text

    def draw(self, surface, pos, fonts):
        tooltip_font = fonts["small"]
        text_surf = tooltip_font.render(self.text, True, COLORS["text_dark"])
        text_rect = text_surf.get_rect(topleft=(pos[0] + 15, pos[1] + 15))

        # Fondo con sombra
        bg_rect = text_rect.inflate(15, 10)
        pygame.draw.rect(surface, (220, 220, 230), bg_rect, border_radius=4)
        pygame.draw.rect(surface, (180, 180, 190), bg_rect, 1, border_radius=4)

        # Texto
        surface.blit(text_surf, text_rect)
