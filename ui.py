# ui.py
import pygame
from config import COLORS, WIDTH, HEIGHT, TOP_BAR_HEIGHT, CONTROL_PANEL_WIDTH, SIM_WIDTH

def init_fonts():
    pygame.font.init()
    return {
        "title": pygame.font.SysFont("Arial", 28, bold=True),
        "large": pygame.font.SysFont("Arial", 22, bold=True),
        "medium": pygame.font.SysFont("Arial", 18),
        "small": pygame.font.SysFont("Arial", 14),
    }

def draw_top_bar(surface, fonts, top_buttons):
    # Fondo de la barra (opaco)
    pygame.draw.rect(surface, COLORS["panel_bg"], (0, 0, WIDTH, TOP_BAR_HEIGHT))

    # Dibujar botones
    for button in top_buttons:
        button.draw(surface, fonts)

    # Título más hacia la izquierda
    title = fonts["title"].render("Simulador de Comportamiento Poblacional", True, COLORS["text_dark"])
    surface.blit(title, (20, 20))  # Ajusta la posición del título

def draw_control_panel(surface, fonts, elements, stats=None):
    panel_x = WIDTH - CONTROL_PANEL_WIDTH
    pygame.draw.rect(surface, COLORS["panel_bg"], (panel_x, 0, CONTROL_PANEL_WIDTH, surface.get_height()))

    # Título del panel
    panel_title = fonts["medium"].render("Controles", True, COLORS["text_dark"])
    surface.blit(panel_title, (panel_x + 20, 70))

    for element in elements:
        element.draw(surface, fonts)

    if stats:
        stats_y = 400
        stats_title = fonts["medium"].render("Estadísticas", True, COLORS["text_dark"])
        surface.blit(stats_title, (panel_x + 20, stats_y))

        for i, (label, value) in enumerate(stats.items()):
            stat_text = fonts["small"].render(f"{label}: {value}", True, COLORS["text_dark"])
            surface.blit(stat_text, (panel_x + 20, stats_y + 30 + i * 25))

def draw_interface(screen, fonts, top_buttons, control_panel_elements, stats=None):
    # Fondo opaco para la barra superior
    pygame.draw.rect(screen, COLORS["panel_bg"], (0, 0, WIDTH, TOP_BAR_HEIGHT))
    draw_top_bar(screen, fonts, top_buttons)

    # Fondo opaco para el panel de control
    pygame.draw.rect(screen, COLORS["panel_bg"], (SIM_WIDTH, 0, CONTROL_PANEL_WIDTH, HEIGHT))
    draw_control_panel(screen, fonts, control_panel_elements, stats)

def set_button_position(button, x, y):
    button.rect.topleft = (x, y)
