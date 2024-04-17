import canjam_game.meltysynth as ms
import pyaudio

SAMPLE_RATE = 44100

pa = pyaudio.PyAudio()
strm = pa.open(
    format = pyaudio.paInt16,
    channels = 2,
    rate = SAMPLE_RATE,
    output = True)


# Load the SoundFont.
sound_font = ms.SoundFont.from_file("demo/example.sf2")

# Create the synthesizer.
settings = ms.SynthesizerSettings(SAMPLE_RATE)
synthesizer = ms.Synthesizer(sound_font, settings)

# Play some notes (middle C, E, G).
synthesizer.note_on(0, 60, 100)
synthesizer.note_on(0, 64, 100)
synthesizer.note_on(0, 67, 100)

# The output buffer (3 seconds).
left = ms.create_buffer(3 * settings.sample_rate)
right = ms.create_buffer(3 * settings.sample_rate)

# Render the waveform.
synthesizer.render(left, right)

