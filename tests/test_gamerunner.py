import unittest

from canjam.message import Synth
from canjam.gamerunner import GameRunner
from canjam.sound_fonts.canjamsynth import CanJamSynth

class GameRunnerTest(unittest.TestCase):

    def test_create_canjamsynth():
        """Confirm that a CanJamSynth can properly initialize its py_audio
        and fluid_synth modules, and play a single note.
        """
        player_synth = CanJamSynth(font=Synth.PIANO)
        d_note = 60
        player_synth.play_note(d_note)