import pygame
from pygame.locals import *
import myStorage
from BackgroundProcesses import file_make, EstablishNewNovel#, mySpellCheck, webnovel_cleaner, webnovel_scraper


class ProgramWindow():
    
    def __init__(self):
        self.colour_pallet = {
            'bg_colour': (230, 220, 220),
            'button_colour': (165, 150, 127)
        }
        self.screen_size = pygame.display.list_modes()[0]
        self.window = pygame.display.set_mode(self.screen_size, pygame.FULLSCREEN)   
        pygame.display.set_caption("Webnovel Downloader")
        
        #Create Page Layouts
        self.home_page = self.layout_homepage()
        
        self.current_page = self.home_page
        

        return None

    
    
    def layout_homepage(self):
        page_layout = myStorage.MyList(self.window)
        win_size = win_width, win_height = self.window.get_size()
        
        # Fill background
        background = self.create_block(
            win_size, 
            self.colour_pallet['bg_colour'], 
            self.window, 
            (0, 0), 
            page_layout
        )
        button_1 = self.create_block(
            (win_width // 2, win_height // 10),
            self.colour_pallet['button_colour'],
            background,
            (background.get_width()//2 - win_width // 4,
             background.get_height()//2 - win_height // 20),
            page_layout
        )
        return page_layout
    
    
    def toggle_fullscreen(self):
        screen = self.window
        screen_size = screen.get_size
        screen_size_list = pygame.display.list_modes()
        
        tmp = screen.convert()
        caption = pygame.display.get_caption()
        cursor = pygame.mouse.get_cursor()  # Duoas 16-04-2007 
        
        flags = screen.get_flags()
        bits = screen.get_bitsize()
        
        pygame.display.quit()
        pygame.display.init()
        
        if screen_size == screen_size_list[0]:
            screen = pygame.display.set_mode(screen_size_list[2],flags^FULLSCREEN,bits)
        else:
            screen = pygame.display.set_mode(screen_size_list[0],flags^FULLSCREEN,bits)
    
        self.home_page = self.layout_homepage()        
        
        screen.blit(tmp, (0,0))
        pygame.display.set_caption(*caption)
    
        pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??
    
        pygame.mouse.set_cursor( *cursor )  # Duoas 16-04-2007
        
        self.window = screen
        return screen
    
    
    def create_block(self, width_height, colour, parent, coords, block_list):
        #block_size = (width * BASE_UNIT, height * BASE_UNIT)
        block = pygame.Surface(width_height)
        block = block.convert()
        block.fill(colour)
        block_list.append(block, parent, coords)
        return block
    
    
    def draw_screen(self):
        root_block = self.current_page.root_node
        for block, parent, position in reversed(self.current_page.branch(root_block)):
            parent.blit(block, position)    
        pygame.display.flip()
        return None


def main():
    pygame.init()
    program_instance = ProgramWindow()
    
    # Mainloop
    quit = False
    while not quit:
    
        for event in pygame.event.get():
            if (event.type is KEYDOWN and event.key == K_RETURN
                    and (event.mod&(KMOD_LALT|KMOD_RALT)) != 0):
                program_instance.toggle_fullscreen()
            if event.type is QUIT: quit = True
            if event.type is KEYDOWN and event.key == K_ESCAPE: quit = True
            
        program_instance.draw_screen()
        pygame.time.delay(50)
        
    pygame.quit()


if __name__ == '__main__':
    main()