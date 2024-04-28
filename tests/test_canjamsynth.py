import unittest

from canjam.canjamsynth import CanJamSynth, SynthType


class CanjamSynthTest(unittest.TestCase):

    def test_create_canjamsynth(self):
        """Confirm that a CanJamSynth can properly initialize its py_audio
        and fluid_synth modules, and play a single note.
        """
        player_synth = CanJamSynth(font=SynthType.PIANO)
        d_note = 60
        player_synth.play_note(d_note)
