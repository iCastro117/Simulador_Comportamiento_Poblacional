# main.py
import pygame
import random
import sys
import time
from config import (
    COLORS, WIDTH, HEIGHT, TOP_BAR_HEIGHT, SIM_WIDTH, SIM_HEIGHT,
    CONTROL_PANEL_WIDTH, PANEL_ELEMENT_WIDTH, DEFAULT_PARAMS, VISUALIZATIONS
)
from person import Person
from map_utils import MapManager
from ui import draw_top_bar, draw_control_panel, init_fonts, draw_interface, set_button_position
from components import Button, Slider, TextField, DropDown, Checkbox, Tooltip

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Comportamiento Poblacional")
clock = pygame.time.Clock()

# Estado global
simulation_running = False
simulation_paused = False
simulation_speed = 1.0
simulation_time = 0.0  # Asegúrate de que esté inicializada
people = []
meet_points = []
start_point = None
current_mode = None
visualization_mode = "none"
show_vectors = False
show_trails = True
show_fallen_trails = False
current_tooltip = None
tooltip_timer = 0
density_map = None

fonts = init_fonts()

# Cargar mapa
try:
    map_image = pygame.image.load("assets/mapa.png")
    map_image = pygame.transform.scale(map_image, (SIM_WIDTH, SIM_HEIGHT))
except:
    # Crear un mapa predeterminado si no se encuentra la imagen
    map_image = pygame.Surface((SIM_WIDTH, SIM_HEIGHT))
    map_image.fill(COLORS["panel_bg"])
    pygame.draw.rect(map_image, (200, 200, 210), (0, 0, SIM_WIDTH, SIM_HEIGHT), 2)

map_manager = MapManager(map_image)

