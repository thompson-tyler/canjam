# 
# three part multiprocessing program for our pygame
#   The first process 
#

#  NCS stands for the Note color synth
#  message format struct = (note:int, color:(int,int,int), synth:str)


from multiprocessing import Queue as MQ
from multiprocessing import Process
# this Queue will be changed once we have handoff from @skylar and @tyler
from queue import Queue 


def game_outbound_process_handler(outputProgramQueue:MQ, outbound_com_queue:Queue):
    """outbound process, takes NCS messages from the pygame process
        1. plays the outbound noise to the user 
        2. sends NCS to the outbound games 
    
    Args:
        outbound_program_queue (MQ): multiprocessing queue for outbound noises
        outbound_com_queue (Queue): Network queue to distribute outbound messages
    """
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
                outbound_com_queue.put(from_queue)
                print(f"sent {from_queue} to outbound worker")


# TODO THIS IS THE CRUX OF SYNCHRONIZATION ##### def gonna need some thinking 
def game_inbound_process_handler(inboundProcessQueue:MQ, inbound_com_process:Queue):
    """ Takes NCS messages form the inbound_com_process, 
        1. while true plays a noise from the inbound_com_queue
        2. and then sends it to the inboundProcessQueue to update the color
    
    Args:
        inboundProcessQueue (MQ): multiprocessing queue for inbound noises
        inbound_com_process (Queue): Network queue to take inbound messages
    """
    
    done = False
    while not done: 
        if not inbound_com_process.empty()
            # play the noise 

if __name__ == "__main__":
    
    import pygame 
    
    
    queuefromOutputProcess = MQ()
    queueFromInputProcess = MQ()
    
    # for now since we are waiting for handoff we will just be putting things 
    # on these queues and printing them to terminal 
    inboundCommunicationQueue = Queue()
    outboundCommunicationQueue = Queue()
    
    #### Start up the processes #### 
    inputProcess = Process(target=game_inbound_process_handler, args=(queueFromInputProcess,inboundCommunicationQueue))
    outputProcess = Process(target=game_outbound_process_handler, args=(queuefromOutputProcess, outboundCommunicationQueue))
    
    ## start em 
    inputProcess.start()
    outputProcess.start()
    
    pygame.init()
    
    # display loop 
    
    done = False 
    updateDisplay = False
    ## Start U pte Pygame #### 
    while not done:
        """main program loop: 
            updates a grid of colors, based on input of NCS, color objects, 
            and user input to the grid of colors only deals with user input to the 
            grid, doesn't deal with sound uses outbound process to deal with sound
        """
        print("hello")
        # checks to see if the user has touched the grid 
        # if they have but it on queue FromInputProcess
        
    # here we have an event loop that checks if a grid square has been pressed 
    
    # if a square gets clicked we need to update it's color and send it outbound
    
    # after this we check from the inbound queue to see if there are any inbound 
    # noises: if there are we display the colors 