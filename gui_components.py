# -*- coding: utf-8 -*-
import pygame
from constants import *









class Adv_Slider:
    def __init__(self, x, y, w, h, min_val, max_val, current_val, label, unit):
        self.rect = pygame.Rect(x, y + 10, w, h)
        self.handle_rect = pygame.Rect(x, y, 10, h + 20)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.label = label
        self.unit = unit
        self.dragging = False
        self.update_handle_pos()

    def update_handle_pos(self):
        if (self.max_val - self.min_val) == 0:
            percent = 0
        else:
            percent = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + percent * self.rect.width

    def set_value_from_pos(self, x_pos):
        x_pos = max(self.rect.x, min(x_pos, self.rect.right))
        percent = (x_pos - self.rect.x) / self.rect.width
        self.current_val = self.min_val + percent * (self.max_val - self.min_val)
        self.update_handle_pos()

    def set_value(self, val):
        self.current_val = max(self.min_val, min(val, self.max_val))
        self.update_handle_pos()

    def get_value(self):
        return self.current_val

    def is_over(self, pos):
        return self.handle_rect.inflate(10, 10).collidepoint(pos)

    def draw(self, screen, font=None):
        if font is None:
            font = pygame.font.SysFont("Arial", 14)
        label_text = f"{self.label}: {self.current_val:.2f} {self.unit}"
        text_surf = font.render(label_text, True, BLACK)
        screen.blit(text_surf, (self.rect.x, self.rect.y - 15))
        
        pygame.draw.rect(screen, DARK_GRAY, self.rect, border_radius=5)
        
        handle_color = BLUE if self.dragging else BLACK
        pygame.draw.rect(screen, handle_color, self.handle_rect, border_radius=3)

class Adv_Button:
    def __init__(self, x, y, w, h, text, color, disabled=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.pressed_color = tuple(max(c - 30, 0) for c in color)
        self.disabled_color = DISABLED_GRAY
        self.disabled = disabled

    def is_over(self, pos):
        return self.rect.collidepoint(pos) and not self.disabled

    def draw(self, screen, font=None):
        if font is None:
            font = pygame.font.SysFont("Arial", 18)
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        current_color = self.color
        if self.disabled:
            current_color = self.disabled_color
        elif self.is_over(mouse_pos):
            current_color = self.hover_color
            if mouse_pressed[0]:
                current_color = self.pressed_color
        
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
class Adv_TabButton:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = DARK_GRAY
        self.active_color = WHITE
        self.hover_color = (120, 120, 120)

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, is_active):
        color = self.active_color if is_active else self.color
        if not is_active and self.is_over(pygame.mouse.get_pos()):
            color = self.hover_color
            
        pygame.draw.rect(screen, color, self.rect, border_top_left_radius=8, border_top_right_radius=8)
        
        text_color = BLACK if is_active else WHITE
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class Adv_CheckBox:
    def __init__(self, x, y, w, h, label, font, initial_state=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.font = font
        self.checked = initial_state

    def is_over(self, pos):
        text_w = self.font.size(self.label)[0]
        full_rect = self.rect.union(pygame.Rect(self.rect.right + 5, self.rect.y, text_w, self.rect.height))
        return full_rect.collidepoint(pos)

    def toggle(self):
        self.checked = not self.checked

    def draw(self, screen, font=None):
        if font is None: font = self.font # Use self.font if None
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, GREEN, (self.rect.x + 3, self.rect.centery), (self.rect.centerx - 2, self.rect.bottom - 3), 3)
            pygame.draw.line(screen, GREEN, (self.rect.centerx - 2, self.rect.bottom - 3), (self.rect.right - 3, self.rect.y + 3), 3)
        
        text_surf = self.font.render(self.label, True, BLACK)
        screen.blit(text_surf, (self.rect.right + 5, self.rect.centery - text_surf.get_height() // 2))

class Adv_TextBox:
    def __init__(self, x, y, w, h, text, font, mode='numeric'):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.mode = mode

    def handle_event(self, event):
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.active = False
            
            elif self.mode == 'numeric':
                if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text) or (event.unicode == '-' and not self.text):
                    self.text += event.unicode
            
            elif self.mode == 'function':
                
                allowed_chars = "xabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/().** "
                if event.unicode in allowed_chars:
                    self.text += event.unicode
            
            self.cursor_visible = True
            self.cursor_timer = pygame.time.get_ticks()

    def get_value_as_float(self):
        try:
            return float(self.text)
        except ValueError:
            if self.text == "" or self.text == "-":
                return 0.0
            try:
                return float(self.text[:-1])
            except ValueError:
                return 0.0

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, font=None):
        if font is None: font = self.font # Use self.font if None
        color = BLUE if self.active else DARK_GRAY
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=3)
        
        text_surf = self.font.render(self.text, True, BLACK)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))
        
        if self.active:
            if (pygame.time.get_ticks() - self.cursor_timer) > 500:
                self.cursor_timer = pygame.time.get_ticks()
                self.cursor_visible = not self.cursor_visible
                
            if self.cursor_visible:
                cursor_x = self.rect.x + 5 + text_surf.get_width()
                if cursor_x > self.rect.right - 5:
                    cursor_x = self.rect.right - 5
                pygame.draw.line(screen, BLACK, (cursor_x, self.rect.y + 5), (cursor_x, self.rect.bottom - 5), 2)

