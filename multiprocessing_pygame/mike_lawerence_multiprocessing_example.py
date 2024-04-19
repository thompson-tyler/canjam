# as snagged from https://gist.github.com/mike-lawrence demo to understand 
# multiprocessing for our pygame instance


#import used modules
import sys
import time
import multiprocessing # we import Queue and Process

#create a multiprocessing Queue object for sending messages to an input process
queueToInputProcess = multiprocessing.Queue()

#create a multiprocessing Queue object for receiving messages from an input process
queueFromInputProcess = multiprocessing.Queue()

#define a function to run continuously in a seperate process that monitors the pygame event queue for keypress events
def inputProcessLoop(queueToInputProcess,queueFromInputProcess):
	import pygame
	pygame.init()
	print("hello from process 1")
	done = False
	while not done:
		now = time.time()
		pygame.event.pump()
		for event in pygame.event.get() :
			if event.type == pygame.KEYDOWN :
				response = event.unicode
				response_time = now
				queueFromInputProcess.put([response,response_time])
				print('recieved input')
		if not queueToInputProcess.empty():
			from_queue = queueToInputProcess.get()
			if from_queue == 'quit':
				done = True



#define a function to run continuously in a seperate process that monitors the output queue for messages and writes data as necessary
def outputProcessLoop(queueToOutputProcess):
	outfile = open('outfile.txt','w')
	print("hello from process 2! :)")
	done = False
	while not done:
		if not queueToOutputProcess.empty():
			from_queue = queueToOutputProcess.get()
			if from_queue == 'quit':
				outfile.close()
				done = True
			else:
				outfile.write(from_queue+'\n')




if __name__ == "__main__":
    
    
    #initialize pygame
	import pygame
 
	#start up the input detector in a separate process, this is a pygame input detector, but others will work probs
	inputProcess = multiprocessing.Process(target=inputProcessLoop, args=(queueToInputProcess,queueFromInputProcess,))
	inputProcess.start()


    
	#create a multiprocessing Queue object for sending messages to an output process
	queueToOutputProcess = multiprocessing.Queue()
    
    #### PROCESS HANDLING PORTION ######
    
    #start up the output process in a separate process
	outputProcess = multiprocessing.Process(target=outputProcessLoop, args=(queueToOutputProcess,))
	outputProcess.start()
 
	pygame.init()
	
	#initialize a font
	defaultFontName = pygame.font.get_default_font()
	feedbackFont = pygame.font.Font(defaultFontName, 100)

	#start the diaplay loop
	done = False
	updateDisplay = False

	print("hello from the pygame process! :)")
	screen = pygame.display.set_mode((500, 500))

	while not done:
		if not queueFromInputProcess.empty():
			from_queue = queueFromInputProcess.get()
			if from_queue[0]=='\x1b':				# THIS CODE ENDS EVERYTHING NAND CLOSES OUT ALL THE PROCESSES 
				queueToInputProcess.put('quit') # put quit on the queue's to signal done
				queueToOutputProcess.put('quit') # put quit on the queues to signal done 
				inputProcess.join() # signal processes to end computation
				outputProcess.join() #signal processes to end computation
				pygame.quit()	     # quit the pygame 
				sys.exit()			 # exit program after cleaing 
			elif from_queue[0]=='i':  # from queue is input then display the input or do some random shit I don't know 
				screen = pygame.display.set_mode((500, 500))
				screen.fill((0,0,0))
				pygame.display.flip()				
			else:						 # otherwise if it isn't then display the queue at 0 
				toDisplay = from_queue[0]
				updateDisplay = True	# update the display 
		if updateDisplay:
			updateDisplay = False	# set the display update back to false 
			thisRender = feedbackFont.render(toDisplay, True, (255,255,255)) # 	TODO: i don't know what this does
			x = screen.get_width()/2-thisRender.get_width()/2				 #  TODO:I also don't kow what this does 
			y = screen.get_height()/2-thisRender.get_height()/2				
			screen.fill((0,0,0))
			screen.blit(thisRender,(x,y)) # changes the screen
			pygame.display.flip() # re renders the display 
			flipLatency = str(time.time()-from_queue[1]) # TODO: idk what this does 
			queueToOutputProcess.put(flipLatency)		# TODO: idk what this does maybe metrics? 