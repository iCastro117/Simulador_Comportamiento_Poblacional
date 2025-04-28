# logic.py - Versión mejorada con detección de obstáculos

import pygame
import random
import numpy as np
from config import COLORS, WIDTH, HEIGHT, BAR_HEIGHT

class CrowdPerson:
    def __init__(self, x, y, target, velocity=1.5, map_manager=None):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.desired_speed = velocity
        self.mass = 60
        self.target = pygame.Vector2(target)
        self.radius = 4
        self.color = COLORS["green"]
        self.collision_radius = 10
        self.fallen = False
        self.reached_target = False
        self.map_manager = map_manager
        self.path = []
        self.current_path_index = 0
        self.random_move_counter = 0
        self.stuck_counter = 0
        self.last_pos = pygame.Vector2(x, y)
        self.path_update_counter = 0
        
        # Añadir variación de color para mejor visualización
        r = min(255, 50 + int(velocity * 20))
        g = min(255, 150 + int(velocity * 10))
        b = 50
        self.color = (r, g, b)
        
        # Planificar ruta inicial
        if map_manager:
            self.plan_path()

    def plan_path(self):
        """Planifica una ruta desde la posición actual hasta el objetivo"""
        if not self.map_manager:
            return
            
        # Generar camino
        self.path = self.map_manager.find_path(
            (int(self.pos.x), int(self.pos.y)), 
            (int(self.target.x), int(self.target.y))
        )
        self.current_path_index = 0
        self.path_update_counter = random.randint(100, 200)  # Actualizar ruta cada cierto tiempo

    def desired_direction(self):
        """Calcula la dirección deseada basada en el camino o el objetivo"""
        # Decrementar contador de actualización de ruta
        if self.path_update_counter > 0:
            self.path_update_counter -= 1
            if self.path_update_counter == 0:
                self.plan_path()  # Replanificar ruta periódicamente
        
        # Si no hay camino o llegamos al final, ir directo al objetivo
        if not self.path or self.current_path_index >= len(self.path):
            direction = (self.target - self.pos)
            distance = direction.length()
            
            # Verificar si ha llegado al objetivo
            if distance < 15:
                self.reached_target = True
                return pygame.Vector2(0, 0)
                
            if distance != 0:
                return direction.normalize()
            return pygame.Vector2(0, 0)
        
        # Seguir el camino
        next_point = self.path[self.current_path_index]
        direction = next_point - self.pos
        distance = direction.length()
        
        # Si llegamos al punto actual del camino, avanzar al siguiente
        if distance < 10:
            self.current_path_index += 1
            # Si llegamos al final del camino, planificar uno nuevo
            if self.current_path_index >= len(self.path):
                if random.random() < 0.3:  # 30% de probabilidad de movimiento aleatorio
                    self.random_move()
                else:
                    self.plan_path()  # Replanificar ruta
                    
        if distance != 0:
            return direction.normalize()
        return pygame.Vector2(0, 0)

    def random_move(self):
        """Genera un movimiento aleatorio por las calles"""
        if not self.map_manager or not self.map_manager.street_points:
            return
            
        # Elegir un punto aleatorio en las calles
        random_target = self.map_manager.get_random_street_point()
        self.path = self.map_manager.find_path(
            (int(self.pos.x), int(self.pos.y)), 
            random_target
        )
        self.current_path_index = 0
        self.random_move_counter = random.randint(100, 300)  # Contar frames antes de otro movimiento aleatorio

    def acceleration_force(self):
        if self.reached_target:
            # Si llegó al objetivo, reducir velocidad gradualmente
            return -self.vel * 2
            
        desired_velocity = self.desired_direction() * self.desired_speed
        tau = 0.5  # tiempo de reacción
        return (desired_velocity - self.vel) / tau

    def repulsive_force(self, others):
        force = pygame.Vector2(0, 0)
        
        # Optimización: solo considerar personas cercanas
        for other in others:
            if other is self or other.fallen:
                continue
                
            # Cálculo rápido de distancia aproximada para filtrar
            dx = self.pos.x - other.pos.x
            dy = self.pos.y - other.pos.y
            approx_dist_sq = dx*dx + dy*dy
            
            # Solo calcular repulsión para personas cercanas
            if approx_dist_sq < 400:  # 20^2
                diff = self.pos - other.pos
                distance = diff.length()
                if distance < 1e-2:
                    continue
                    
                overlap = self.collision_radius * 2 - distance
                if overlap > 0:
                    repulsion = diff.normalize() * (overlap * 1.2)
                    force += repulsion
                    
        return force
        
    def obstacle_avoidance_force(self):
        """Genera una fuerza de repulsión de los obstáculos"""
        if not self.map_manager:
            return pygame.Vector2(0, 0)
            
        force = pygame.Vector2(0, 0)
        
        # Verificar en varias direcciones alrededor de la persona
        for angle in range(0, 360, 45):
            radians = angle * 3.14159 / 180
            direction = pygame.Vector2(np.cos(radians), np.sin(radians))
            
            # Verificar a diferentes distancias
            for dist in [5, 10, 15]:
                check_pos = self.pos + direction * dist
                x, y = int(check_pos.x), int(check_pos.y)
                
                # Si hay obstáculo, generar fuerza de repulsión
                if self.map_manager.is_obstacle(x, y):
                    # Fuerza inversamente proporcional a la distancia
                    repulsion = -direction * (30 / dist)
                    force += repulsion
                    break
        
        return force

    def update(self, others, dt):
        if self.fallen:
            return
            
        # Verificar si está atascado
        if (self.pos - self.last_pos).length() < 0.5:
            self.stuck_counter += 1
            if self.stuck_counter > 60:  # Si está atascado por 60 frames
                # Intentar encontrar un nuevo camino o moverse aleatoriamente
                if random.random() < 0.7:
                    self.random_move()
                else:
                    self.plan_path()
                self.stuck_counter = 0
        else:
            self.stuck_counter = 0
            
        self.last_pos = pygame.Vector2(self.pos)
            
        # Decrementar contador de movimiento aleatorio
        if self.random_move_counter > 0:
            self.random_move_counter -= 1
            if self.random_move_counter == 0 and random.random() < 0.3:
                self.random_move()
            
        f_accel = self.acceleration_force()
        f_rep = self.repulsive_force(others)
        f_obs = self.obstacle_avoidance_force()

        total_force = f_accel + f_rep + f_obs * 3  # Dar más peso a evitar obstáculos
        self.vel += total_force * dt
        
        # Limitar velocidad máxima para estabilidad
        speed = self.vel.length()
        max_speed = self.desired_speed * 2
        if speed > max_speed:
            self.vel = self.vel * (max_speed / speed)
            
        # Calcular nueva posición
        new_pos = self.pos + self.vel * dt
        
        # Verificar si la nueva posición está en un obstáculo
        if self.map_manager and self.map_manager.is_obstacle(int(new_pos.x), int(new_pos.y)):
            # Si está en un obstáculo, no moverse en esa dirección
            # Intentar moverse solo en la dirección que no está bloqueada
            test_pos_x = pygame.Vector2(new_pos.x, self.pos.y)
            test_pos_y = pygame.Vector2(self.pos.x, new_pos.y)
            
            if not self.map_manager.is_obstacle(int(test_pos_x.x), int(test_pos_x.y)):
                self.pos.x = new_pos.x
            
            if not self.map_manager.is_obstacle(int(test_pos_y.x), int(test_pos_y.y)):
                self.pos.y = new_pos.y
                
            # Replanificar ruta si chocamos con un obstáculo
            self.plan_path()
        else:
            self.pos = new_pos

        # Condición de caída: mucha fuerza o densidad
        if f_rep.length() > 20:
            if random.random() < 0.01:  # probabilidad de caída reducida
                self.fallen = True
                self.color = (150, 0, 0)  # rojo oscuro
                self.vel = pygame.Vector2(0, 0)
                
        # Cambiar color según velocidad
        if not self.fallen and not self.reached_target:
            speed = self.vel.length()
            intensity = min(255, int(50 + speed * 40))
            self.color = (intensity, min(255, 100 + intensity), 50)

    def draw(self, surface):
        # Dibujar persona
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Dibujar indicador de dirección (opcional, para depuración)
        if not self.fallen and not self.reached_target and self.vel.length() > 0.5:
            direction = self.vel.normalize() * 8
            end_pos = (int(self.pos.x + direction.x), int(self.pos.y + direction.y))
            pygame.draw.line(surface, (50, 50, 50), (int(self.pos.x), int(self.pos.y)), end_pos, 1)