# Test playing pseudo synchronous notes using multiple CanJam synths on 
# differnt threads 

import unittest
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
            print(f"synth {synthty} playing")
            synth.play_note(note)
            
    
class MultiThreadTestCase(unittest.TestCase):

    def test_multi_thread_synths(self): 
        comm_queue = Queue() # type: ignore

        thread = threading.Thread(target=play_synth_note, args= [50, SynthType.TRUMPET, comm_queue])
        thread2 = threading.Thread(target=play_synth_note, args= [70, SynthType.MARIO, comm_queue])
        thread3 = threading.Thread(target=play_synth_note, args= [60, SynthType.BELLS, comm_queue])
        
        thread.start()
        thread2.start()
        thread3.start()
        

        sleep(10)

        comm_queue.put('quit')
        comm_queue.put('quit')
        comm_queue.put('quit')

        thread.join()
        thread.join()
        thread.join()
