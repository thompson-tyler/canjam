# 
# three part multiprocessing program for our pygame
#   The first process 
#

#  NCS stands for the Note color synth
#  message format struct = (note:int, color:(int,int,int), synth:str)

import multiprocessing
from multiprocessing import Process
# this Queue will be changed once we have handoff from @skylar and @tyler
from queue import Queue
from time import sleep 
from sound_fonts.canjamsynth import CanJamSynth

GRID_SIZE = 9


def game_outbound_process_handler(outputProgramQueue:multiprocessing.Queue, synth:str):
    """outbound process, takes NCS messages from the pygame process
        1. plays the outbound noise to the user 
        2. sends NCS to the outbound games 
    l
    Args:
        outbound_program_queue (Multiprocessing.Queue): multiprocessing queue for outbound noises
    """
    
    # make the personal synth 
    player_synth = CanJamSynth(font = synth)
    
    
    outbound_com_queue = Queue() # FROM HANDOFF 
    
    
    done = False
    while not done: 
        if not outputProgramQueue.empty(): 
            from_queue = outputProgramQueue.get()
            if from_queue == 'quit': 
                print("signal outbound processer to quit")
                outbound_com_queue.put('quit')
                done = True
            else: 
                # play the outbound noise from the synth
                (row, col) = from_queue.get('note')
                note = get_note_index(row,col)
                player_synth.play_note(note)
                outbound_com_queue.put(from_queue)
                print(f"sent {from_queue} to outbound worker")


# TODO THIS IS THE CRUX OF SYNCHRONIZATION 
##  TODO: Also have to figure out how to kill this since only monitoroing the inboudn communications 
def game_inbound_process_handler(inboundProcessQueue:multiprocessing.Queue):
    """ Takes NCS messages form the inbound_com_process, 
        1. while true plays a noise from the inbound_com_queue
        2. and then sends it to the inboundProcessQueue to update the color
    
    Args:
        inboundProcessQueue (multiprocessing.Queue: multiprocessing queue for inbound noises
    """
    
    inbound_com_process = Queue() # FROM HANDOFF

    
    synth = CanJamSynth(font='drums')
    INBOUND_SYNTH = 'drums'
    my_color = (0, 0 , 0)
    
    curr_ncs = {
        'note': (4,3), 
        'color': my_color,
        'synth': INBOUND_SYNTH
    }

    # for all the games and all the synths make a synth dictionary for each 
    
    # make_neighbor_synths(neighborslist, synthslist) # HANDOFF 
    # for _ in range(1, 20):
    #     inbound_com_process.put(curr_ncs) # demo puts thigns on the outbound 
    #     queue to play 
    
    
    # TODO: get a simulation of multiple requests 
    
    done = False
    while not done: 
        
        if not inbound_com_process.empty(): 
            from_queue = inbound_com_process.get()
            print(f"from queue is {from_queue}\n")
            if from_queue == "quit": 
                print("signal inbound processer to quit")
                done = True
            else:
                print(f"got noise sent from inbound queue {from_queue}")
                # put the color on the inboundProcess queue for the program to 
    
                (row,col) = from_queue.get('note')
                note = get_note_index(row,col)
                synth.play_note(note)
                inboundProcessQueue.put(from_queue)
   
        inbound_com_process.put(curr_ncs)
                # play the noise 
            

# pygame display functions TODO: maybe inline this 
def get_note_index(row:int, col:int) -> int:
    """gets a note from the given index

    Args:
        row (int): row in grid
        col (_type_): col in grid

    Returns:
        note: int 
    """
    return (row * GRID_SIZE + col) + 11

# Function to draw the grid
def draw_grid(colors, game_obj, screen):
    """draws the grid given the array of colors for the grid 
       that is the default unclicked color, the game and the screen 

    Args:
        colors (color array)): array of pixels that represent the grid 
        game_obj (pygame obj): current pygame 
        screen (pygame obj): python screen 
    """
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                col * (GRID_SQUARE_SIZE + GRID_MARGIN),
                row * (GRID_SQUARE_SIZE + GRID_MARGIN),
                GRID_SQUARE_SIZE,
                GRID_SQUARE_SIZE,
            )
            game_obj.draw.rect(screen, colors[row][col], rect)
            
