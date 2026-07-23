import unittest
from engine.systems import SoundSystem


class TestSoundSystem(unittest.TestCase):
    def test_basic_behavior(self):
        cfg = {'enabled': True, 'volume': 0.6}
        ss = SoundSystem(cfg)

        # set_volume clamps and updates internal state
        ss.set_volume(1.5)
        self.assertLessEqual(ss.volume, 1.0)

        ss.set_volume(-1.0)
        self.assertGreaterEqual(ss.volume, 0.0)

        # Playing unknown sounds/tracks should return False
        self.assertFalse(ss.play_sound('nonexistent'))
        self.assertFalse(ss.play_music('no_track'))
        self.assertFalse(ss.play_ambience('no_ambience'))

        # stop functions should handle missing entries gracefully
        self.assertFalse(ss.stop_sound('nope'))
        self.assertFalse(ss.stop_music())


if __name__ == '__main__':
    unittest.main()
