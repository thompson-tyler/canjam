#  Note: NCS indicates Note, Color, Synth
#  message format struct = (note:int, color:(int,int,int), synth:str)

import pygame
from random import choice

# this Queue will be changed once we have handoff from @skylar and @tyler
from threading import Thread, Semaphore, Lock
from queue import Queue, Empty
from time import sleep
from canjam.sound_fonts.canjamsynth import CanJamSynth

# from canjam.logger import vprint
from canjam.message import Message, Sound, Die, Color, SynthType, Cell
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

        self.running = True
        self.screen_notifier = Semaphore(0)

        # select a random Color and a random Synth
        self.color = choice(PLAYER_COLORS)
        self.synth_type = choice(list(SynthType)).value

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

    def set_grid_color(self, row: int, col: int, color: Color, screen: pygame.Surface):
        """Set and re-render the specified color on the CanJam grid.

        Args:
            row (int): _description_
            col (int): _description_
            grid_colors (_type_): _description_
        """
        self.grid[row][col] = color
        
        self.draw_grid(game_obj=pygame, screen=screen)
        pygame.display.flip()

        sleep(0.025)  # TODO: why?

        self.draw_grid(game_obj=pygame, screen=screen)
        pygame.display.flip()

        self.grid[row][col] = Color.GRAY.value


    def sound_handler(self, color_queue: Queue[Cell]):
        """ """
        synth = CanJamSynth("piano")

        while self.running:
            match self.in_queue.get():
                case Die():
                    return
                # TODO: play note with different synth from different user?
                case Sound(note, color, synth_type):
                    synth.play_note(note)
                    (row, col) = (note // WIDTH, note % WIDTH)
                    color_queue.put(Cell(color, (row, col)))

    def run_game(self):
        """ """

        pygame.init()
        pygame.display.set_caption("CanJam")
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.fill(Color.WHITE.value)

        color_queue: Queue[Cell] = Queue()

        sound_player = Thread(target=GameRunner.sound_handler, 
                              args=[self, color_queue])

        sound_player.start()

        while self.running:
            try:
                match color_queue.get_nowait():
                    case Cell(color, (row, col)):
                       self.set_grid_color(row, col, color, screen)
            except Empty:
                pass

            # if user presses escape, shut down game
            # TODO: nice options GUI to set color and synth?
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    response = event.unicode
                    if response == ESCAPE_KEY:
                        self.in_queue.put(Die())
                        self.out_queue.put((Die(), None))
                        self.running = False

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
                    row = (ypos - GRID_MARGIN) // (GRID_SQUARE_SIZE + GRID_GAP)
                    col = (xpos - GRID_MARGIN) // (GRID_SQUARE_SIZE + GRID_GAP)

                    # create sound from mouse position, send to in_queue to
                    # play locally and out_queue to broadcast
                    sound = Sound(row * WIDTH + col, self.color, self.synth_type)
                    self.in_queue.put(sound)
                    self.out_queue.put((sound, None))

                    # set color and redraw screen to flash cell
                    self.set_grid_color(row, col, self.color, screen)

            self.draw_grid(game_obj=pygame, screen=screen)
            pygame.display.flip()

        sound_player.join()

        pygame.display.quit()
        pygame.quit()
