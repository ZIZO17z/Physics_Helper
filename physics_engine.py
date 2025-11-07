# -*- coding: utf-8 -*-
import pygame
import math
import numpy as np
import random
from constants import *


class Adv_Projectile:
    def __init__(self, x, y, vx, vy, mass, area, g, rho, Cd, wind_vx):
        self.state = np.array([x, y, vx, vy])
        self.mass = mass
        self.area = area
        self.g = g
        self.rho = rho
        self.Cd = Cd
        self.wind_vx = wind_vx
        self.k = 0.5 * self.rho * self.area * self.Cd
        
        self.is_active = True
        self.time = 0.0
        self.max_height = 0.0

    @property
    def x(self): return self.state[0]
    @property
    def y(self): return self.state[1]
    @property
    def vx(self): return self.state[2]
    @property
    def vy(self): return self.state[3]

    def _calculate_derivatives(self, state_vec, t):
        x, y, vx, vy = state_vec
        
        dxdt = vx
        dydt = vy
        
        v_rel_x = vx - self.wind_vx
        v_rel_y = vy
        v_rel_mag = math.sqrt(v_rel_x**2 + v_rel_y**2)
        
        if v_rel_mag == 0:
            return np.array([dxdt, dydt, 0, -self.g])

        F_grav_y = -self.mass * self.g
        F_drag_mag = self.k * (v_rel_mag ** 2)
        
        F_drag_x = -F_drag_mag * (v_rel_x / v_rel_mag)
        F_drag_y = -F_drag_mag * (v_rel_y / v_rel_mag)
        
        F_net_x = F_drag_x
        F_net_y = F_grav_y + F_drag_y
        
        ax = F_net_x / self.mass
        ay = F_net_y / self.mass
        
        return np.array([dxdt, dydt, ax, ay])

    def update_rk4(self, dt):
        if not self.is_active:
            return

        k1 = self._calculate_derivatives(self.state, self.time)
        k2 = self._calculate_derivatives(self.state + 0.5 * dt * k1, self.time + 0.5 * dt)
        k3 = self._calculate_derivatives(self.state + 0.5 * dt * k2, self.time + 0.5 * dt)
        k4 = self._calculate_derivatives(self.state + dt * k3, self.time + dt)
        
        self.state = self.state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        
        self.time += dt
        if self.y > self.max_height:
            self.max_height = self.y
            
        if self.y < 0:
            self.state[1] = 0
            self.is_active = False

    def draw(self, screen, zoom, origin, sim_rect):
        if not self.is_active:
            return
        
       
        origin_x, origin_y = origin
        x_pix = origin_x + int(self.x * zoom)
        y_pix = origin_y - int(self.y * zoom)
        pos_pix = (x_pix, y_pix)
        
        if not sim_rect.collidepoint(pos_pix):
            return

        pygame.draw.circle(screen, BLACK, pos_pix, 6)
        pygame.draw.circle(screen, DARK_GRAY, pos_pix, 6, 1)

class Adv_IdealProjectile:
    def __init__(self, x, y, vx, vy, g):
        self.x = x
        self.y = y
        self.vx_initial = vx
        self.vy_initial = vy
        self.g = g
        self.time = 0.0
        self.is_active = True

    def update(self, dt):
        if not self.is_active:
            return
            
        self.time += dt
        self.x = self.vx_initial * self.time
        self.y = (self.vy_initial * self.time) - (0.5 * self.g * self.time**2)
        
        if self.y < 0:
            self.y = 0
            self.is_active = False


class Particle:
    def __init__(self, position, velocity, radius=8):
        self.pos = np.array(position, dtype=np.float64)
        self.vel = np.array(velocity, dtype=np.float64)
        self.radius = radius
        self.mass = self.radius ** 2
        self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        self.is_in = True
        self.is_grabbed = False

    def update(self, dt, gravity, wind, air_density):
        F_grav = gravity * self.mass
        
        v_rel = self.vel - wind
        v_rel_mag = np.linalg.norm(v_rel)
        F_drag = np.zeros(2)
        if v_rel_mag > 0 and air_density > 0:
            area = math.pi * (self.radius/10.0)**2
            F_drag_mag = 0.5 * air_density * area * v_rel_mag**2
            F_drag = -F_drag_mag * (v_rel / v_rel_mag)
        
        F_net = F_grav + F_drag
        
        accel = F_net / self.mass
        self.vel += accel * dt
        self.pos += self.vel * dt

    def check_container_collision(self, center, radius, container_angle, gap_angle, spin_speed):
        if not self.is_in: 
            return
            
        dist_vec = self.pos - center
        dist = np.linalg.norm(dist_vec)
        
        if dist + self.radius > radius:
            ball_angle = math.atan2(dist_vec[1], dist_vec[0])
            
            gap_half_angle = gap_angle / 2
            start_angle = (container_angle - gap_half_angle) % (2 * math.pi)
            end_angle = (container_angle + gap_half_angle) % (2 * math.pi)
            
            is_in_gap = False
            if start_angle > end_angle:
                if ball_angle >= start_angle or ball_angle <= end_angle:
                    is_in_gap = True
            else:
                if start_angle <= ball_angle <= end_angle:
                    is_in_gap = True
            
            if is_in_gap:
                self.is_in = False
                return 
            
            self.is_in = True
            
            normal_vec = dist_vec / dist
            self.pos = center + (radius - self.radius) * normal_vec 
            
            wall_vel_mag = radius * spin_speed
            tangent_vec = np.array([-normal_vec[1], normal_vec[0]])
            wall_vel = wall_vel_mag * tangent_vec
            
            v_rel = self.vel - wall_vel
            elasticity = 0.85
            v_rel_normal_comp = np.dot(v_rel, normal_vec)
            
            if v_rel_normal_comp > 0: 
                v_reflect = v_rel - (1 + elasticity) * v_rel_normal_comp * normal_vec
                self.vel = v_reflect + wall_vel

    def is_mouse_over(self, mouse_pos):
        return np.linalg.norm(self.pos - mouse_pos) < self.radius

    def draw(self, screen):
        color = BLUE if self.is_grabbed else self.color
        pygame.draw.circle(screen, color, self.pos.astype(int), int(self.radius))
        pygame.draw.circle(screen, DARK_GRAY, self.pos.astype(int), int(self.radius), 1)

# --- Physics Functions (for Particle Sandbox) ---
def resolve_particle_collision(ball1, ball2):
    dist_vec = ball1.pos - ball2.pos
    dist = np.linalg.norm(dist_vec)
    if dist == 0 or dist > (ball1.radius + ball2.radius): return
    
    overlap = (ball1.radius + ball2.radius) - dist
    ball1.pos += 0.5 * overlap * (dist_vec / dist)
    ball2.pos -= 0.5 * overlap * (dist_vec / dist)
    
    normal_vec = dist_vec / dist
    tangent_vec = np.array([-normal_vec[1], normal_vec[0]])
    
    v1_n = np.dot(ball1.vel, normal_vec)
    v2_n = np.dot(ball2.vel, normal_vec)
    v1_t = np.dot(ball1.vel, tangent_vec)
    v2_t = np.dot(ball2.vel, tangent_vec)
    
    m1 = ball1.mass
    m2 = ball2.mass
    
    v1_n_new = (v1_n * (m1 - m2) + 2 * m2 * v2_n) / (m1 + m2)
    v2_n_new = (v2_n * (m2 - m1) + 2 * m1 * v1_n) / (m1 + m2)
    
    ball1.vel = (v1_n_new * normal_vec) + (v1_t * tangent_vec)
    ball2.vel = (v2_n_new * normal_vec) + (v2_t * tangent_vec)