class Adv_Graph:
    def __init__(self, rect, x_label, y_label, font, max_points=100):
        self.rect = rect
        self.x_label = x_label
        self.y_label = y_label
        self.font = font
        self.max_points = max_points
        self.data = []
        self.padding = 30
        self.plot_area = pygame.Rect(
            rect.x + self.padding, rect.y + 5,
            rect.width - self.padding - 5, rect.height - self.padding - 5
        )

    def clear_data(self):
        self.data = []

    def add_data_point(self, x, y):
        self.data.append((x, y))
        if len(self.data) > self.max_points:
            self.data.pop(0)

    def draw_axes(self, screen):
        pygame.draw.line(screen, BLACK, (self.plot_area.left, self.plot_area.bottom), (self.plot_area.right, self.plot_area.bottom), 2)
        pygame.draw.line(screen, BLACK, (self.plot_area.left, self.plot_area.bottom), (self.plot_area.left, self.plot_area.top), 2)

        x_label_surf = self.font.render(self.x_label, True, BLACK)
        screen.blit(x_label_surf, (self.plot_area.centerx - x_label_surf.get_width() // 2, self.plot_area.bottom + 5))
        
        y_label_surf = self.font.render(self.y_label, True, BLACK)
        y_label_surf = pygame.transform.rotate(y_label_surf, 90)
        screen.blit(y_label_surf, (self.plot_area.left - self.padding + 5, self.plot_area.centery - y_label_surf.get_height() // 2))

    def draw_data(self, screen):
        if len(self.data) < 2:
            return

        max_x = max(p[0] for p in self.data) if self.data else 1
        max_y = max(p[1] for p in self.data) if self.data else 1
        min_x = min(p[0] for p in self.data)
        min_y = 0 
        
        if max_x == min_x: max_x += 1
        if max_y <= min_y: max_y = min_y + 1

        points = []
        for x, y in self.data:
            x_norm = (x - min_x) / (max_x - min_x)
            y_norm = (y - min_y) / (max_y - min_y)
            
            x_pix = self.plot_area.left + x_norm * self.plot_area.width
            y_pix = self.plot_area.bottom - y_norm * self.plot_area.height
            points.append((x_pix, y_pix))
            
        pygame.draw.lines(screen, RED, False, points, 2)

        max_y_text = self.font.render(f"{max_y:.1f}", True, DARK_GRAY)
        screen.blit(max_y_text, (self.plot_area.left + 5, self.plot_area.top))
        max_x_text = self.font.render(f"{max_x:.1f}", True, DARK_GRAY)
        screen.blit(max_x_text, (self.plot_area.right - max_x_text.get_width() - 5, self.plot_area.bottom - max_x_text.get_height() - 5))

    def draw(self, screen):
        pygame.draw.rect(screen, GRAPH_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, GRAPH_GRID, self.plot_area, 1)
        
        self.draw_axes(screen)
        self.draw_data(screen)

# --- OLD GUI Classes (Used by Particle Sandbox) ---
class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, current_val, label, unit):
        self.rect = pygame.Rect(x, y + 10, w, h)
        self.handle_rect = pygame.Rect(x, y, 10, h + 20)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.label = label
        self.unit = unit
        self.dragging = False
        self.update_handle_pos()

    def update_handle_pos(self):
        if (self.max_val - self.min_val) == 0: percent = 0
        else: percent = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + percent * self.rect.width

    def set_value_from_pos(self, x_pos):
        x_pos = max(self.rect.x, min(x_pos, self.rect.right))
        percent = (x_pos - self.rect.x) / self.rect.width
        self.current_val = self.min_val + percent * (self.max_val - self.min_val)
        self.update_handle_pos()

    def set_value(self, val):
        self.current_val = max(self.min_val, min(val, self.max_val))
        self.update_handle_pos()

    def get_value(self): return self.current_val
    def is_over(self, pos): return self.handle_rect.inflate(10, 10).collidepoint(pos)

    def draw(self, screen, font=None):
        if font is None: font = pygame.font.SysFont("Arial", 14)
        label_text = f"{self.label}: {self.current_val:.2f} {self.unit}"
        text_surf = font.render(label_text, True, BLACK)
        screen.blit(text_surf, (self.rect.x, self.rect.y - 15))
        pygame.draw.rect(screen, DARK_GRAY, self.rect, border_radius=5)
        handle_color = BLUE if self.dragging else BLACK
        pygame.draw.rect(screen, handle_color, self.handle_rect, border_radius=3)

class Button:
    def __init__(self, x, y, w, h, text, color, disabled=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.pressed_color = tuple(max(c - 30, 0) for c in color)
        self.disabled_color = DISABLED_GRAY
        self.disabled = disabled

    def is_over(self, pos): return self.rect.collidepoint(pos) and not self.disabled

    def draw(self, screen, font=None):
        if font is None: font = pygame.font.SysFont("Arial", 18)
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        current_color = self.color
        if self.disabled: current_color = self.disabled_color
        elif self.is_over(mouse_pos):
            current_color = self.hover_color
            if mouse_pressed[0]: current_color = self.pressed_color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
class CheckBox:
    def __init__(self, x, y, w, h, label, font, initial_state=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.font = font
        self.checked = initial_state

    def is_over(self, pos):
        text_w = self.font.size(self.label)[0]
        full_rect = self.rect.union(pygame.Rect(self.rect.right + 5, self.rect.y, text_w, self.rect.height))
        return full_rect.collidepoint(pos)

    def toggle(self): self.checked = not self.checked

    def draw(self, screen, font=None):
        if font is None: font = self.font
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, GREEN, (self.rect.x + 3, self.rect.centery), (self.rect.centerx - 2, self.rect.bottom - 3), 3)
            pygame.draw.line(screen, GREEN, (self.rect.centerx - 2, self.rect.bottom - 3), (self.rect.right - 3, self.rect.y + 3), 3)
        text_surf = self.font.render(self.label, True, BLACK)
        screen.blit(text_surf, (self.rect.right + 5, self.rect.centery - text_surf.get_height() // 2))

class TextBox:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if not self.active: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER): self.active = False
            elif event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text) or (event.unicode == '-' and not self.text):
                self.text += event.unicode
            self.cursor_visible = True
            self.cursor_timer = pygame.time.get_ticks()

    def get_value_as_float(self):
        try: return float(self.text)
        except ValueError:
            if self.text == "" or self.text == "-": return 0.0
            try: return float(self.text[:-1])
            except ValueError: return 0.0

    def is_over(self, pos): return self.rect.collidepoint(pos)

    def draw(self, screen, font=None):
        if font is None: font = self.font
        color = BLUE if self.active else DARK_GRAY
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=3)
        text_surf = self.font.render(self.text, True, BLACK)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))
        
        if self.active:
            if (pygame.time.get_ticks() - self.cursor_timer) > 500:
                self.cursor_timer = pygame.time.get_ticks()
                self.cursor_visible = not self.cursor_visible
            if self.cursor_visible:
                cursor_x = self.rect.x + 5 + text_surf.get_width()
                if cursor_x > self.rect.right - 5: cursor_x = self.rect.right - 5
                pygame.draw.line(screen, BLACK, (cursor_x, self.rect.y + 5), (cursor_x, self.rect.bottom - 5), 2)

class Graph:
    def __init__(self, rect, x_label, y_label, font, max_points=100):
        self.rect = rect
        self.x_label = x_label
        self.y_label = y_label
        self.font = font
        self.max_points = max_points
        self.data = []
        self.padding = 30
        self.plot_area = pygame.Rect(rect.x + self.padding, rect.y + 5, rect.width - self.padding - 5, rect.height - self.padding - 5)

    def clear_data(self): self.data = []

    def add_data_point(self, x, y):
        self.data.append((x, y))
        if len(self.data) > self.max_points: self.data.pop(0)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAPH_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, GRAPH_GRID, self.plot_area, 1)
        
        pygame.draw.line(screen, BLACK, (self.plot_area.left, self.plot_area.bottom), (self.plot_area.right, self.plot_area.bottom), 2)
        pygame.draw.line(screen, BLACK, (self.plot_area.left, self.plot_area.bottom), (self.plot_area.left, self.plot_area.top), 2)
        x_label_surf = self.font.render(self.x_label, True, BLACK)
        screen.blit(x_label_surf, (self.plot_area.centerx - x_label_surf.get_width() // 2, self.plot_area.bottom + 5))
        y_label_surf = self.font.render(self.y_label, True, BLACK)
        y_label_surf = pygame.transform.rotate(y_label_surf, 90)
        screen.blit(y_label_surf, (self.plot_area.left - self.padding + 5, self.plot_area.centery - y_label_surf.get_height() // 2))

        if len(self.data) < 2: return




        max_x = max(p[0] for p in self.data)
        max_y = max(p[1] for p in self.data) if self.data else 1
        min_x = min(p[0] for p in self.data)
        min_y = 0
        
        if max_x == min_x: max_x += 1
        if max_y <= min_y: max_y = min_y + 1

        points = []
        for x, y in self.data:
            x_norm = (x - min_x) / (max_x - min_x)
            y_norm = (y - min_y) / (max_y - min_y)
            x_pix = self.plot_area.left + x_norm * self.plot_area.width
            y_pix = self.plot_area.bottom - y_norm * self.plot_area.height
            points.append((x_pix, y_pix))
            
        pygame.draw.lines(screen, RED, False, points, 2)

        max_y_text = self.font.render(f"{max_y:.0f}", True, DARK_GRAY)
        screen.blit(max_y_text, (self.plot_area.left + 5, self.plot_area.top))
        max_x_text = self.font.render(f"{max_x:.1f}", True, DARK_GRAY)
        screen.blit(max_x_text, (self.plot_area.right - max_x_text.get_width() - 5, self.plot_area.bottom - max_x_text.get_height() - 5))