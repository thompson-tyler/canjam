import numpy
import pyaudio
import fluidsynth

from enum import Enum

# NOTE ENCODING: (channel, key, velocity)

# channel: the synth channel where the note is sent.
# should probably always be 0. OR, we could have one synth with one soundfont per channel.
# might be easier.
# key: the literal note. Middle C, for example, is 48.
# velocity: how hard the note is pressed. Higher = louder.

DEFAULT_SAMPLE_RATE = 44100
START_CHANNEL = 0  # TODO this will change with initialization from game
DEFAULT_VELOCITY = 100
DEFAULT_SYS_AUDIO_CHANNELS = 2
MAX_SYNTH_CHANNELS = 5


# fonts again
class SynthType(Enum):
    PIANO = "canjam/sound_fonts/example.sf2"
    MARIO = "canjam/sound_fonts/SuperMarioKart.sf2"
    BELLS = "canjam/sound_fonts/Tubular_Carillon.sf2"
    TRUMPET = "canjam/sound_fonts/battletoads.sf2"


class CanJamSynth:
    def __init__(self, font: SynthType):
        """
        Intialize a CanJamSynth with defined presets.
        note: If you have fewer than 2 channels on your computer this will need
        to be changed.
        """
        self.SAMPLE_RATE = DEFAULT_SAMPLE_RATE
        self.MAX_CHANNELS = MAX_SYNTH_CHANNELS
        self.font = font

        self.py_audio = pyaudio.PyAudio()
        self.stream = self.py_audio.open(
            format=pyaudio.paInt16,
            channels=DEFAULT_SYS_AUDIO_CHANNELS,
            rate=DEFAULT_SAMPLE_RATE,
            output=True,
        )

        self.fluid_synth = fluidsynth.Synth()

        self.curr_channel = START_CHANNEL
        self.curr_velocity = DEFAULT_VELOCITY

        font_path = font.value

        font_id = self.fluid_synth.sfload(font_path)
        # TODO: figure out what program_select does
        self.fluid_synth.program_select(START_CHANNEL, font_id, 0, 0)

    def __del__(self):
        """ """
        self.py_audio.close(self.stream)
        self.py_audio.terminate()

    def play_note(self, note: int):
        """ """
        sound = []
        self.fluid_synth.noteon(self.curr_channel, note, self.curr_velocity)

        # TODO: why use numpy append here?
        sound = numpy.append(sound, self.fluid_synth.get_samples(2000))
        self.fluid_synth.noteoff(self.curr_channel, note)

        sound = numpy.append(sound, self.fluid_synth.get_samples(1))
        audio = fluidsynth.raw_audio_string(sound)
        self.stream.write(audio)
