# map_utils.py - Enhanced map and pathfinding system

import pygame
import numpy as np
import random
import math
from config import COLORS, SIM_WIDTH, SIM_HEIGHT, TOP_BAR_HEIGHT

class MapManager:
    def __init__(self, map_image):
        self.map_image = map_image
        self.obstacle_map = None
        self.street_points = []
        self.street_graph = {}
        self.debug_surface = pygame.Surface((SIM_WIDTH, SIM_HEIGHT), pygame.SRCALPHA)
        self.density_map = np.zeros((SIM_HEIGHT, SIM_WIDTH))
        self.heatmap_surface = pygame.Surface((SIM_WIDTH, SIM_HEIGHT), pygame.SRCALPHA)
        self.generate_obstacle_map()
        
    def generate_obstacle_map(self):
        """Generates a binary obstacle map from the image"""
        self.obstacle_map = np.zeros((SIM_HEIGHT, SIM_WIDTH), dtype=bool)
        
        # Temporary surface for pixel access
        map_surface = pygame.Surface((SIM_WIDTH, SIM_HEIGHT))
        map_surface.blit(self.map_image, (0, 0))
        
        # Sample pixels to identify obstacles (buildings, etc.)
        for y in range(TOP_BAR_HEIGHT, SIM_HEIGHT):
            for x in range(SIM_WIDTH):
                # Get pixel color
                color = map_surface.get_at((x, y))
                
                # Detect obstacles based on color brightness
                brightness = (color.r + color.g + color.b) / 3
                
                # Dark pixels (< 140) are likely buildings
                if brightness < 140 and y >= TOP_BAR_HEIGHT:
                    self.obstacle_map[y, x] = True
                elif y >= TOP_BAR_HEIGHT:
                    # Store some street points for random placement
                    if random.random() < 0.001:  # Reduced for performance
                        self.street_points.append((x, y))
        
        # Create debug visualization surface
        self.debug_surface.fill((0, 0, 0, 0))
        for y in range(TOP_BAR_HEIGHT, SIM_HEIGHT):
            for x in range(SIM_WIDTH):
                if self.obstacle_map[y, x]:
                    self.debug_surface.set_at((x, y), (200, 0, 0, 100))
        
        # Dilate obstacles to create safer paths
        self.dilate_obstacles(margin=3)
        
        # Build navigation graph for pathfinding
        self.build_street_graph()
    
    def dilate_obstacles(self, margin=3):
        """Expands obstacles to create a safety margin"""
        dilated_map = np.copy(self.obstacle_map)
        
        # For each obstacle pixel, mark neighbors within margin
        for y in range(TOP_BAR_HEIGHT, SIM_HEIGHT):
            for x in range(SIM_WIDTH):
                if self.obstacle_map[y, x]:
                    for dy in range(-margin, margin+1):
                        for dx in range(-margin, margin+1):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < SIM_HEIGHT and 0 <= nx < SIM_WIDTH:
                                dilated_map[ny, nx] = True
        
        # Update obstacle map
        self.obstacle_map = dilated_map
        
        # Update debug visualization
        for y in range(TOP_BAR_HEIGHT, SIM_HEIGHT):
            for x in range(SIM_WIDTH):
                if dilated_map[y, x] and not self.obstacle_map[y, x]:
                    self.debug_surface.set_at((x, y), (200, 100, 0, 50))
    
    def build_street_graph(self, step=20):
        """Builds a navigation graph of connected street points"""
        self.street_graph = {}
        
        # Create nodes on street points with regular spacing
        nodes = []
        for y in range(TOP_BAR_HEIGHT, SIM_HEIGHT, step):
            for x in range(0, SIM_WIDTH, step):
                if not self.is_obstacle(x, y):
                    nodes.append((x, y))
        
        # Connect nodes that have clear paths between them
        for node in nodes:
            self.street_graph[node] = []
            for other in nodes:
                if node != other:
                    dx, dy = other[0] - node[0], other[1] - node[1]
                    dist = (dx*dx + dy*dy) ** 0.5
                    
                    # Only connect reasonably close nodes
                    if dist < step * 1.5:
                        if self.has_clear_path(node, other):
                            self.street_graph[node].append(other)
    
    def has_clear_path(self, start, end):
        """Checks if there's a clear path between two points"""
        # Use Bresenham's line algorithm
        x0, y0 = start
        x1, y1 = end
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while x0 != x1 or y0 != y1:
            if self.is_obstacle(x0, y0):
                return False
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        
        return True
    
    def is_obstacle(self, x, y):
        """Checks if a point is an obstacle"""
        # Check boundaries
        if x < 0 or x >= SIM_WIDTH or y < TOP_BAR_HEIGHT or y >= SIM_HEIGHT:
            return True
            
        # Check obstacle map
        return self.obstacle_map[int(y), int(x)]
    
    def find_path(self, start, end, max_iterations=300):
        """A* pathfinding algorithm with optimizations"""
        # Convert to integers
        start = (int(start[0]), int(start[1]))
        end = (int(end[0]), int(end[1]))
        
        # If start or end is in an obstacle, find nearest valid point
        if self.is_obstacle(*start):
            start = self.find_nearest_street(start)
        if self.is_obstacle(*end):
            end = self.find_nearest_street(end)
        
        # Early exit if direct path is clear and short
        if self.has_clear_path(start, end) and self.distance(start, end) < 200:
            return [pygame.Vector2(start), pygame.Vector2(end)]
        
        # A* implementation
        open_set = {start}
        closed_set = set()
        
        # Track path and scores
        came_from = {}
        g_score = {start: 0}  # Cost from start
        f_score = {start: self.heuristic(start, end)}  # Estimated total cost
        
        iterations = 0
        while open_set and iterations < max_iterations:
            iterations += 1
            
            # Get node with lowest f_score
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            
            # Check if we're close enough to target
            if self.distance(current, end) < 20:
                path = self.reconstruct_path(came_from, current)
                path.append(pygame.Vector2(end))
                return self.simplify_path(path)
            
            # Move current from open to closed
            open_set.remove(current)
            closed_set.add(current)
            
            # Try 8 directions with varying step sizes
            for step in [20, 10]:  # Try larger steps first for efficiency
                for angle in range(0, 360, 45):  # 8 directions
                    rad = math.radians(angle)
                    dx = step * math.cos(rad)
                    dy = step * math.sin(rad)
                    
                    # Round to integer coordinates
                    neighbor = (int(current[0] + dx), int(current[1] + dy))
                    
                    # Skip if out of bounds, in closed set, or obstacle
                    if (neighbor in closed_set or
                        neighbor[0] < 0 or neighbor[0] >= SIM_WIDTH or
                        neighbor[1] < TOP_BAR_HEIGHT or neighbor[1] >= SIM_HEIGHT or
                        self.is_obstacle(*neighbor)):
                        continue
                    
                    # Check path clearance
                    if not self.has_clear_path(current, neighbor):
                        continue
                    
                    # Calculate new path cost
                    tentative_g_score = g_score[current] + self.distance(current, neighbor)
                    
                    if neighbor not in open_set:
                        open_set.add(neighbor)
                    elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                        continue
                    
                    # This path is better, record it
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, end) * 1.1  # Slight heuristic bias
        
        # If path not found, use fallback method
        return self.fallback_path(start, end)
    
    def reconstruct_path(self, came_from, current):
        """Reconstructs path from A* result"""
        path = [pygame.Vector2(current)]
        while current in came_from:
            current = came_from[current]
            path.append(pygame.Vector2(current))
        path.reverse()
        return path
    
    def simplify_path(self, path, tolerance=10):
        """Simplifies path by removing redundant points"""
        if len(path) <= 2:
            return path
            
        simplified = [path[0]]
        
        for i in range(1, len(path) - 1):
            prev = simplified[-1]
            current = path[i]
            next_point = path[i + 1]
            
            # Vector from prev to current
            v1 = current - prev
            # Vector from current to next
            v2 = next_point - current
            
            # Normalize vectors
            if v1.length() > 0:
                v1.normalize_ip()
            if v2.length() > 0:
                v2.normalize_ip()
                
            # Dot product measures how parallel the vectors are
            dot = v1.x * v2.x + v1.y * v2.y
            
            # If not on a straight line or near an obstacle, keep the point
            if dot < 0.95 or not self.has_clear_path((prev.x, prev.y), (next_point.x, next_point.y)):
                simplified.append(current)
                
        simplified.append(path[-1])
        return simplified
    
    def fallback_path(self, start, end):
        """Fallback pathfinding when A* fails"""
        path = [pygame.Vector2(start)]
        current = pygame.Vector2(start)
        
        for _ in range(30):  # Limit iterations for efficiency
            # Direction to target
            direction = pygame.Vector2(end) - current
            if direction.length() < 20:
                path.append(pygame.Vector2(end))
                break
                
            # Normalize and scale
            if direction.length() > 0:
                direction = direction.normalize() * 20
                
            # Try direct path
            new_pos = current + direction
            
            # If obstacle, try alternate directions
            if self.is_obstacle(int(new_pos.x), int(new_pos.y)):
                # Try different angles
                found_path = False
                for angle in [30, -30, 60, -60, 90, -90]:
                    rad = angle * math.pi / 180
                    rotated = pygame.Vector2(
                        direction.x * math.cos(rad) - direction.y * math.sin(rad),
                        direction.x * math.sin(rad) + direction.y * math.cos(rad)
                    )
                    
                    test_pos = current + rotated
                    if not self.is_obstacle(int(test_pos.x), int(test_pos.y)):
                        new_pos = test_pos
                        found_path = True
                        break
                
                if not found_path:
                    # Last resort: random street point
                    random_point = self.get_random_street_point()
                    direction = pygame.Vector2(random_point) - current
                    if direction.length() > 0:
                        direction = direction.normalize() * 20
                    new_pos = current + direction
            
            # Add to path and update position
            current = new_pos
            path.append(current)
            
        return path
    
    def heuristic(self, a, b):
        """A* heuristic (Euclidean distance)"""
        return self.distance(a, b)
    
    def distance(self, a, b):
        """Euclidean distance between points"""
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5
    
    def get_random_street_point(self):
        """Returns a random valid street point"""
        if not self.street_points:
            # Create some street points if none exist
            self.street_points = []
            for y in range(TOP_BAR_HEIGHT, SIM_HEIGHT, 10):
                for x in range(0, SIM_WIDTH, 10):
                    if not self.is_obstacle(x, y):
                        self.street_points.append((x, y))
        
        if not self.street_points:
            return (SIM_WIDTH//2, SIM_HEIGHT//2)
            
        return random.choice(self.street_points)
    
    def find_nearest_street(self, pos):
        """Finds the nearest valid street point"""
        if not self.is_obstacle(int(pos[0]), int(pos[1])):
            return pos
            
        # Search in expanding circles
        for radius in range(1, 50, 2):
            for angle in range(0, 360, 15):  # 24 directions
                rad = math.radians(angle)
                x = int(pos[0] + radius * math.cos(rad))
                y = int(pos[1] + radius * math.sin(rad))
                
                if (0 <= x < SIM_WIDTH and 
                    TOP_BAR_HEIGHT <= y < SIM_HEIGHT and 
                    not self.is_obstacle(x, y)):
                    return (x, y)
                    
        # Fallback to a random street point
        return self.get_random_street_point()
    
    def update_density_map(self, people, decay=0.95):
        """Updates density heatmap based on people positions"""
        # Apply decay to existing density
        self.density_map *= decay
        
        # Add density for each person
        for person in people:
            x, y = int(person.pos.x), int(person.pos.y)
            if 0 <= x < SIM_WIDTH and TOP_BAR_HEIGHT <= y < SIM_HEIGHT:
                # Add density at person position and surrounding area
                radius = 8
                for dy in range(-radius, radius+1):
                    for dx in range(-radius, radius+1):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < SIM_WIDTH and TOP_BAR_HEIGHT <= ny < SIM_HEIGHT):
                            # Gaussian-like falloff from center
                            dist_sq = dx*dx + dy*dy
                            if dist_sq <= radius*radius:
                                density_contribution = 1.0 * math.exp(-dist_sq / (radius*0.5))
                                self.density_map[ny, nx] += density_contribution
        
        # Cap maximum density
        self.density_map = np.clip(self.density_map, 0, 10)
        
        # Update heatmap visualization
        self.update_heatmap_surface()
    
    def update_heatmap_surface(self):
        """Updates the heatmap visualization surface"""
        self.heatmap_surface.fill((0, 0, 0, 0))
        
        # Find max density for normalization
        max_density = np.max(self.density_map)
        if max_density > 0:
            for y in range(TOP_BAR_HEIGHT, SIM_HEIGHT):
                for x in range(0, SIM_WIDTH):
                    density = self.density_map[y, x]
                    if density > 0.1:  # Only draw significant density
                        # Normalize to 0-1
                        normalized = density / max_density
                        
                        # Color gradient from blue (low) to red (high)
                        if normalized < 0.5:
                            # Blue to green
                            r = int(0 + normalized * 2 * 255)
                            g = int(100 + normalized * 2 * 155)
                            b = int(255 - normalized * 2 * 155)
                        else:
                            # Green to red
                            factor = (normalized - 0.5) * 2
                            r = int(255)
                            g = int(255 - factor * 255)
                            b = 0
                        
                        # Alpha based on density
                        alpha = min(180, int(normalized * 200))
                        
                        self.heatmap_surface.set_at((x, y), (r, g, b, alpha))
    
    def draw_debug(self, surface):
        """Draws debug visualization"""
        surface.blit(self.debug_surface, (0, 0))
    
    def draw_heatmap(self, surface):
        """Draws density heatmap visualization"""
        surface.blit(self.heatmap_surface, (0, 0))