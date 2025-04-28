# config.py
COLORS = {
    "background": (240, 240, 245),
    "panel_bg": (250, 250, 255),
    "accent": (70, 130, 200),
    "accent_hover": (50, 110, 180),
    "blue": (50, 120, 200),
    "red": (200, 80, 80),
    "green": (80, 180, 120),
    "orange": (220, 150, 80),
    "text_dark": (40, 40, 40),
    "shadow": (210, 210, 210),
    "person_default": (100, 170, 220),
    "person_fallen": (180, 60, 60),
    "person_reached": (80, 180, 80),
    "person_highlight": (220, 150, 80)
}

# Dimensiones
WIDTH = 1400
HEIGHT = 800
TOP_BAR_HEIGHT = 70

SIM_WIDTH = 1000
SIM_HEIGHT = HEIGHT - TOP_BAR_HEIGHT

CONTROL_PANEL_WIDTH = WIDTH - SIM_WIDTH
PANEL_ELEMENT_WIDTH = CONTROL_PANEL_WIDTH - 40

# Parámetros de simulación
DEFAULT_PARAMS = {
    "personal_space": 12,
    "preferred_speed": 1.3,
    "max_speed": 2.5,
    "panic_threshold": 0.7,
    "cooperation": 0.8,
    "update_interval": 50
}

# Opciones de visualización
VISUALIZATIONS = {
    "none": "None",
    "density": "Densidad",
    "heatmap": "Mapa de calor",
}
