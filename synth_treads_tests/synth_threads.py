# 

from queue import Queue
import threading
from time import sleep
from canjam.canjamsynth import CanJamSynth
from canjam.message import SynthType


def play_synth_note(note:int, synthty:SynthType, comm_queue:Queue[str]):
    
    synth = CanJamSynth(font=synthty)
    
    running = True
    while running: 
        if comm_queue.empty(): 
            synth.play_note(note)
    
    
def main(): 
    comm_queue = Queue() # type: ignore
    
    thread = threading.Thread(target=play_synth_note, args= [8, SynthType.BELLS, comm_queue])
    thread2 = threading.Thread(target=play_synth_note, args= [8, SynthType.MARIO, comm_queue])
    
    thread.start()
    thread2.start()
    
    while input() != 'q': 
        print("waiting")

    comm_queue.put('quit')
    comm_queue.put('quit')
    
    thread.join()
    thread.join()
    
if __name__ == "__main__":
    main()