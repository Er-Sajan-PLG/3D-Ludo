import unittest
from engine.systems import UISystem, Button, Label, TextInput


class TestUISystem(unittest.TestCase):
    def test_ui_initialization(self):
        cfg = {'enabled': True, 'screen_width': 800, 'screen_height': 600}
        ui = UISystem(cfg)

        # Main menu buttons created
        self.assertIn('new_game', ui.buttons)
        self.assertIn('load_game', ui.buttons)
        self.assertIn('settings', ui.buttons)

        # Labels exist
        self.assertIn('title', ui.labels)

        # Text input operations
        ti = TextInput('t1', (10, 10), (100, 24))
        ti.add_character('a')
        self.assertEqual(ti.text, 'a')
        ti.remove_character()
        self.assertEqual(ti.text, '')


if __name__ == '__main__':
    unittest.main()
