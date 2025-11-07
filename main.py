import pygame
from app import MainApp

if __name__ == "__main__":
   
    pygame.init()
    pygame.font.init()
    
    
    app = MainApp()
    
    app.run()
    
    
    pygame.quit()