# person.py
import pygame
import random
import math
from config import COLORS, SIM_WIDTH, SIM_HEIGHT, TOP_BAR_HEIGHT

class Person:
    def __init__(self, pos, target, params, map_manager=None):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.target = pygame.Vector2(target)
        self.original_target = pygame.Vector2(target)

        # Parámetros de comportamiento
        self.desired_speed = params["preferred_speed"] * random.uniform(0.8, 1.2)
        self.max_speed = params["max_speed"]
        self.mass = random.uniform(50, 80)
        self.personal_space = params["personal_space"] * random.uniform(0.9, 1.1)
        self.cooperation = random.uniform(0.6, 1.0)
        self.panic_level = 0.0
        self.patience = random.uniform(0.7, 1.0)
        self.decisiveness = random.uniform(0.6, 1.0)

        # Atributos físicos
        self.radius = 4
        self.collision_radius = 8
        self.color = self._get_color()
        self.energy = 100.0

        # Estado
        self.fallen = False
        self.reached_target = False
        self.stuck = False
        self.stuck_counter = 0
        self.recoverable = True
        self.recovery_counter = 0
        self.avoiding_obstacle = False

        # Navegación
        self.map_manager = map_manager
        self.path = []
        self.current_path_index = 0
        self.path_update_counter = random.randint(20, 50)
        self.last_pos = pygame.Vector2(pos)
        self.random_move_counter = 0
        self.intermediate_targets = []

        # Visualización
        self.history = []
        self.max_history = 15
        self.fallen_history = []

    def _get_color(self):
        speed_factor = self.desired_speed / self.max_speed
        r = min(255, int(COLORS["person_default"][0] + speed_factor * 40))
        g = min(255, int(COLORS["person_default"][1] + speed_factor * 20))
        b = max(0, int(COLORS["person_default"][2] - speed_factor * 50))
        return (r, g, b)

    def plan_path(self):
        if not self.map_manager:
            return

        self.path = self.map_manager.find_path(
            (int(self.pos.x), int(self.pos.y)),
            (int(self.target.x), int(self.target.y))
        )
        self.current_path_index = 0

        if not self.path:
            direction = self.target - self.pos
            if direction.length() > 0:
                direction.normalize_ip()
                distance = min(200, (self.target - self.pos).length() * 0.6)
                intermediate = self.pos + direction * distance
                intermediate = self.map_manager.find_nearest_street((int(intermediate.x), int(intermediate.y)))
                self.path = self.map_manager.find_path(
                    (int(self.pos.x), int(self.pos.y)),
                    intermediate
                )
                if self.path:
                    self.intermediate_targets.append(intermediate)

    def desired_direction(self):
        if self.path_update_counter > 0:
            self.path_update_counter -= 1
            if self.path_update_counter == 0:
                self.plan_path()
                self.path_update_counter = random.randint(20, 50)

        if self.reached_target:
            return pygame.Vector2(0, 0)

        if not self.path or self.current_path_index >= len(self.path):
            direction = self.target - self.pos
            distance = direction.length()

            if distance < 20:
                self.reached_target = True
                self.color = COLORS["person_reached"]
                return pygame.Vector2(0, 0)

            if self.intermediate_targets and distance > 100:
                self.plan_path()

            if distance > 0:
                direct_path = direction.normalize()
                test_pos = self.pos + direct_path * 20
                if not self.map_manager or not self.map_manager.is_obstacle(int(test_pos.x), int(test_pos.y)):
                    return direct_path
                else:
                    self.avoiding_obstacle = True
                    for angle in [30, -30, 60, -60, 90, -90]:
                        radians = angle * math.pi / 180
                        test_dir = pygame.Vector2(
                            direct_path.x * math.cos(radians) - direct_path.y * math.sin(radians),
                            direct_path.x * math.sin(radians) + direct_path.y * math.cos(radians)
                        )
                        test_pos = self.pos + test_dir * 20
                        if not self.map_manager.is_obstacle(int(test_pos.x), int(test_pos.y)):
                            return test_dir

                    if random.random() < 0.1:
                        angle = random.uniform(0, 360) * math.pi / 180
                        return pygame.Vector2(math.cos(angle), math.sin(angle))

                    return pygame.Vector2(0, 0)

            return pygame.Vector2(0, 0)

        next_point = self.path[self.current_path_index]
        direction = next_point - self.pos
        distance = direction.length()

        if distance < 10:
            self.current_path_index += 1
            self.avoiding_obstacle = False

            if self.current_path_index >= len(self.path):
                if self.intermediate_targets:
                    self.intermediate_targets.pop(0)
                    self.pos = pygame.Vector2(next_point)
                    self.plan_path()

        if distance > 0:
            return direction.normalize()

        return pygame.Vector2(0, 0)

    def random_move(self):
        if not self.map_manager or not self.map_manager.street_points:
            return

        random_target = self.map_manager.get_random_street_point()
        self.path = self.map_manager.find_path(
            (int(self.pos.x), int(self.pos.y)),
            random_target
        )
        self.current_path_index = 0
        self.random_move_counter = random.randint(100, 300)

    def acceleration_force(self):
        if self.reached_target or self.fallen:
            return -self.vel * 0.5

        desired_direction = self.desired_direction()
        current_max_speed = self.max_speed * (1 + self.panic_level * 0.5) * (self.energy / 100)
        desired_velocity = desired_direction * min(self.desired_speed, current_max_speed)

        tau = 0.5 * (1 + self.panic_level * 0.5)

        if self.stuck:
            return (desired_velocity - self.vel) / tau * 1.5

        return (desired_velocity - self.vel) / tau

    def repulsive_force(self, others):
        force = pygame.Vector2(0, 0)
        nearby_people = [other for other in others
                        if other is not self and
                           (other.pos - self.pos).length_squared() < 900]

        for other in nearby_people:
            if other.fallen and not other.recoverable:
                diff = self.pos - other.pos
                dist = diff.length()
                if dist < 1:
                    continue

                avoidance_radius = (self.collision_radius + other.collision_radius * 2) * self.personal_space
                if dist < avoidance_radius:
                    repulsion_strength = 20 * (avoidance_radius - dist) / avoidance_radius
                    force += diff.normalize() * repulsion_strength

            elif not other.fallen:
                diff = self.pos - other.pos
                dist = diff.length()
                if dist < 1:
                    continue

                avoidance_radius = (self.collision_radius + other.collision_radius) * self.personal_space
                if dist < avoidance_radius:
                    repulsion_strength = 10 * (avoidance_radius - dist) / avoidance_radius
                    repulsion_strength *= (2 - self.cooperation) * (1 + self.panic_level)
                    force += diff.normalize() * repulsion_strength

                    if dist < avoidance_radius * 0.5:
                        self.panic_level = min(1.0, self.panic_level + 0.01)

        return force

    def obstacle_avoidance_force(self):
        if not self.map_manager:
            return pygame.Vector2(0, 0)

        force = pygame.Vector2(0, 0)

        if self.vel.length_squared() > 0.1:
            look_dir = self.vel.normalize()
        else:
            look_dir = self.desired_direction()
            if look_dir.length_squared() < 0.1:
                angles = [0, 45, 90, 135, 180, 225, 270, 315]
                for angle in angles:
                    rad = math.radians(angle)
                    check_dir = pygame.Vector2(math.cos(rad), math.sin(rad))
                    for distance in [5, 10, 15, 20]:
                        check_pos = self.pos + check_dir * distance

                        if self.map_manager.is_obstacle(int(check_pos.x), int(check_pos.y)):
                            repulsion = -check_dir * (30 / distance)
                            force += repulsion
                return force

        for distance in [10, 20, 30]:
            check_pos = self.pos + look_dir * distance
            if self.map_manager.is_obstacle(int(check_pos.x), int(check_pos.y)):
                force += -look_dir * (50 / distance)

                for angle in [30, -30, 60, -60]:
                    rad = math.radians(angle)
                    side_dir = pygame.Vector2(
                        look_dir.x * math.cos(rad) - look_dir.y * math.sin(rad),
                        look_dir.x * math.sin(rad) + look_dir.y * math.cos(rad)
                    )
                    side_pos = self.pos + side_dir * distance

                    if not self.map_manager.is_obstacle(int(side_pos.x), int(side_pos.y)):
                        force += side_dir * (30 / distance)

                break

        return force

    def update(self, others, dt, global_panic=0):
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append(pygame.Vector2(self.pos))

        if self.fallen:
            if self.recoverable:
                self.recovery_counter += dt
                if self.recovery_counter > 5:
                    self.fallen = False
                    self.recovery_counter = 0
                    self.color = self._get_color()
                    self.energy = 70
            else:
                if len(self.fallen_history) < 3:
                    self.fallen_history.append(pygame.Vector2(self.pos))
            return

        self.panic_level = min(1.0, self.panic_level * 0.99 + global_panic * 0.1)

        displacement = (self.pos - self.last_pos).length()
        if displacement < 0.5 * dt * 60:
            self.stuck_counter += 1
            if self.stuck_counter > 120:
                self.stuck = True

                if random.random() < self.decisiveness:
                    if random.random() < 0.7:
                        self.random_move()
                    else:
                        self.plan_path()

                self.stuck_counter = 0
        else:
            self.stuck_counter = 0
            self.stuck = False

        self.last_pos = pygame.Vector2(self.pos)

        if self.random_move_counter > 0:
            self.random_move_counter -= 1
            if self.random_move_counter == 0 and random.random() < 0.2:
                self.random_move()

        self.acceleration = pygame.Vector2(0, 0)
        self.acceleration += self.acceleration_force()
        self.acceleration += self.repulsive_force(others)
        self.acceleration += self.obstacle_avoidance_force() * 2.0

        if not self.avoiding_obstacle and random.random() < 0.01:
            angle = random.uniform(0, 360) * math.pi / 180
            self.acceleration += pygame.Vector2(math.cos(angle), math.sin(angle)) * 0.5

        self.vel += self.acceleration * dt

        speed = self.vel.length()
        if speed > self.max_speed:
            self.vel = self.vel * (self.max_speed / speed)

        new_pos = self.pos + self.vel * dt
        new_pos.x = max(0, min(SIM_WIDTH, new_pos.x))
        new_pos.y = max(TOP_BAR_HEIGHT, min(SIM_HEIGHT, new_pos.y))

        if self.map_manager and self.map_manager.is_obstacle(int(new_pos.x), int(new_pos.y)):
            test_x = pygame.Vector2(new_pos.x, self.pos.y)
            test_y = pygame.Vector2(self.pos.x, new_pos.y)

            x_valid = not self.map_manager.is_obstacle(int(test_x.x), int(test_x.y))
            y_valid = not self.map_manager.is_obstacle(int(test_y.x), int(test_y.y))

            if x_valid:
                self.pos.x = new_pos.x
            if y_valid:
                self.pos.y = new_pos.y

            self.vel *= 0.7
            self.energy -= 0.5

            if random.random() < 0.1:
                self.plan_path()
        else:
            self.pos = new_pos

        self.energy -= 0.01 * (1 + speed / self.max_speed)
        self.energy = max(0, min(100, self.energy))

        fall_probability = 0.001

        repulsive_magnitude = self.acceleration.length()
        if repulsive_magnitude > 10:
            fall_probability += 0.01 * (repulsive_magnitude / 10)

        if self.energy < 30:
            fall_probability += 0.01 * (1 - self.energy / 30)

        fall_probability += 0.01 * self.panic_level

        if random.random() < fall_probability * dt * 10:
            self.fallen = True
            self.vel = pygame.Vector2(0, 0)
            self.color = COLORS["person_fallen"]
            self.recoverable = random.random() < 0.7

        if not self.fallen and not self.reached_target:
            if self.stuck:
                self.color = COLORS["person_highlight"]
            elif self.panic_level > 0.5:
                r = min(255, int(200 + self.panic_level * 55))
                g = max(0, int(100 - self.panic_level * 100))
                b = max(0, int(80 - self.panic_level * 80))
                self.color = (r, g, b)
            else:
                speed_ratio = min(1.0, self.vel.length() / self.max_speed)
                base_color = COLORS["person_default"]
                r = min(255, int(base_color[0] + speed_ratio * 70))
                g = min(255, int(base_color[1] + speed_ratio * 20))
                b = max(0, int(base_color[2] - speed_ratio * 50))
                self.color = (r, g, b)

    def draw(self, surface, draw_vectors=False, draw_trails=True, draw_fallen_trails=True):
        if draw_trails and len(self.history) > 1 and not self.fallen and not self.reached_target:
            alpha = 50
            for i in range(len(self.history) - 1):
                alpha_factor = (i + 1) / len(self.history)
                trail_color = (
                    self.color[0],
                    self.color[1],
                    self.color[2],
                    int(alpha * alpha_factor)
                )
                start = (int(self.history[i].x), int(self.history[i].y))
                end = (int(self.history[i+1].x), int(self.history[i+1].y))

                line_surface = pygame.Surface((SIM_WIDTH, SIM_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(line_surface, trail_color, start, end, 2)
                surface.blit(line_surface, (0, 0))

        if draw_fallen_trails and self.fallen and len(self.fallen_history) > 0:
            for pos in self.fallen_history:
                pygame.draw.circle(surface, (200, 50, 50, 100), (int(pos.x), int(pos.y)), 3)

        if self.fallen:
            center = (int(self.pos.x), int(self.pos.y))
            size = self.radius * 1.5
            pygame.draw.line(surface, self.color,
                            (center[0] - size, center[1] - size),
                            (center[0] + size, center[1] + size), 2)
            pygame.draw.line(surface, self.color,
                            (center[0] - size, center[1] + size),
                            (center[0] + size, center[1] - size), 2)
        else:
            pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

        if draw_vectors and self.vel.length() > 0.1:
            vec_end = self.pos + self.vel.normalize() * 15
            pygame.draw.line(surface, COLORS["blue"],
                            (int(self.pos.x), int(self.pos.y)),
                            (int(vec_end.x), int(vec_end.y)), 1)

        if draw_vectors and self.acceleration.length() > 0.1:
            acc_end = self.pos + self.acceleration.normalize() * 10
            pygame.draw.line(surface, COLORS["red"],
                            (int(self.pos.x), int(self.pos.y)),
                            (int(acc_end.x), int(acc_end.y)), 1)
