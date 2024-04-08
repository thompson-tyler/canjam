# program to display a notes grid with corresponding notes displayed
# that then plays the notes on keypress to the specified grid area 

# from canjamsynth import CanJamsynth
from number_midi import NOTES, note_to_number

import pygame as pg

# Initialize Pygame
pg.init()

# Define constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 12  # Assuming a 12x12 grid for 132 notes
GRID_MARGIN = 5
GRID_SQUARE_SIZE = 50
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0) # TODO: generate a random color per person for this 

# Initialize the screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Note Grid")

# Function to draw the grid
def draw_grid(colors):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pg.Rect(
                col * (GRID_SQUARE_SIZE + GRID_MARGIN),
                row * (GRID_SQUARE_SIZE + GRID_MARGIN),
                GRID_SQUARE_SIZE,
                GRID_SQUARE_SIZE,
            )
            pg.draw.rect(screen, colors[row][col], rect)

# Initialize grid colors
grid_colors = [[GRAY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
clicked_squares = set()  # Set to keep track of currently clicked squares

# Function to get note index from row and column
def get_note_index(row, col):
    return row * GRID_SIZE + col


running = True


while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            # Check if mouse click is within the grid area
            mouse_pos = pg.mouse.get_pos()
            
            col = mouse_pos[0] // (GRID_SQUARE_SIZE + GRID_MARGIN)
            row = mouse_pos[1] // (GRID_SQUARE_SIZE + GRID_MARGIN)
            
            if col < GRID_SIZE and row < GRID_SIZE:
                
                # Change color of the clicked square
                
                grid_colors[row][col] = RED  # Change to any color you desire
                
                clicked_squares.add((row, col))  # Add the clicked square to the set
                
                note_index = get_note_index(row, col)
                click_start_time = pg.time.get_ticks()
                
                print("Note clicked:", note_index)
                
        elif event.type == pg.MOUSEBUTTONUP:
            click_end_time = pg.time.get_ticks()
            endtime = (click_end_time - click_start_time) / 1000 #convert ticks to seconds
            print(f"done clicking note: {note_index}, for {endtime} seconds")
            
            for square in clicked_squares:
                grid_colors[square[0]][square[1]] = GRAY
            clicked_squares.clear() 
            

    # Clear the screen
    screen.fill(WHITE)

    # Draw the grid with updated colors
    draw_grid(grid_colors)

    # Update the display
    pg.display.flip()

# Quit Pygame
pg.quit()
