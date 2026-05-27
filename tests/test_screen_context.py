import unittest

from voice_codex.screen_context import should_capture


class ScreenContextTests(unittest.TestCase):
    def test_detects_visual_prompts(self):
        self.assertTrue(should_capture("Te gusta como queda este fondo de pantalla?"))
        self.assertTrue(should_capture("Que ves en esta ventana?"))

    def test_ignores_non_visual_prompts(self):
        self.assertFalse(should_capture("Actualiza la documentacion del proyecto"))


if __name__ == "__main__":
    unittest.main()
