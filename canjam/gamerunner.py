#  Note: NCS indicates Note, Color, Synth
#  message format struct = (note:int, color:(int,int,int), synth:str)

import pygame
from random import choice

# this Queue will be changed once we have handoff from @skylar and @tyler
from queue import Queue, Empty
from time import sleep
from canjam.sound_fonts.canjamsynth import CanJamSynth

# from canjam.logger import vprint
from canjam.message import Message, Sound, Die, Color, SynthType
from canjam.logger import vprint

WIDTH = 9

### GAME CONSTANTS ###
GRID_SQUARE_SIZE = 50
GRID_GAP = 5
GRID_MARGIN = 10
SCREEN_HEIGHT = (GRID_SQUARE_SIZE + GRID_GAP) * WIDTH + (2 * GRID_MARGIN) - GRID_GAP
SCREEN_WIDTH = (GRID_SQUARE_SIZE + GRID_GAP) * WIDTH + (2 * GRID_MARGIN) - GRID_GAP
ESCAPE_KEY = "\x1b"

PLAYER_COLORS = [
    Color.STRAWB.value,
    Color.ORANGE.value,
    Color.HONEY.value,
    Color.MATCHA.value,
    Color.MINT.value,
    Color.BLUEB.value,
]


class GameRunner:
    """A module that runs the CanJam game GUI using pygame."""

    def __init__(self, in_queue: Queue[Message], out_queue: Queue[Message]):
        self.in_queue = in_queue
        self.out_queue = out_queue

        # select a random Color and a random Synth
        self.color = choice(PLAYER_COLORS)
        self.synth_type = choice(list(SynthType))

        self.player_synth = CanJamSynth(font=self.synth_type)
        self.grid = [[Color.GRAY.value for _ in range(WIDTH)] for _ in range(WIDTH)]

    def draw_grid(self, game_obj, screen):
        """Draw the CanJam GUI's grid of colors."""
        for row in range(WIDTH):
            for col in range(WIDTH):
                rect = pygame.Rect(
                    (col * (GRID_SQUARE_SIZE + GRID_GAP)) + GRID_MARGIN,
                    (row * (GRID_SQUARE_SIZE + GRID_GAP)) + GRID_MARGIN,
                    GRID_SQUARE_SIZE,
                    GRID_SQUARE_SIZE,
                )
                game_obj.draw.rect(screen, self.grid[row][col], rect)

    def set_grid_color(self, row: int, col: int, color: Color, screen):
        """Set and re-render the specified color on the CanJam grid.

        Args:
            row (int): _description_
            col (int): _description_
            grid_colors (_type_): _description_
            screen (_type_): _description_
        """
        self.grid[row][col] = color
        self.draw_grid(pygame, screen)
        pygame.display.flip()
        sleep(0.09)  # TODO: why?
        self.grid[row][col] = Color.GRAY.value

    def run_game(self):
        """ """

        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption("CanJam")
        screen.fill(Color.WHITE.value)

        # TODO: optimize and put sound player and grid color setter in separate threads?
        running = True
        while running:
            # if user presses escape, shut down game
            # TODO: nice options GUI to set color and synth?
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    response = event.unicode
                    if response == ESCAPE_KEY:
                        self.out_queue.put(Die())
                        running = False

            # if user presses mouse, set current tile to their color
            if pygame.mouse.get_pressed()[0]:
                (xpos, ypos) = pygame.mouse.get_pos()
                in_bounds = (
                    xpos >= GRID_MARGIN
                    and xpos <= SCREEN_HEIGHT - GRID_MARGIN - GRID_GAP
                    and ypos >= GRID_MARGIN
                    and ypos <= SCREEN_HEIGHT - GRID_MARGIN - GRID_GAP
                )
                if in_bounds:
                    col = (xpos - GRID_MARGIN) // (GRID_SQUARE_SIZE + GRID_GAP)
                    row = (ypos - GRID_MARGIN) // (GRID_SQUARE_SIZE + GRID_GAP)

                    # create note from mouse position and send Sound to out_queue
                    self.set_grid_color(row, col, self.color, screen)

            self.draw_grid(game_obj=pygame, screen=screen)
            pygame.display.flip()

        pygame.display.quit()
        pygame.quit()
