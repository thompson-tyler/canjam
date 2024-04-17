##
# 
#
##

import time
import numpy
import pyaudio
import fluidsynth
import wave 
import music_encodings # translates midi numbers onto notes 

print(music_encodings.note_to_number("E", 0))

# NOTE ENCODING: (channel, key, velocity)

# channel: the synth channel where the note is sent.
# should probably always be 0. OR, we could have one synth with one soundfont per channel. 
# might be easier. 
# key: the literal note. Middle C, for example, is 48. 
# velocity: how hard the note is pressed. Higher = louder. 


DEFAULT_SAMPLE_RATE = 44100
START_CHANNEL = 0 # TODO this will change with initialization from game
DEFAULT_VELOCITY = 100
DEFAULT_SYS_AUDIO_CHANNELS= 2
MAX_SYNTH_CHANNELS = 5

class CanJamSynth:
    def __init__(self, start_channel= START_CHANNEL ) -> None:
        """
        CanJanSynth: creates a synth, with defined presets
        note: If you have fewer than 2 channels on your computer this will need
        to be changed.
        """
        self.SAMPLE_RATE = DEFAULT_SAMPLE_RATE
        self.MAX_CHANNELS = MAX_SYNTH_CHANNELS
        self.pa = pyaudio.PyAudio()
        self.synth = fluidsynth.Synth() 
        # self.sfs = ["sound_fonts/example.sf2", "sound_fonts/Nokia.sf2"] # TODO load this in from a file of soundfonts
        
        self.sfs = ["sound_fonts/CT8MGM.sf2"]
        
        self.stream = self.pa.open(
                        format = pyaudio.paInt16,
                        channels = DEFAULT_SYS_AUDIO_CHANNELS,
                        rate = DEFAULT_SAMPLE_RATE,
                        output = True)
        self.current_channel = start_channel
        self.current_velocity = DEFAULT_VELOCITY
        self.bindings = {"D" : 60} # TODO load this in from a bindings dict
        self.load_all_sfs()

    def __del__(self):
        self.pa.close(self.stream)
        self.pa.terminate()
    
    def load_all_sfs(self):
        for i, sf in enumerate(self.sfs):
            self.load_sf_to_channel(sf, i)

    def load_sf_to_channel(self, soundfont: str, chan: int):
        sfid = self.synth.sfload(soundfont)
        self.synth.program_select(chan, sfid, 0, 0) # TODO idk what this actually does 
    

    def play_from_keystroke(self, keystroke: str):
        note = self.bindings[keystroke]
        self.play_note(note)

    def play_note(self, noteval: int):
        s = []
        self.synth.noteon(self.current_channel, noteval, self.current_velocity)
        s = numpy.append(s, self.synth.get_samples(2000))
        self.synth.noteoff(self.current_channel, noteval)
        s = numpy.append(s, self.synth.get_samples(1))
        audio = fluidsynth.raw_audio_string(s)
        self.stream.write(audio)



def main():
    cjs = CanJamSynth(START_CHANNEL)
    cjs.play_from_keystroke("D")

if __name__ == "__main__":
    main()


                ################## OLD CODE ####################


# def play_from_keystroke(keystroke: str):
#     note = 60
#     play_note(note)

# def play_note(noteval: int):
#     fl.noteon(0, noteval, 30)
#     audio = fluidsynth.raw_audio_string(fl.get_samples(SAMPLE_RATE // 2))
#     strm.write(audio)

# pa = pyaudio.PyAudio()
# strm = pa.open(
#     format = pyaudio.paInt16,
#     channels = 2,
#     rate = SAMPLE_RATE,
#     output = True)

# s = []

# fl = fluidsynth.Synth() # if pyfluidsynth has problem with library 
                        # linking this line will error with "Synth" not found 

# Initial silence is 1 second
# s = numpy.append(s, fl.get_samples(SAMPLE_RATE * 1))

# def load_sf_to_channel(synth: fluidsynth.Synth, soundfont: str, chan: int):
#     sfid = fl.sfload(soundfont)
#     fl.program_select(chan, sfid, 0, 0) # TODO idk what this actually does 

# sfid = fl.sfload("example.sf2") # load in a soundfont, this is like loading an 
                                # instrument for the synth to use 
# fl.program_select(0, sfid, 0, 0)

    # fl.noteon(0, 60, 30) 
    # s = numpy.append(s, fl.get_samples(SAMPLE_RATE // 2))
    # samps = fluidsynth.raw_audio_string(s) 
    # strm.write(samps)
    
    # time.sleep(1)

# fl.noteon(0, 60, 30)  
# fl.noteon(0, 67, 30)
# fl.noteon(0, 76, 30)

# # Chord is held for 2 seconds
# s = numpy.append(s, fl.get_samples(SAMPLE_RATE * 2))

# fl.noteoff(0, 60)
# fl.noteoff(0, 67)
# fl.noteoff(0, 76)

# # Decay of chord is held for 1 second
# s = numpy.append(s, fl.get_samples(SAMPLE_RATE * 1))

# fl.delete()

# # actually plays the samps 
# samps = fluidsynth.raw_audio_string(s) 

# # print(samps[0:999])

# print(f"{len(samps) = }")
# print('Starting playback')
# strm.write(samps)
