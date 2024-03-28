import time
import numpy
# import pyaudio
import fluidsynth

SAMPLE_RATE = 44100

pa = pyaudio.PyAudio()
strm = pa.open(
    format = pyaudio.paInt16,
    channels = 2,
    rate = SAMPLE_RATE,
    output = True)

s = []

fl = fluidsynth.Synth() # if pyfluidsynth has problem with library 
                        # linking this line will error with "Synth" not found 

# Initial silence is 1 second
# s = numpy.append(s, fl.get_samples(SAMPLE_RATE * 1))

sfid = fl.sfload("example.sf2") # load in a soundfont, this is like loading an 
                                # instrument for the synth to use 
fl.program_select(0, sfid, 0, 0)

fl.noteon(0, 60, 30) 
fl.noteon(0, 67, 30)
fl.noteon(0, 76, 30)

# Chord is held for 2 seconds
s = numpy.append(s, fl.get_samples(SAMPLE_RATE * 2))

fl.noteoff(0, 60)
fl.noteoff(0, 67)
fl.noteoff(0, 76)

# Decay of chord is held for 1 second
s = numpy.append(s, fl.get_samples(SAMPLE_RATE * 1))

fl.delete()

# actually plays the samps 
samps = fluidsynth.raw_audio_string(s) 

# print(samps[0:999])

print(f"{len(samps) = }")
print('Starting playback')
strm.write(samps)
