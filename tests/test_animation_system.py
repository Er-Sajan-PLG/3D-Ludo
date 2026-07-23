import unittest
import time
from engine.systems import AnimationSystem, AnimationType


class TestAnimationSystem(unittest.TestCase):
    def test_animation_flow(self):
        cfg = {'enabled': True, 'animation_speed': 1.0}
        anim = AnimationSystem(cfg)

        # create and play an animation
        a = anim.create_animation('a1', AnimationType.MOVEMENT, 1, 0.1)
        self.assertEqual(a.animation_id, 'a1')

        played = anim.play_animation(a)
        self.assertTrue(played)

        # animate piece movement returns an id
        aid = anim.animate_piece_movement(2, (1.0, 2.0, 3.0))
        self.assertIsInstance(aid, str)

        # update should run without error
        anim.update(0.05)

        # add screen shake and flash
        anim.add_screen_shake(0.5, 0.2)
        anim.add_flash_effect((1, 0, 0, 1), 0.1)

        # cleanup should clear lists
        anim.cleanup()
        self.assertEqual(len(anim.active_animations), 0)


if __name__ == '__main__':
    unittest.main()