def note_color_on(row:int, col:int, color, grid_colors, screen):
    """displays the color on the index on the grid

    Args:
        row (int): _description_
        col (int): _description_
        grid_colors (_type_): _description_
        screen (_type_): _description_
    """
    grid_colors[row][col] = color 
    draw_grid(grid_colors, game_obj=pygame, screen=screen)
    pygame.display.flip()
    sleep(.09)
    grid_colors[row][col] = GRAY
    

if __name__ == "__main__":
    
    import pygame 
    
    ### GAME CONSTANTS ###
    GRID_SQUARE_SIZE = 50
    GRID_MARGIN = 5
    SCREEN_HEIGHT = (GRID_SQUARE_SIZE + GRID_MARGIN) * GRID_SIZE
    SCREEN_WIDTH  = (GRID_SQUARE_SIZE + GRID_MARGIN) * GRID_SIZE
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GRAY = (200, 200, 200)
    BLACK = (0, 0, 0) # TODO: generate a random color per person for this 
    CURRENT_NOTE = 0 
    
    # HANDOFF PLACE HOLDER  
    PLAYER_COLOR = RED
    PLAYER_SYNTH = "piano"
    
    #CONSTANTS FOR PYGAME PROCESSING
    SWITCH_COUNT = 6 #
        
    
    
    ## MULTIPROCESSING ARGS ##
    queuefromOutputProcess = multiprocessing.Queue()
    queueFromInputProcess = multiprocessing.Queue()
    
    # TODO: change at HANDOFF 
    inboundCommunicationQueue = Queue()
    outboundCommunicationQueue = Queue()
    
    #### Start up the processes #### 
    inputProcess = Process(target=game_inbound_process_handler, args=(queueFromInputProcess,))
    outputProcess = Process(target=game_outbound_process_handler, args=(queuefromOutputProcess,PLAYER_SYNTH))
    
    inputProcess.start()
    outputProcess.start()
    
    pygame.init()
    
    #### SCREEN THINGS ###  
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("CanJam")

    screen.fill(WHITE)
    
    # Initialize grid colors
    grid_colors = [[GRAY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    clicked_squares = set()  # Set to keep track of currently clicked squares

    # GAME LOOP THANGZ 
    done = False 
    updateDisplay = False
    
    queue_check_counter = 0 # HANDOFF 
    
    while not done:
        """main program loop: 
            updates a grid of colors, based on input of NCS, color objects, 
            and user input to the grid of colors only deals with user input to the 
            grid, doesn't deal with sound uses outbound process to deal with sound
        """

        # ALTERNATE CHECK TO SEE IF WE CARE ABOUT LOOP  
        if queue_check_counter > 2: 
            if not queueFromInputProcess.empty(): 
                note_col_loc = queueFromInputProcess.get()
                (row,col,)= note_col_loc.get('note')
                color = note_col_loc.get('color')
                note_color_on(row, col, color = color, grid_colors= grid_colors, screen=screen)
                
            queue_check_counter == -2
        
        queue_check_counter += 1
            
        for event in pygame.event.get(): 
            if event.type == pygame.KEYDOWN :
                response = event.unicode
                if response == '\x1b': 
                    # trigger all the queues to die 
                    queueFromInputProcess.put('quit')
                    queuefromOutputProcess.put('quit')
                    done = True
                    
        if pygame.mouse.get_pressed()[0]: 
            mouse_pos = pygame.mouse.get_pos()
            col = mouse_pos[0] // (GRID_SQUARE_SIZE + GRID_MARGIN)
            row = mouse_pos[1] // (GRID_SQUARE_SIZE + GRID_MARGIN)
            # and send it to the outbound queue 
            curr_ncs = {'note': (row,col), 'color': PLAYER_COLOR, 'synth': PLAYER_SYNTH}
            queuefromOutputProcess.put(curr_ncs)
            note_color_on(row,col, color = PLAYER_COLOR, grid_colors=grid_colors,
                          screen=screen)
      
        draw_grid(grid_colors, game_obj=pygame, screen=screen)
        
        pygame.display.flip()

    
    pygame.quit()
           
    # update the display 