# Botones superiores
top_buttons = [
    Button(WIDTH // 2 - 160, 20, 120, 40, "Punto Inicio", color=COLORS["blue"], hover_color=COLORS["accent_hover"]),
    Button(WIDTH // 2 - 20, 20, 120, 40, "Punto Encuentro", color=COLORS["red"], hover_color=(200, 100, 100)),
    Button(WIDTH // 2 + 120, 20, 120, 40, "Iniciar Simulación", color=COLORS["green"], hover_color=(60, 180, 100)),
]

# Elementos del panel de control
control_panel_elements = []

speed_slider = Slider(SIM_WIDTH + 20, 100, PANEL_ELEMENT_WIDTH, 20, 0.5, 5.0, 1.0, "Velocidad")
people_input = TextField(SIM_WIDTH + 20, 160, PANEL_ELEMENT_WIDTH, 35, "100", "Ingrese número", "Nº Personas")
visualization_dropdown = DropDown(SIM_WIDTH + 20, 230, PANEL_ELEMENT_WIDTH, 35,
                                [(key, value) for key, value in VISUALIZATIONS.items()], 0, "Visualización")
vectors_checkbox = Checkbox(SIM_WIDTH + 20, 300, 20, 20, "Mostrar vectores de movimiento", False)
trails_checkbox = Checkbox(SIM_WIDTH + 20, 340, 20, 20, "Mostrar rastros de movimiento", True)
fallen_trails_checkbox = Checkbox(SIM_WIDTH + 20, 380, 20, 20, "Mostrar rastros de bajas", False)

control_panel_elements.extend([
    speed_slider,
    people_input,
    visualization_dropdown,
    vectors_checkbox,
    trails_checkbox,
    fallen_trails_checkbox
])

tooltips = {
    speed_slider: "Controla la velocidad de la simulación",
    people_input: "Número de personas en la simulación",
    visualization_dropdown: "Tipo de visualización adicional",
    vectors_checkbox: "Muestra vectores de dirección y velocidad",
    trails_checkbox: "Muestra el rastro de movimiento de las personas",
    fallen_trails_checkbox: "Muestra dónde han caído personas"
}

def create_person(start_pos, target_pos):
    variation = 10
    x = start_pos[0] + random.uniform(-variation, variation)
    y = start_pos[1] + random.uniform(-variation, variation)
    if map_manager.is_obstacle(int(x), int(y)):
        x, y = map_manager.find_nearest_street((int(x), int(y)))
    return Person((x, y), target_pos, DEFAULT_PARAMS, map_manager)

def start_simulation():
    global simulation_running, people, simulation_time, density_map
    if not start_point or not meet_points:
        print("Error: Debes establecer un punto de inicio y al menos un punto de encuentro")
        return

    try:
        num_people = int(people_input.text)
        if num_people <= 0:
            raise ValueError
    except ValueError:
        print("Error: Número de personas inválido")
        return

    num_people = min(num_people, 2000)  # Límite máximo
    people.clear()

    for _ in range(num_people):
        target = random.choice(meet_points)
        people.append(create_person(start_point, target))

    # Inicializar mapa de densidad
    density_map = {
        'data': [[0 for _ in range(SIM_HEIGHT)] for _ in range(SIM_WIDTH)],
        'max_density': 1  # Evitar división por cero
    }

    simulation_time = 0.0
    simulation_running = True
    print(f"Simulación iniciada con {num_people} personas")

def handle_map_click(pos):
    x, y = pos
    if x >= SIM_WIDTH or y < TOP_BAR_HEIGHT:
        return

    global start_point, meet_points

    # Encontrar el punto más cercano en la calle
    street_pos = map_manager.find_nearest_street((x, y))

    if current_mode == "start_point":
        start_point = street_pos
        print(f"Punto de inicio establecido en {start_point}")
    elif current_mode == "meet_point":
        meet_points.append(street_pos)
        print(f"Punto de encuentro añadido en {street_pos}")

def update_density_map():
    if visualization_mode != "density":
        return

    # Resetear el mapa de densidad
    for x in range(SIM_WIDTH):
        for y in range(SIM_HEIGHT):
            density_map['data'][x][y] = 0

    # Actualizar con las posiciones actuales
    max_density = 1
    for person in people:
        x, y = int(person.pos.x), int(person.pos.y)
        if 0 <= x < SIM_WIDTH and 0 <= y < SIM_HEIGHT:
            density_map['data'][x][y] += 1
            if density_map['data'][x][y] > max_density:
                max_density = density_map['data'][x][y]

    density_map['max_density'] = max_density

def handle_events():
    global current_mode, simulation_running, visualization_mode, show_vectors
    global show_trails, show_fallen_trails, current_tooltip, tooltip_timer, simulation_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            # Botones superiores
            for i, button in enumerate(top_buttons):
                if button.rect.collidepoint(pos):
                    if i == 0:
                        current_mode = "start_point"
                        print("Modo: Establecer punto de inicio")
                    elif i == 1:
                        current_mode = "meet_point"
                        print("Modo: Añadir punto de encuentro")
                    elif i == 2:
                        start_simulation()

            # Clic en el mapa
            if 0 <= pos[0] < SIM_WIDTH and pos[1] >= TOP_BAR_HEIGHT:
                handle_map_click(pos)

            # Elementos del panel de control
            for element in control_panel_elements:
                if isinstance(element, Slider):
                    if element.handle_event(event):
                        if element is speed_slider:
                            simulation_speed = element.value  # Actualizar la velocidad aquí
                elif isinstance(element, Checkbox):
                    if element.handle_event(event):
                        if element is vectors_checkbox:
                            show_vectors = element.checked
                        elif element is trails_checkbox:
                            show_trails = element.checked
                        elif element is fallen_trails_checkbox:
                            show_fallen_trails = element.checked
                elif isinstance(element, DropDown):
                    if element.handle_event(event):
                        visualization_mode = element.get_selected_value()
                        update_density_map()
                elif isinstance(element, TextField):
                    element.handle_event(event, fonts)

        elif event.type == pygame.MOUSEBUTTONUP:
            # Asegurarse de soltar el slider
            if speed_slider.dragging:
                speed_slider.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            current_tooltip = None
            tooltip_timer = 0

            # Verificar hover sobre elementos con tooltip
            for element, tooltip_text in tooltips.items():
                if hasattr(element, 'rect') and element.rect.collidepoint(mouse_pos):
                    current_tooltip = Tooltip(tooltip_text)
                    tooltip_timer = 1.0
                    break

            # Manejar arrastre del slider
            if event.buttons[0]:  # Si el botón izquierdo está presionado
                for element in control_panel_elements:
                    if isinstance(element, Slider) and element.rect.collidepoint(mouse_pos):
                        if element.handle_event(event):
                            if element is speed_slider:
                                simulation_speed = element.value  # Actualizar durante el arrastre

def update_simulation(dt):
    global simulation_time  # Añade esta línea

    if not simulation_running:
        return

    scaled_dt = dt * simulation_speed
    simulation_time += scaled_dt

    for person in people:
        person.update(people, scaled_dt, 0.0)

    # Actualizar visualizaciones
    if visualization_mode == "density":
        update_density_map()

def draw_simulation_area():
    # Fondo del área de simulación
    screen.blit(map_image, (0, TOP_BAR_HEIGHT))

    # Dibujar puntos de inicio y encuentro
    if start_point:
        pygame.draw.circle(screen, COLORS["blue"], start_point, 10)
        pygame.draw.circle(screen, (255, 255, 255), start_point, 6)

    for point in meet_points:
        pygame.draw.circle(screen, COLORS["red"], point, 8)
        pygame.draw.circle(screen, (255, 255, 255), point, 4)

    # Dibujar visualizaciones
    if visualization_mode == "density" and density_map:
        density_surface = pygame.Surface((SIM_WIDTH, SIM_HEIGHT), pygame.SRCALPHA)
        max_density = density_map['max_density']

        for x in range(SIM_WIDTH):
            for y in range(SIM_HEIGHT):
                density = density_map['data'][x][y]
                if density > 0:
                    alpha = min(200, int(200 * density / max_density))
                    pygame.draw.circle(density_surface, (255, 100, 100, alpha), (x, y), 3)

        screen.blit(density_surface, (0, TOP_BAR_HEIGHT))

    # Dibujar personas
    for person in people:
        person.draw(screen, show_vectors, show_trails, show_fallen_trails)

def main():
    global simulation_time  # Puedes añadir esto también por seguridad

    running = True
    prev_time = time.time()

    while running:
        now = time.time()
        dt = now - prev_time
        prev_time = now
        dt = min(dt, 0.05)  # Limitar dt máximo para evitar saltos grandes

        # Manejo de eventos
        handle_events()

        # Actualización de la simulación
        update_simulation(dt)

        # Dibujado
        screen.fill(COLORS["background"])
        draw_simulation_area()  # Dibuja el área de simulación primero
        draw_interface(screen, fonts, top_buttons, control_panel_elements)  # Luego dibuja la interfaz

        # Tooltips siempre encima de todo
        if current_tooltip and tooltip_timer > 0:
            current_tooltip.draw(screen, pygame.mouse.get_pos(), fonts)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
