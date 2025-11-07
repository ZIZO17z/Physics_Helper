import pygame
import sys 
from constants import *
from menu_button import Button 


from simulations.projectile import AdvancedProjectileLab
from simulations.collosion import ParticleSandbox
from simulations.functions import FunctionPlotter

class MainApp:
    def __init__(self):
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption("Physics Lab Menu")
        self.clock = pygame.time.Clock()
        
        
        try:
            self.BG = pygame.image.load("assets/Background.jpg")
            
            self.get_font = lambda size: pygame.font.Font("assets/font.ttf", size) 
        except pygame.error as e:
            
            print(f"WARNING: Menu assets not found. Using SysFont and solid color background. Error: {e}")
            self.BG = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.BG.fill((40, 40, 40)) 
            self.get_font = lambda size: pygame.font.SysFont("Arial", size, bold=True)
            
        self.running = True
        self.app_state = 'main_menu'
        
        
        sim_fonts = {
            'small': self.get_font(14),
            'medium': self.get_font(18),
            'large': self.get_font(26),
            'title': self.get_font(48)
        }
        
      
        self.advanced_projectile_lab = AdvancedProjectileLab(self.screen, self.screen_rect, sim_fonts)
        self.particle_sandbox = ParticleSandbox(self.screen, self.screen_rect, sim_fonts)
        self.function_plotter = FunctionPlotter(self.screen, self.screen_rect, sim_fonts)
        
       
        center_x = self.screen_rect.centerx
        
        try:
           
            play_img = pygame.image.load("assets/Play Rect.png")
            part_img = pygame.image.load("assets/Options Rect.png")
            func_img = pygame.image.load("assets/Options Rect.png")
            quit_img = pygame.image.load("assets/Quit Rect.png")
        except pygame.error:
            
            play_img = part_img = func_img = quit_img = None
            
        self.menu_buttons = {
            'PLAY': Button(image=play_img, pos=(center_x, 250), 
                           text_input="PROJECTILE LAB", font=self.get_font(40), 
                           base_color="#d7fcd4", hovering_color="White"),
            'PARTICLES': Button(image=part_img, pos=(center_x, 400), 
                              text_input="PARTICLE SANDBOX", font=self.get_font(40), 
                              base_color="#d7fcd4", hovering_color="White"),
            'FUNCTION': Button(image=func_img, pos=(center_x, 550), 
                              text_input="FUNCTION PLOTTER", font=self.get_font(40), 
                              base_color="#d7fcd4", hovering_color="White"),
            'QUIT': Button(image=quit_img, pos=(center_x, 700),
                           text_input="QUIT", font=self.get_font(40), 
                           base_color="#d7fcd4", hovering_color="White"),
        }

    def run(self):
        
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            
            if self.app_state == 'main_menu':
                self.handle_menu_events(events)
                self.draw_main_menu()
            
            
            elif self.app_state == 'projectile_lab':
                app_signal = self.advanced_projectile_lab.handle_events(events)
                if app_signal == 'main_menu':
                    self.app_state = 'main_menu'
                    pygame.display.set_caption("Physics Lab Menu")
                else:
                    self.advanced_projectile_lab.update_simulation()
                    self.advanced_projectile_lab.draw_all()
            
            elif self.app_state == 'particle_sandbox':
                app_signal = self.particle_sandbox.handle_events(events)
                if app_signal == 'main_menu':
                    self.app_state = 'main_menu'
                    pygame.display.set_caption("Physics Lab Menu")
                else:
                    self.particle_sandbox.update_simulation()
                    self.particle_sandbox.draw_all()
            
            elif self.app_state == 'function_plotter':
                app_signal = self.function_plotter.handle_events(events)
                if app_signal == 'main_menu':
                    self.app_state = 'main_menu'
                    pygame.display.set_caption("Physics Lab Menu")
                else:
                    self.function_plotter.update_simulation()
                    self.function_plotter.draw_all()
            
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_menu_events(self, events):
        
        menu_mouse_pos = pygame.mouse.get_pos()
        
        
        for button in self.menu_buttons.values():
            button.changeColor(menu_mouse_pos)
            
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_buttons['PLAY'].checkForInput(menu_mouse_pos):
                    self.app_state = 'projectile_lab'
                    pygame.display.set_caption("Advanced Projectile Lab (RK4 Engine)")
                    self.advanced_projectile_lab.reset_simulation()
                elif self.menu_buttons['PARTICLES'].checkForInput(menu_mouse_pos):
                    self.app_state = 'particle_sandbox'
                    pygame.display.set_caption("Particle Sandbox")
                elif self.menu_buttons['FUNCTION'].checkForInput(menu_mouse_pos):
                    self.app_state = 'function_plotter'
                    pygame.display.set_caption("Function Plotter")
                elif self.menu_buttons['QUIT'].checkForInput(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

    def draw_main_menu(self):
        self.screen.blit(self.BG, (0, 0))
        
        
        menu_text = self.get_font(100).render("PHYSICS LAB", True, "#b68f40")
        menu_rect = menu_text.get_rect(center=(self.screen_rect.centerx, 100))
        self.screen.blit(menu_text, menu_rect)

        
        for button in self.menu_buttons.values():
            button.update(self.screen)



    