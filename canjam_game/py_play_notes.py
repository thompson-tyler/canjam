# recieves notes from a thread/process and plays them but no display 

# since this is python we communicate via a shared threadsafe queue 

from queue import Queue
import random
import threading
from time import sleep 
from canjamsynth import CanJamSynth


taskqueue = Queue()
sim_running = True
# sim_lock = Lock()
# a thread that is a synth with a while loop consumer
def consumer():

    synth = CanJamSynth() 
    while sim_running: 
        (note, duration) = taskqueue.get()
        for duration in range(duration): 
            synth.play_note(note)
        taskqueue.task_done()
        
        
# a thread that generates notes for the consumer to play producer 

def producer(): 
    while sim_running: 
            rand_note = random.randrange(16,120)
            rand_duration = random.randrange(1, 10)
            taskqueue.put((rand_note, rand_duration))
            sleep(.01)
            
def main(): 
    prods = [threading.Thread(target= producer, args=[]) for _ in range(6)]
    con = threading.Thread(target=consumer, daemon=True, args=[])
    
    con.start()
    for prod in prods: 
        prod.start()
    
 
    con.join()
    for prod in prods: 
        prod.join()


if __name__ == "__main__":
    main()
    