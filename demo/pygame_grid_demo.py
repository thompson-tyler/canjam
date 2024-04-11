# program to display a notes grid with corresponding notes displayed
# that then plays the notes on keypress to the specified grid area 

from canjamsynth import CanJamSynth
from number_midi import NOTES, note_to_number

import pygame as pg

# Define constants
GRID_SIZE = 9
GRID_SQUARE_SIZE = 50
GRID_MARGIN = 5
SCREEN_HEIGHT = (GRID_SQUARE_SIZE + GRID_MARGIN) * GRID_SIZE
SCREEN_WIDTH  = (GRID_SQUARE_SIZE + GRID_MARGIN) * GRID_SIZE
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0) # TODO: generate a random color per person for this 
CURRENT_NOTE = 0 


#constatns for the synth 
STARTCHANNEL = 0 


# Function to get note index from row and column
def get_note_index(row, col):
    return (row * GRID_SIZE + col) + 11

# Function to draw the grid
def draw_grid(colors, game_obj, screen):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pg.Rect(
                col * (GRID_SQUARE_SIZE + GRID_MARGIN),
                row * (GRID_SQUARE_SIZE + GRID_MARGIN),
                GRID_SQUARE_SIZE,
                GRID_SQUARE_SIZE,
            )
            game_obj.draw.rect(screen, colors[row][col], rect)


def main():
    # Initialize Pygame
    pg.init()

    # Initialize the screen
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("CanJam")

    screen.fill(WHITE)
    # Initialize grid colors
    grid_colors = [[GRAY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    clicked_squares = set()  # Set to keep track of currently clicked squares
    
    # make the synth 
    gameSynth = CanJamSynth()
  
    running = True

    def note_on_and_red(row, col):
        grid_colors[row][col] = RED  
        draw_grid(grid_colors, game_obj= pg, screen = screen)
        pg.display.flip()

        # clicked_squares.add((row, col)) 
        
        note_index = get_note_index(row, col)
        print("Note clicked:", note_index)
        
        gameSynth.play_note(note_index)
        grid_colors[row][col] = GRAY

    while running:
        for event in pg.event.get():

            if event.type == pg.QUIT:
                running = False
                print("quit canjam")
                # Check if mouse click is within the grid area
            
            if pg.mouse.get_pressed()[0]:
                # mouse is being held                
                mouse_pos = pg.mouse.get_pos()
                col = mouse_pos[0] // (GRID_SQUARE_SIZE + GRID_MARGIN)
                row = mouse_pos[1] // (GRID_SQUARE_SIZE + GRID_MARGIN)
                note_on_and_red(row, col)
                    
            # elif event.type == pg.MOUSEBUTTONUP:
            #     held = False
            # else:
                # for square in clicked_squares:
                #     grid_colors[square[0]][square[1]] = GRAY
                # clicked_squares.clear() 


        # Clear the screen
        # screen.fill(WHITE)

        # Draw the grid with updated colors
        draw_grid(grid_colors, game_obj= pg, screen = screen)
        
        # Update the display
        pg.display.flip()
        
    # Quit Pygame
    pg.quit()

    
if __name__ == "__main__":
    main()
    
    