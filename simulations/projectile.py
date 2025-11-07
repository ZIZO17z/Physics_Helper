# -*- coding: utf-8 -*-
import pygame
import math
import numpy as np


from constants import *
from gui_components import Adv_Slider, Adv_Button, Adv_TabButton, Adv_CheckBox, Adv_TextBox, Adv_Graph
from physics_engine import Adv_Projectile, Adv_IdealProjectile


def adv_to_screen_coords(pos_m, zoom, origin):
    origin_x, origin_y = origin
    x_pix = origin_x + int(pos_m[0] * zoom)
    y_pix = origin_y - int(pos_m[1] * zoom)
    return (x_pix, y_pix)

def adv_to_meters_coords(pos_pix, zoom, origin):
    origin_x, origin_y = origin
    x_m = (pos_pix[0] - origin_x) / zoom
    y_m = (origin_y - pos_pix[1]) / zoom
    return (x_m, y_m)

class AdvancedProjectileLab:
    def __init__(self, screen, screen_rect, fonts):
        self.screen = screen
        self.screen_rect = screen_rect
        self.font_small = fonts['small']
        self.font_medium = fonts['medium']
        self.font_large = fonts['large']
        
        
        self.sim_rect = pygame.Rect(0, 0, 900, screen_rect.height)
        self.ui_rect = pygame.Rect(900, 0, 400, screen_rect.height)

        self.simulation_running = False
        
        self.last_projectile = None
        self.last_ideal_projectile = None
        self.trajectories = []
        self.ideal_trajectories = []
        
        self.target_pos_m = None
        self.target_radius_m = 2.0
        self.hit_target = False
        
        
        self.SIM_AREA_WIDTH = self.sim_rect.width
        self.GROUND_Y = self.sim_rect.height - 70
        self.CANNON_ORIGIN_PIX = (self.sim_rect.x + 60, self.GROUND_Y)
        self.PIXELS_PER_METER = 5.0

        self.create_gui_elements()
        self.active_textbox = None
        self.active_tab = 'projectile'

    def create_gui_elements(self):
        self.sliders = {}
        self.buttons = {}
        self.checkboxes = {}
        self.textboxes = {}
        self.tab_buttons = {}
        
        self.widgets_by_tab = {
            'projectile': [],
            'environment': [],
            'view': []
        }
        
        panel_x = self.ui_rect.x + 20
        panel_w = self.ui_rect.width - 40
        
     
        tab_w = self.ui_rect.width // 3
        self.tab_buttons['projectile'] = Adv_TabButton(self.ui_rect.x, 40, tab_w, 30, "Projectile", self.font_medium)
        self.tab_buttons['environment'] = Adv_TabButton(self.ui_rect.x + tab_w, 40, tab_w, 30, "Environment", self.font_medium)
        self.tab_buttons['view'] = Adv_TabButton(self.ui_rect.x + 2 * tab_w, 40, tab_w, 30, "View", self.font_medium)
        
        y_pos_start = 90
        
       
        y_pos = y_pos_start
        x_pos = panel_x
        w = panel_w - 90
        
        self.sliders['velocity'] = Adv_Slider(x_pos, y_pos, w, 20, 1.0, 500.0, 100.0, "Initial Velocity", "m/s")
        self.textboxes['velocity'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, "100.0", self.font_medium)
        self.widgets_by_tab['projectile'].extend([self.sliders['velocity'], self.textboxes['velocity']])
        y_pos += 50
        
        self.sliders['angle'] = Adv_Slider(x_pos, y_pos, w, 20, 0.0, 90.0, 45.0, "Launch Angle", "deg")
        self.textboxes['angle'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, "45.0", self.font_medium)
        self.widgets_by_tab['projectile'].extend([self.sliders['angle'], self.textboxes['angle']])
        y_pos += 50

        self.sliders['mass'] = Adv_Slider(x_pos, y_pos, w, 20, 0.1, 100.0, 10.0, "Mass", "kg")
        self.textboxes['mass'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, "10.0", self.font_medium)
        self.widgets_by_tab['projectile'].extend([self.sliders['mass'], self.textboxes['mass']])
        y_pos += 50

        self.sliders['radius'] = Adv_Slider(x_pos, y_pos, w, 20, 0.01, 2.0, 0.1, "Radius", "m")
        self.textboxes['radius'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, "0.1", self.font_medium)
        self.widgets_by_tab['projectile'].extend([self.sliders['radius'], self.textboxes['radius']])
        y_pos += 50
        
        
        y_pos = y_pos_start
        
        self.sliders['gravity'] = Adv_Slider(x_pos, y_pos, w, 20, 0.1, 25.0, DEFAULT_GRAVITY_M, "Gravity (g)", "m/s²")
        self.textboxes['gravity'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, str(DEFAULT_GRAVITY_M), self.font_medium)
        self.widgets_by_tab['environment'].extend([self.sliders['gravity'], self.textboxes['gravity']])
        y_pos += 50

        self.sliders['air_density'] = Adv_Slider(x_pos, y_pos, w, 20, 0.0, 2.0, DEFAULT_AIR_DENSITY, "Air Density (ρ)", "kg/m³")
        self.textboxes['air_density'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, str(DEFAULT_AIR_DENSITY), self.font_medium)
        self.widgets_by_tab['environment'].extend([self.sliders['air_density'], self.textboxes['air_density']])
        y_pos += 50

        self.sliders['drag_coeff'] = Adv_Slider(x_pos, y_pos, w, 20, 0.0, 1.0, DEFAULT_DRAG_COEFF, "Drag Coeff (Cd)", "")
        self.textboxes['drag_coeff'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, str(DEFAULT_DRAG_COEFF), self.font_medium)
        self.widgets_by_tab['environment'].extend([self.sliders['drag_coeff'], self.textboxes['drag_coeff']])
        y_pos += 50
        
        self.sliders['wind_vx'] = Adv_Slider(x_pos, y_pos, w, 20, -50.0, 50.0, DEFAULT_WIND_VX_M, "Wind Velocity (x)", "m/s")
        self.textboxes['wind_vx'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, str(DEFAULT_WIND_VX_M), self.font_medium)
        self.widgets_by_tab['environment'].extend([self.sliders['wind_vx'], self.textboxes['wind_vx']])
        y_pos += 50
        
        self.checkboxes['air_drag'] = Adv_CheckBox(x_pos, y_pos, 20, 20, "Enable Air Drag", self.font_medium, True)
        self.widgets_by_tab['environment'].append(self.checkboxes['air_drag'])
        
        
        y_pos = y_pos_start
        
        self.sliders['zoom'] = Adv_Slider(x_pos, y_pos, w, 20, 1.0, 20.0, self.PIXELS_PER_METER, "Zoom (Pixels/Meter)", "")
        self.textboxes['zoom'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, str(self.PIXELS_PER_METER), self.font_medium)
        self.widgets_by_tab['view'].extend([self.sliders['zoom'], self.textboxes['zoom']])
        y_pos += 50
        
        self.sliders['time_scale'] = Adv_Slider(x_pos, y_pos, w, 20, 0.1, 2.0, 1.0, "Time Scale", "x")
        self.textboxes['time_scale'] = Adv_TextBox(x_pos + w + 10, y_pos, 70, 30, "1.0", self.font_medium)
        self.widgets_by_tab['view'].extend([self.sliders['time_scale'], self.textboxes['time_scale']])
        y_pos += 50
        
        self.checkboxes['ideal_path'] = Adv_CheckBox(x_pos, y_pos, 20, 20, "Show Ideal Path", self.font_medium, True)
        self.widgets_by_tab['view'].append(self.checkboxes['ideal_path'])
        
        
        graph_y = 300
        self.altitude_graph = Adv_Graph(
            pygame.Rect(panel_x, graph_y, panel_w, 200),
            "Time (s)", "Altitude (m)", self.font_small, 200
        )
        
        
        button_y = 520
        self.buttons['launch'] = Adv_Button(panel_x, button_y, (panel_w - 10) // 2, 50, "LAUNCH", GREEN)
        self.buttons['reset'] = Adv_Button(panel_x + (panel_w + 10) // 2, button_y, (panel_w - 10) // 2, 50, "RESET", RED)
        button_y += 60
        self.buttons['clear_trails'] = Adv_Button(panel_x, button_y, panel_w, 40, "Clear All Trails", BLUE)
        
       
        self.data_readout_y = button_y + 60

        
        self.buttons['back'] = Adv_Button(panel_x, self.ui_rect.height - 60, panel_w, 40, "Back to Menu", DARK_GRAY)
    
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

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
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
                
                if self.active_textbox and not self.active_textbox.is_over(mouse_pos):
                    for key, tb in self.textboxes.items():
                        if tb == self.active_textbox: self.sync_widgets('textbox', key)
                    self.active_textbox.active = False
                    self.active_textbox = None

                
                if self.ui_rect.collidepoint(mouse_pos):
                    
                    for tb in self.textboxes.values():
                        if tb in self.widgets_by_tab[self.active_tab] and tb.is_over(mouse_pos):
                            self.active_textbox = tb
                            tb.active = True
                            break
                    
                    if not self.active_textbox:
                        if self.buttons['launch'].is_over(mouse_pos) and not self.buttons['launch'].disabled:
                            self.launch_projectile()
                        elif self.buttons['reset'].is_over(mouse_pos):
                            self.reset_simulation()
                        elif self.buttons['clear_trails'].is_over(mouse_pos):
                            self.trajectories = []
                            self.ideal_trajectories = []
                        elif self.buttons['back'].is_over(mouse_pos):
                            return 'main_menu'
                        
                        for cb in self.checkboxes.values():
                            if cb in self.widgets_by_tab[self.active_tab] and cb.is_over(mouse_pos):
                                cb.toggle()
                        
                        for key, tab_btn in self.tab_buttons.items():
                            if tab_btn.is_over(mouse_pos):
                                self.active_tab = key
                                break
                
                
                if self.sim_rect.collidepoint(mouse_pos) and not self.active_textbox:
                    zoom = self.sliders['zoom'].get_value()
                    self.target_pos_m = adv_to_meters_coords(mouse_pos, zoom, self.CANNON_ORIGIN_PIX)
                    self.hit_target = False

            
            for key, slider in self.sliders.items():
                if slider in self.widgets_by_tab[self.active_tab]:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if slider.is_over(mouse_pos):
                            slider.dragging = True
                    
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        if slider.dragging:
                            slider.dragging = False
                            self.sync_widgets('slider', key)
                    
                    if event.type == pygame.MOUSEMOTION and slider.dragging:
                        slider.set_value_from_pos(mouse_pos[0])
                        self.sync_widgets('slider', key)
        return None 

    def launch_projectile(self):
        self.simulation_running = True
        self.buttons['launch'].disabled = True
        self.buttons['launch'].text = "RUNNING..."
        self.hit_target = False
        
        self.altitude_graph.clear_data()
        self.last_projectile = None
        self.last_ideal_projectile = None
        
        v0 = self.sliders['velocity'].get_value()
        angle_deg = self.sliders['angle'].get_value()
        angle_rad = math.radians(angle_deg)
        mass = self.sliders['mass'].get_value()
        radius = self.sliders['radius'].get_value()
        g = self.sliders['gravity'].get_value()
        rho = self.sliders['air_density'].get_value()
        Cd = self.sliders['drag_coeff'].get_value()
        wind_vx = self.sliders['wind_vx'].get_value()
        
        use_air_drag = self.checkboxes['air_drag'].checked
        show_ideal = self.checkboxes['ideal_path'].checked
        
        vx_initial = v0 * math.cos(angle_rad)
        vy_initial = v0 * math.sin(angle_rad)
        
        area = math.pi * radius**2
        
        if not use_air_drag:
            rho, Cd, wind_vx = 0, 0, 0
            
        start_pos = (0, 0.1)
        self.last_projectile = Adv_Projectile(start_pos[0], start_pos[1], vx_initial, vy_initial, mass, area, g, rho, Cd, wind_vx)
        self.trajectories.append([])
        
        if show_ideal:
            self.last_ideal_projectile = Adv_IdealProjectile(start_pos[0], start_pos[1], vx_initial, vy_initial, g)
            self.ideal_trajectories.append([])

    def reset_simulation(self):
        self.simulation_running = False
        self.last_projectile = None
        self.last_ideal_projectile = None
        self.buttons['launch'].disabled = False
        self.buttons['launch'].text = "LAUNCH"
        self.target_pos_m = None
        self.hit_target = False
        self.altitude_graph.clear_data()

    def update_simulation(self):
        self.PIXELS_PER_METER = self.sliders['zoom'].get_value()
        zoom = self.PIXELS_PER_METER
        time_scale = self.sliders['time_scale'].get_value()
        effective_dt = DT * time_scale
        
        if not self.simulation_running:
            return
            
        active_projectiles_exist = False
        
        if self.last_projectile and self.last_projectile.is_active:
            active_projectiles_exist = True
            self.last_projectile.update_rk4(effective_dt)
            
            screen_pos = adv_to_screen_coords((self.last_projectile.x, self.last_projectile.y), zoom, self.CANNON_ORIGIN_PIX)
            if self.trajectories:
                self.trajectories[-1].append(screen_pos)
            
            self.altitude_graph.add_data_point(self.last_projectile.time, self.last_projectile.y)
            
            if self.target_pos_m and not self.hit_target:
                dist = math.sqrt((self.last_projectile.x - self.target_pos_m[0])**2 + (self.last_projectile.y - self.target_pos_m[1])**2)
                if dist <= self.target_radius_m:
                    self.hit_target = True

        if self.last_ideal_projectile and self.last_ideal_projectile.is_active:
            self.last_ideal_projectile.update(effective_dt)
            screen_pos = adv_to_screen_coords((self.last_ideal_projectile.x, self.last_ideal_projectile.y), zoom, self.CANNON_ORIGIN_PIX)
            if self.ideal_trajectories:
                self.ideal_trajectories[-1].append(screen_pos)
        
        if not active_projectiles_exist and self.simulation_running:
            self.simulation_running = False
            self.buttons['launch'].disabled = False
            self.buttons['launch'].text = "LAUNCH"

    def draw_all(self):
        self.draw_simulation_area()
        self.draw_gui_panel()

    def draw_simulation_area(self):
        
        self.screen.set_clip(self.sim_rect)
        
        
        for y in range(self.sim_rect.top, self.sim_rect.bottom):
            lerp = y / self.sim_rect.height
            color = (
                SKY_BLUE_TOP[0] * (1 - lerp) + SKY_BLUE_BOTTOM[0] * lerp,
                SKY_BLUE_TOP[1] * (1 - lerp) + SKY_BLUE_BOTTOM[1] * lerp,
                SKY_BLUE_TOP[2] * (1 - lerp) + SKY_BLUE_BOTTOM[2] * lerp,
            )
            pygame.draw.line(self.screen, color, (self.sim_rect.left, y), (self.sim_rect.right, y))
            
        pygame.draw.rect(self.screen, GRASS_GREEN, (self.sim_rect.left, self.GROUND_Y, self.sim_rect.width, self.sim_rect.height - self.GROUND_Y))
        pygame.draw.line(self.screen, BLACK, (self.sim_rect.left, self.GROUND_Y), (self.sim_rect.right, self.GROUND_Y), 3)
        
        zoom = self.sliders['zoom'].get_value()
        if self.target_pos_m:
            target_pix_pos = adv_to_screen_coords(self.target_pos_m, zoom, self.CANNON_ORIGIN_PIX)
            target_pix_rad = int(self.target_radius_m * zoom)
            if target_pix_rad > 0 and self.sim_rect.collidepoint(target_pix_pos):
                pygame.draw.circle(self.screen, TARGET_COLOR, target_pix_pos, target_pix_rad)
                pygame.draw.circle(self.screen, WHITE, target_pix_pos, int(target_pix_rad * 0.6), max(1, int(target_pix_rad * 0.1)))
                pygame.draw.circle(self.screen, TARGET_COLOR, target_pix_pos, int(target_pix_rad * 0.3))
        
        for trajectory in self.ideal_trajectories:
            if len(trajectory) > 2:
                for i in range(0, len(trajectory) - 1, 10):
                    start = trajectory[i]
                    end_index = min(i + 5, len(trajectory) - 1)
                    end = trajectory[end_index]
                    if self.sim_rect.collidepoint(start) and self.sim_rect.collidepoint(end):
                        pygame.draw.line(self.screen, DARK_GRAY, start, end, 2)
                        
        for trajectory in self.trajectories:
            if len(trajectory) > 1:
                valid_points = [p for p in trajectory if self.sim_rect.collidepoint(p)]
                if len(valid_points) > 1:
                    pygame.draw.lines(self.screen, RED, False, valid_points, 3)
                        
        if self.last_projectile:
            self.last_projectile.draw(self.screen, zoom, self.CANNON_ORIGIN_PIX, self.sim_rect)
            
        self.draw_cannon()
        
        title_text = self.font_large.render("Simulation Area (RK4 Engine)", True, DARK_GRAY)
        self.screen.blit(title_text, (self.sim_rect.centerx - title_text.get_width() // 2, 10))
        
        
        self.screen.set_clip(None)
        
        
        pygame.draw.rect(self.screen, DARK_GRAY, self.sim_rect, 5)


    def draw_cannon(self):
        angle_rad = math.radians(self.sliders['angle'].get_value())
        length = 30
        
        end_x = self.CANNON_ORIGIN_PIX[0] + length * math.cos(angle_rad)
        end_y = self.CANNON_ORIGIN_PIX[1] - length * math.sin(angle_rad)
        
        pygame.draw.line(self.screen, BLACK, self.CANNON_ORIGIN_PIX, (end_x, end_y), 10)
        pygame.draw.circle(self.screen, DARK_GRAY, self.CANNON_ORIGIN_PIX, 10)

    def draw_gui_panel(self):
        pygame.draw.rect(self.screen, GRAY, self.ui_rect)
        
        title_text = self.font_large.render("Control Panel", True, BLACK)
        self.screen.blit(title_text, (self.ui_rect.centerx - title_text.get_width() // 2, 10))
        
        for key, tab_btn in self.tab_buttons.items():
            tab_btn.draw(self.screen, self.active_tab == key)
            
        active_panel_rect = (self.ui_rect.x + 10, 80, self.ui_rect.width - 20, 210)
        pygame.draw.rect(self.screen, GRAPH_BG, active_panel_rect, border_radius=5)
        
        for widget in self.widgets_by_tab[self.active_tab]:
            widget.draw(self.screen, self.font_small)
            
        self.altitude_graph.draw(self.screen)
            
        for button in self.buttons.values():
            button.draw(self.screen, self.font_medium)
            
        self.draw_data_readouts(self.ui_rect.x + 20)

    def draw_data_readouts(self, panel_x):
        y_pos = self.data_readout_y
        
        title = self.font_medium.render("--- Last Launch Data ---", True, BLACK)
        self.screen.blit(title, (panel_x, y_pos))
        y_pos += 30

        if not self.last_projectile:
            no_data_text = self.font_small.render("Launch a projectile to see data.", True, DARK_GRAY)
            self.screen.blit(no_data_text, (panel_x, y_pos))
            return

        proj = self.last_projectile
        data = [
            f"Time: {proj.time:.2f} s",
            f"Max Height: {proj.max_height:.2f} m",
            f"Range (Distance): {proj.x:.2f} m",
            f"Current Speed: {math.sqrt(proj.vx**2 + proj.vy**2):.2f} m/s",
        ]
        
        if self.target_pos_m:
            hit_text = "YES!" if self.hit_target else "No"
            data.append(f"Hit Target: {hit_text}")

        for line in data:
            text_surf = self.font_small.render(line, True, BLACK)
            self.screen.blit(text_surf, (panel_x, y_pos))
            y_pos += 20