# program to display a notes grid with corresponding notes displayed
# that then plays the notes on keypress to the specified grid area 

from canjamsynth import CanJamSynth
from number_midi import NOTES, note_to_number


import canjam.demo.pygame_trials.button as button
import pygame as pg

# Define constants
GRID_SIZE = 9
GRID_SQUARE_SIZE = 50
GRID_MARGIN = 5
GRID_BORDER_SIZE = 70
SCREEN_HEIGHT = (GRID_SQUARE_SIZE + GRID_MARGIN) * GRID_SIZE 
SCREEN_WIDTH  = (GRID_SQUARE_SIZE + GRID_MARGIN) * GRID_SIZE 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0) # TODO: generate a random color per person for this 
CURRENT_NOTE = 0 


#constatns for the synth 
STARTCHANNEL = 0 

#game logic 
game_play_on = False

#game fonts
TEXT_COL = (0, 0, 0)


def draw_text(text:str, font:str, text_col, x:int, y:int, screen): 
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Function to get note index from row and column
def get_note_index(row:int, col:int):
    return (row * GRID_SIZE + col) + 11

# Function to calculate the starting position of the grid
def calculate_grid_start_position():
    grid_width = (GRID_SIZE * (GRID_SQUARE_SIZE + GRID_MARGIN)) - GRID_MARGIN
    grid_height = (GRID_SIZE * (GRID_SQUARE_SIZE + GRID_MARGIN)) - GRID_MARGIN
    start_x = (SCREEN_WIDTH - grid_width) // 2
    start_y = (SCREEN_HEIGHT - grid_height) // 2
    return start_x, start_y

# Function to draw the grid
def draw_grid(colors, game_obj, screen):
    start_x, start_y = calculate_grid_start_position()
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pg.Rect(
               start_x + col * (GRID_SQUARE_SIZE + GRID_MARGIN),
               start_y + row * (GRID_SQUARE_SIZE + GRID_MARGIN),
                GRID_SQUARE_SIZE,
                GRID_SQUARE_SIZE,
            )
            game_obj.draw.rect(screen, colors[row][col], rect)


def note_on_and_red(row, col, screen, grid_colors, gameSynth):
       grid_colors[row][col] = RED  
       draw_grid(grid_colors, game_obj= pg, screen = screen)
       pg.display.flip()
       # clicked_squares.add((row, col)) 
       
       note_index = get_note_index(row, col)
       print("Note clicked:", note_index)
       
       gameSynth.play_note(note_index)
       grid_colors[row][col] = GRAY


def main():
    # Initialize Pygame
    pg.init()

    # Initialize the screen
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("CanJam")

    # Import assets
    # exit_img = pg.image.load('images/exit_button.png').convert_alpha()

    screen.fill(WHITE)

    #font defns
    font = pg.font.SysFont("arialblack", 40)

    running = True

    if not game_play_on: 
        draw_text("PRESS SPACE TO PAUSE", font, TEXT_COL, 0, 0,  screen)
    else:
        grid_colors = [[GRAY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Exit button for the screen
        exit_button = button.Button(450, 450, exit_img, .2)

        # Make the synth
        gameSynth = CanJamSynth()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                print("Quit CanJam")

        if pg.mouse.get_pressed()[0]:
            # Mouse is being held
            mouse_pos = pg.mouse.get_pos()
            col = mouse_pos[0] // (GRID_SQUARE_SIZE + GRID_MARGIN)
            row = mouse_pos[1] // (GRID_SQUARE_SIZE + GRID_MARGIN)
            note_on_and_red(row, col, screen, grid_colors, gameSynth)

        # Clear the screen
        screen.fill(WHITE)

        # Draw the grid with updated colors
        draw_grid(grid_colors, game_obj=pg, screen=screen)

        # Draw the exit button
        exit_button.draw(screen)

        # Update the display
        pg.display.update()

    # Quit Pygame
    pg.quit()

if __name__ == "__main__":
    main()
