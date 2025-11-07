# -*- coding: utf-8 -*-
import pygame
import math
import numpy as np
import random


from constants import *
from gui_components import Slider, Button, CheckBox, TextBox, Graph
from physics_engine import Particle, resolve_particle_collision

class ParticleSandbox:
    def __init__(self, screen, screen_rect, fonts):
        self.screen = screen
        self.screen_rect = screen_rect
        self.font_small = fonts['small']
        self.font_medium = fonts['medium']
        self.font_large = fonts['large']
        
       
        self.sim_rect = pygame.Rect(0, 0, 1000, screen_rect.height)
        self.ui_rect = pygame.Rect(1000, 0, 300, screen_rect.height)
        
        self.simulation_running = True
        self.particles = []
        
        
        self.container_center = np.array([self.sim_rect.centerx, self.sim_rect.centery], dtype=np.float64)
        self.container_radius = self.sim_rect.height // 2 - 40 # Scale with height
        self.container_spin_speed = 0.5
        self.container_gap_angle = math.radians(60)
        self.container_angle = 0.0
        
        self.spawn_timer = 0.0
        self.spawn_rate = 1.0
        self.spawn_pos = np.array([self.container_center[0], self.container_center[1] - self.container_radius // 2], dtype=np.float64)
        self.spawn_vel_variance = 20
        self.spawner_active = True
        
        self.grabbed_object = None
        self.active_textbox = None
        self.graph_timer = 0.0

        self.create_gui_elements()

    def create_gui_elements(self):
        self.sliders = {}
        self.buttons = {}
        self.checkboxes = {}
        self.textboxes = {}
        
        panel_x = self.ui_rect.x + 20
        panel_w = self.ui_rect.width - 40
        w = panel_w - 90
        
        y_pos = self.ui_rect.y + 90
        
        self.checkboxes['spawner_active'] = CheckBox(panel_x, y_pos, 20, 20, "Particle Spawner", self.font_medium, True)
        y_pos += 40
        
        self.sliders['spawn_rate'] = Slider(panel_x, y_pos, w, 20, 0.1, 20.0, 1.0, "Spawn Rate", "parts/s")
        self.textboxes['spawn_rate'] = TextBox(panel_x + w + 10, y_pos, 70, 30, "1.0", self.font_medium)
        y_pos += 50
        
        self.sliders['spawn_vel'] = Slider(panel_x, y_pos, w, 20, 0.0, 100.0, 20.0, "Spawn Velocity Var", "+/-")
        self.textboxes['spawn_vel'] = TextBox(panel_x + w + 10, y_pos, 70, 30, "20.0", self.font_medium)
        y_pos += 50
        
        self.sliders['gravity'] = Slider(panel_x, y_pos, w, 20, 0.0, 500.0, DEFAULT_GRAVITY_PX, "Gravity (g)", "px/s²")
        self.textboxes['gravity'] = TextBox(panel_x + w + 10, y_pos, 70, 30, str(DEFAULT_GRAVITY_PX), self.font_medium)
        y_pos += 50

        self.sliders['spin_speed'] = Slider(panel_x, y_pos, w, 20, -5.0, 5.0, self.container_spin_speed, "Spin Speed", "rad/s")
        self.textboxes['spin_speed'] = TextBox(panel_x + w + 10, y_pos, 70, 30, str(self.container_spin_speed), self.font_medium)
        y_pos += 50
        
        self.sliders['gap_angle'] = Slider(panel_x, y_pos, w, 20, 0.0, 360.0, 60.0, "Gap Size", "degrees")
        self.textboxes['gap_angle'] = TextBox(panel_x + w + 10, y_pos, 70, 30, "60.0", self.font_medium)
        y_pos += 50

        self.buttons['toggle_pause'] = Button(panel_x, y_pos, (panel_w - 10) // 2, 40, "PAUSE", RED)
        self.buttons['clear'] = Button(panel_x + (panel_w + 10) // 2, y_pos, (panel_w - 10) // 2, 40, "CLEAR", BLUE)
        y_pos += 50
        
        self.particle_count_graph = Graph(
            pygame.Rect(panel_x, y_pos, panel_w, 150),
            "Time (s)", "Particle Count", self.font_small, 200
        )
        y_pos += 160
        self.data_readout_y = y_pos

        
        self.buttons['back'] = Button(panel_x, self.ui_rect.height - 60, panel_w, 40, "Back to Menu", DARK_GRAY)

    def handle_events(self, events):
        for event in events:
            if self.active_textbox:
                self.active_textbox.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    for key, tb in self.textboxes.items():
                        if tb == self.active_textbox:
                            self.sync_widgets('textbox', key)
                            break
                    self.active_textbox.active = False
                    self.active_textbox = None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                if self.active_textbox and not self.active_textbox.is_over(mouse_pos):
                    for key, tb in self.textboxes.items():
                        if tb == self.active_textbox: self.sync_widgets('textbox', key)
                    self.active_textbox.active = False
                    self.active_textbox = None

                if self.ui_rect.collidepoint(mouse_pos):
                    for tb in self.textboxes.values():
                        if tb.is_over(mouse_pos):
                            self.active_textbox = tb
                            tb.active = True
                            break
                    
                    if not self.active_textbox:
                        if self.buttons['toggle_pause'].is_over(mouse_pos):
                            self.simulation_running = not self.simulation_running
                            self.buttons['toggle_pause'].text = "PAUSE" if self.simulation_running else "RESUME"
                            self.buttons['toggle_pause'].color = RED if self.simulation_running else GREEN
                        elif self.buttons['clear'].is_over(mouse_pos):
                            self.particles = []
                            self.particle_count_graph.clear_data()
                        elif self.buttons['back'].is_over(mouse_pos):
                            return 'main_menu'
                        
                        for cb in self.checkboxes.values():
                            if cb.is_over(mouse_pos):
                                cb.toggle()
                
                if self.sim_rect.collidepoint(mouse_pos) and not self.active_textbox:
                    for particle in reversed(self.particles):
                        if particle.is_mouse_over(mouse_pos):
                            self.grabbed_object = particle
                            self.grabbed_object.is_grabbed = True
                            self.grabbed_object.vel = np.zeros(2)
                            break

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.grabbed_object:
                    self.grabbed_object.is_grabbed = False
                    self.grabbed_object = None
                
                for slider in self.sliders.values():
                    if slider.dragging:
                        slider.dragging = False
                        for key, s in self.sliders.items():
                            if s == slider: self.sync_widgets('slider', key)
            
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                if self.grabbed_object:
                    self.grabbed_object.pos = np.array(mouse_pos, dtype=np.float64)
                    self.grabbed_object.vel = np.array(event.rel, dtype=np.float64) * 5.0
                
                for key, slider in self.sliders.items():
                    if slider.dragging:
                        slider.set_value_from_pos(mouse_pos[0])
                        self.sync_widgets('slider', key)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.ui_rect.collidepoint(mouse_pos) and not self.active_textbox and not self.grabbed_object:
                    for slider in self.sliders.values():
                        if slider.is_over(mouse_pos):
                            slider.dragging = True
                            break
        return None 

    def spawn_particle(self):
        vel_var = self.sliders['spawn_vel'].get_value()
        vel = np.array([random.uniform(-vel_var, vel_var), 
                        random.uniform(-vel_var, vel_var)], dtype=np.float64)
        
        new_particle = Particle(self.spawn_pos.copy(), vel)
        new_particle.radius = 8
        new_particle.mass = new_particle.radius**2
        self.particles.append(new_particle)

    def update_simulation(self):
        if not self.simulation_running:
            return
            
        self.spawner_active = self.checkboxes['spawner_active'].checked
        self.spawn_rate = self.sliders['spawn_rate'].get_value()
        self.container_spin_speed = self.sliders['spin_speed'].get_value()
        self.container_gap_angle = math.radians(self.sliders['gap_angle'].get_value())
        
        gravity_vec = np.array([0, self.sliders['gravity'].get_value()], dtype=np.float64)
        
        if self.spawner_active:
            self.spawn_timer += DT
            if self.spawn_timer >= 1.0 / self.spawn_rate:
                self.spawn_timer = 0
                self.spawn_particle()
        
        self.container_angle = (self.container_angle + self.container_spin_speed * DT) % (2 * math.pi)
        
        particles_to_remove = []
        for i, particle in enumerate(self.particles):
            if particle.is_grabbed:
                continue
                
            particle.update(DT, gravity_vec, np.zeros(2), 0.0) # No wind/drag for this one
            
            particle.check_container_collision(self.container_center, self.container_radius, self.container_angle, self.container_gap_angle, self.container_spin_speed)
            
            for j in range(i + 1, len(self.particles)):
                particle2 = self.particles[j]
                if particle2.is_grabbed:
                    continue
                resolve_particle_collision(particle, particle2)
            
            if not self.sim_rect.collidepoint(particle.pos) and particle.is_in == False:
                particles_to_remove.append(particle)

        for particle in particles_to_remove:
            if particle in self.particles:
                self.particles.remove(particle)
            
        self.graph_timer += DT
        if self.graph_timer >= 0.5:
            self.graph_timer = 0
            self.particle_count_graph.add_data_point(pygame.time.get_ticks() / 1000.0, len(self.particles))

    def sync_widgets(self, source_type, key):
        try:
            if source_type == 'slider':
                slider = self.sliders[key]
                textbox = self.textboxes[key]
                textbox.text = f"{slider.get_value():.2f}"
            elif source_type == 'textbox':
                slider = self.sliders[key]
                textbox = self.textboxes[key]
                slider.set_value(textbox.get_value_as_float())
        except (ValueError, KeyError):
            pass

    def draw_all(self):
        self.draw_simulation_area()
        self.draw_gui_panel()

    def draw_simulation_area(self):
        self.screen.set_clip(self.sim_rect)
        
        pygame.draw.rect(self.screen, BLACK, self.sim_rect)
        
        pygame.draw.circle(self.screen, (255, 165, 0), self.container_center.astype(int), self.container_radius, 5)
        
        gap_half_angle = self.container_gap_angle / 2
        start_angle = self.container_angle - gap_half_angle
        end_angle = self.container_angle + gap_half_angle
        
        p1 = self.container_center + (self.container_radius + self.sim_rect.width) * np.array([math.cos(start_angle), math.sin(start_angle)])
        p2 = self.container_center + (self.container_radius + self.sim_rect.width) * np.array([math.cos(end_angle), math.sin(end_angle)])
        pygame.draw.polygon(self.screen, BLACK, [self.container_center.astype(int), p1.astype(int), p2.astype(int)], 0)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        if self.spawner_active:
            pygame.draw.circle(self.screen, BLUE, self.spawn_pos.astype(int), 5)
            pygame.draw.circle(self.screen, BLUE, self.spawn_pos.astype(int), 10, 1)

        self.screen.set_clip(None)
        
        pygame.draw.rect(self.screen, DARK_GRAY, self.sim_rect, 5)

    def draw_gui_panel(self):
        pygame.draw.rect(self.screen, GRAY, self.ui_rect)
        
        title_text = self.font_large.render("Particle Sandbox", True, BLACK)
        self.screen.blit(title_text, (self.ui_rect.centerx - title_text.get_width() // 2, self.ui_rect.y + 20))
        
        active_panel_rect = (self.ui_rect.x + 10, self.ui_rect.y + 80, self.ui_rect.width - 20, 390)
        pygame.draw.rect(self.screen, GRAPH_BG, active_panel_rect, border_radius=5)

        for widget in self.sliders.values(): widget.draw(self.screen, self.font_small)
        for widget in self.textboxes.values(): widget.draw(self.screen, self.font_medium)
        for widget in self.checkboxes.values(): widget.draw(self.screen, self.font_medium)
        for widget in self.buttons.values(): widget.draw(self.screen, self.font_medium)
            
        self.particle_count_graph.draw(self.screen)
        self.draw_data_readouts(self.ui_rect.x + 20)

    def draw_data_readouts(self, panel_x):
        y_pos = self.data_readout_y
        
        data = [
            f"Total Particles: {len(self.particles)}",
        ]

        for line in data:
            text_surf = self.font_small.render(line, True, BLACK)
            self.screen.blit(text_surf, (panel_x, y_pos))
            y_pos += 20