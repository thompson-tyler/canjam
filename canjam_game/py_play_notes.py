# recieves notes from a thread/process and plays them but no display 

# since this is python we communicate via a shared threadsafe queue 

from queue import Queue
import random
import threading
from time import sleep 
from canjamsynth import CanJamSynth

# GLOBAL VARIABLES 
font_1 = ['Nokia.sf2']
font_2 = ['CT8MGM.sf2']
taskqueue = Queue()
sim_running = True

# a thread that is a synth with a while loop consumer
def consumer(synth_font:list[str]):
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
            
def multi_players_1_synth(): 
    prods = [threading.Thread(target= producer, args=[]) for _ in range(6)]
    con = threading.Thread(target=consumer, daemon=True, args=[font_1])
    
    con.start()
    for prod in prods: 
        prod.start()
    
 
    con.join()
    for prod in prods: 
        prod.join()
        
def main(): 
    sfs = ["sound_fonts/Nokia.sf2", "sound_fonts/NES_Drums___SFX.sf2"]
    cons = [threading.Thread(target= consumer, args=[sf]) for sf in sfs]
    prod = threading.Thread(target = producer, args=[])

    prod.start()
    for con in cons: 
        con.start()
        
    for con in cons: 
        con.join()
    prod.join()
    

if __name__ == "__main__":
    main()
    