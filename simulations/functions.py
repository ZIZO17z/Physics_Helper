# -*- coding: utf-8 -*-
import pygame
import math
import numpy as np


from constants import *
from gui_components import Adv_Slider, Adv_Button, Adv_TextBox

class FunctionPlotter:
    def __init__(self, screen, screen_rect, fonts):
        self.screen = screen
        self.screen_rect = screen_rect
        self.font_small = fonts['small']
        self.font_medium = fonts['medium']
        self.font_large = fonts['large']
        
        
        self.sim_rect = pygame.Rect(0, 0, 1000, screen_rect.height)
        self.ui_rect = pygame.Rect(1000, 0, 300, screen_rect.height)
        self.origin = [self.sim_rect.centerx, self.sim_rect.centery]
        
        self.points = []
        self.function_string = "x**2 / 50"
        self.error_message = ""
        
        self.create_gui_elements()
        self.active_textbox = self.textboxes['function']
        self.textboxes['function'].active = True
        
        self.plot_function() 

    def create_gui_elements(self):
        self.sliders = {}
        self.buttons = {}
        self.textboxes = {}
        
        panel_x = self.ui_rect.x + 20
        panel_w = self.ui_rect.width - 40
        w = panel_w
        
        y_pos = self.ui_rect.y + 90
        
        
        label_surf = self.font_medium.render("f(x) =", True, BLACK)
        self.screen.blit(label_surf, (panel_x, y_pos + 5))
        tb_x = panel_x + label_surf.get_width() + 5
        tb_w = w - label_surf.get_width() - 5
        self.textboxes['function'] = Adv_TextBox(tb_x, y_pos, tb_w, 40, self.function_string, self.font_medium, mode='function')
        y_pos += 60
        
        self.buttons['plot'] = Adv_Button(panel_x, y_pos, w, 40, "PLOT", GREEN)
        y_pos += 70
        
        
        self.sliders['x_range'] = Adv_Slider(panel_x, y_pos, w - 90, 20, 1, 100, 20, "X Range (+/-)", "")
        self.textboxes['x_range'] = Adv_TextBox(panel_x + w - 80, y_pos, 70, 30, "20", self.font_medium)
        y_pos += 50
        
        self.sliders['y_scale'] = Adv_Slider(panel_x, y_pos, w - 90, 20, 0.1, 10.0, 1.0, "Y Scale", "x")
        self.textboxes['y_scale'] = Adv_TextBox(panel_x + w - 80, y_pos, 70, 30, "1.0", self.font_medium)
        y_pos += 70

        
        self.info_y_pos = y_pos
        
        self.buttons['back'] = Adv_Button(panel_x, self.ui_rect.height - 60, w, 40, "Back to Menu", DARK_GRAY)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if self.active_textbox:
                self.active_textbox.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.active_textbox.active = False
                    self.active_textbox = None
                    if self.textboxes['function'].text != self.function_string:
                        self.plot_function() 
                    else:
                        
                        for key, tb in self.textboxes.items():
                            if key != 'function' and tb == self.active_textbox:
                                self.sync_widgets('textbox', key)
                                self.plot_function()
                                break
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.active_textbox and not self.active_textbox.is_over(mouse_pos):
                    self.active_textbox.active = False
                    self.active_textbox = None

                if self.ui_rect.collidepoint(mouse_pos):
                    for key, tb in self.textboxes.items():
                        if tb.is_over(mouse_pos):
                            self.active_textbox = tb
                            tb.active = True
                            break
                    
                    if not self.active_textbox:
                        if self.buttons['plot'].is_over(mouse_pos):
                            self.plot_function()
                        elif self.buttons['back'].is_over(mouse_pos):
                            return 'main_menu'

            
            for key, slider in self.sliders.items():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if slider.is_over(mouse_pos):
                        slider.dragging = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if slider.dragging:
                        slider.dragging = False
                        self.sync_widgets('slider', key)
                        self.plot_function() 
                if event.type == pygame.MOUSEMOTION and slider.dragging:
                    slider.set_value_from_pos(mouse_pos[0])
                    self.sync_widgets('slider', key)
        return None

    def plot_function(self):
        self.function_string = self.textboxes['function'].text
        self.error_message = ""
        self.points = []
        
        try:
            x_range = self.sliders['x_range'].get_value()
            y_scale = self.sliders['y_scale'].get_value()
            
            num_points = self.sim_rect.width
            x_math = np.linspace(-x_range, x_range, num_points)
            
            
            safe_dict = {
                "np": np,
                "x": x_math,
                "sin": np.sin,
                "cos": np.cos,
                "tan": np.tan,
                "pow": np.power,
                "abs": np.abs,
                "log": np.log,
                "log10": np.log10,
                "exp": np.exp,
                "sqrt": np.sqrt,
                "pi": np.pi,
                "e": np.e
            }
            
            
            with np.errstate(divide='ignore', invalid='ignore'):
                y_math = eval(self.function_string, {"__builtins__": {}}, safe_dict)
            
            
            
            x_pix = (x_math + x_range) * (self.sim_rect.width / (2 * x_range))
            y_pix = self.origin[1] - (y_math * y_scale)
            
           
            y_pix[np.isinf(y_pix)] = np.nan
            
            self.points = []
            segment = []
            for i in range(len(x_pix)):
                if np.isnan(y_pix[i]):
                    if len(segment) > 1:
                        self.points.append(segment)
                    segment = []
                else:
                    segment.append((int(x_pix[i]), int(y_pix[i])))
            if len(segment) > 1:
                self.points.append(segment)

        except Exception as e:
            self.error_message = f"Error: {str(e)}"

    def sync_widgets(self, source_type, key):
        try:
            if source_type == 'slider':
                slider = self.sliders[key]
                textbox = self.textboxes[key]
                textbox.text = f"{slider.get_value():.1f}"
            elif source_type == 'textbox':
                slider = self.sliders[key]
                textbox = self.textboxes[key]
                slider.set_value(textbox.get_value_as_float())
        except (ValueError, KeyError):
            pass

    def update_simulation(self):
        
        pass

    def draw_all(self):
        self.draw_simulation_area()
        self.draw_gui_panel()

    def draw_simulation_area(self):
        self.screen.set_clip(self.sim_rect)
        pygame.draw.rect(self.screen, BLACK, self.sim_rect)
        
        
        x_range = self.sliders['x_range'].get_value()
        y_scale = self.sliders['y_scale'].get_value()
        
        
        grid_spacing_x_math = max(1, round(x_range / 10))
        grid_spacing_x_pix = (self.sim_rect.width / (x_range * 2)) * grid_spacing_x_math
        
        grid_spacing_y_math = max(1, round((self.sim_rect.height / 2) / y_scale / 10))
        grid_spacing_y_pix = grid_spacing_y_math * y_scale
        
        
        if grid_spacing_x_pix > 0:
            for i in range(int(self.sim_rect.width / grid_spacing_x_pix) + 1):
                x = self.origin[0] + i * grid_spacing_x_pix
                pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, self.sim_rect.height), 1)
                x = self.origin[0] - i * grid_spacing_x_pix
                pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, self.sim_rect.height), 1)
            
        
        if grid_spacing_y_pix > 0:
            for i in range(int(self.sim_rect.height / grid_spacing_y_pix) + 1):
                y = self.origin[1] + i * grid_spacing_y_pix
                pygame.draw.line(self.screen, DARK_GRAY, (0, y), (self.sim_rect.width, y), 1)
                y = self.origin[1] - i * grid_spacing_y_pix
                pygame.draw.line(self.screen, DARK_GRAY, (0, y), (self.sim_rect.width, y), 1)

        
        pygame.draw.line(self.screen, WHITE, (0, self.origin[1]), (self.sim_rect.width, self.origin[1]), 2)
        pygame.draw.line(self.screen, WHITE, (self.origin[0], 0), (self.origin[0], self.sim_rect.height), 2)
        
        
        if not self.error_message:
            for segment in self.points:
                pygame.draw.lines(self.screen, ORANGE, False, segment, 3)
        
        self.screen.set_clip(None)
        pygame.draw.rect(self.screen, DARK_GRAY, self.sim_rect, 5)

    def draw_gui_panel(self):
        pygame.draw.rect(self.screen, GRAY, self.ui_rect)
        
        title_text = self.font_large.render("Function Plotter", True, BLACK)
        self.screen.blit(title_text, (self.ui_rect.centerx - title_text.get_width() // 2, self.ui_rect.y + 20))
        
        active_panel_rect = (self.ui_rect.x + 10, self.ui_rect.y + 80, self.ui_rect.width - 20, 390)
        pygame.draw.rect(self.screen, GRAPH_BG, active_panel_rect, border_radius=5)

        for widget in self.sliders.values(): widget.draw(self.screen, self.font_small)
        for widget in self.textboxes.values(): widget.draw(self.screen, self.font_medium)
        for widget in self.buttons.values(): widget.draw(self.screen, self.font_medium)
            
        
        y_pos = self.info_y_pos
        if self.error_message:
            err_surf = self.font_small.render(self.error_message, True, RED)
            self.screen.blit(err_surf, (self.ui_rect.x + 20, y_pos))
        else:
            
            mouse_pos = pygame.mouse.get_pos()
            if self.sim_rect.collidepoint(mouse_pos):
                x_range = self.sliders['x_range'].get_value()
                y_scale = self.sliders['y_scale'].get_value()
                
                x_math = (mouse_pos[0] - self.origin[0]) / (self.sim_rect.width / (2 * x_range))
                y_math = (self.origin[1] - mouse_pos[1]) / y_scale
                
                coord_text = f"Mouse: ({x_math:.2f}, {y_math:.2f})"
                coord_surf = self.font_medium.render(coord_text, True, BLACK)
                self.screen.blit(coord_surf, (self.ui_rect.x + 20, y_pos))
        
        y_pos += 40
        info = [
            "Allowed:",
            " x, +, -, *, /, **",
            " sin(), cos(), tan()",
            " sqrt(), log(), exp()",
            " abs(), pow(), pi, e"
        ]
        for line in info:
            text_surf = self.font_small.render(line, True, DARK_GRAY)
            self.screen.blit(text_surf, (self.ui_rect.x + 20, y_pos))
            y_pos += 20