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

import pygame as pg
import threading
from canjamsynth import CanJamSynth
from number_midi import NOTES, note_to_number

# Define constants
# (Your constants)

# Global variables
# (Your global variables)

# Function to get note index from row and column
# (Your function to get note index)

# Function to draw the grid
# (Your function to draw the grid)

def main():
    # Initialize Pygame
    pg.init()

    # Initialize the screen
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("CanJam")

    screen.fill(WHITE)
    # Initialize grid colors
    grid_colors = [[GRAY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Make the synth 
    gameSynth = CanJamSynth()

    # Variable to keep track of the current grid square where the mouse button is held down
    current_grid_square = None

    # Variable to control the sustain thread
    sustain = False
    
    # Thread lock
    lock = threading.Lock()
  
    running = True

    def note_on_and_red(row, col):
        grid_colors[row][col] = RED  
        draw_grid(grid_colors, game_obj= pg, screen = screen)
        pg.display.flip()

        note_index = get_note_index(row, col)
        print("Note clicked:", note_index)
        
        gameSynth.play_note(note_index)

    def sustain_thread():
        nonlocal sustain
        while True:
            with lock:
                if sustain and current_grid_square:
                    note_on_and_red(*current_grid_square)

    sustain_thread = threading.Thread(target=sustain_thread)
    sustain_thread.start()

    while running:
        for event in pg.event.get():

            if event.type == pg.QUIT:
                running = False
                print("quit canjam")

            elif event.type == pg.MOUSEBUTTONDOWN:
                # Check if left mouse button is pressed
                if event.button == 1:
                    # Get the position of the mouse click
                    mouse_pos = pg.mouse.get_pos()
                    col = mouse_pos[0] // (GRID_SQUARE_SIZE + GRID_MARGIN)
                    row = mouse_pos[1] // (GRID_SQUARE_SIZE + GRID_MARGIN)
                    note_on_and_red(row, col)
                    current_grid_square = (row, col)  # Update the current grid square
                    sustain = True

            elif event.type == pg.MOUSEBUTTONUP:
                # Check if left mouse button is released
                if event.button == 1:
                    sustain = False
                    current_grid_square = None  # Reset the current grid square

        # If the left mouse button is held down
        if pg.mouse.get_pressed()[0]:
            # Get the current mouse position
            mouse_pos = pg.mouse.get_pos()
            col = mouse_pos[0] // (GRID_SQUARE_SIZE + GRID_MARGIN)
            row = mouse_pos[1] // (GRID_SQUARE_SIZE + GRID_MARGIN)
            if (row, col) != current_grid_square:
                # If the mouse moves to a different grid square, trigger note_on_and_red for the new square
                if current_grid_square:
                    grid_colors[current_grid_square[0]][current_grid_square[1]] = GRAY
                note_on_and_red(row, col)
                current_grid_square = (row, col)

        # Clear the screen
        # screen.fill(WHITE)

        # Draw the grid with updated colors
        draw_grid(grid_colors, game_obj= pg, screen = screen)
        
        # Update the display
        pg.display.flip()
        
    # Stop the sustain thread
    sustain_thread.join()

    # Quit Pygame
    pg.quit()

if __name__ == "__main__":
    main()
